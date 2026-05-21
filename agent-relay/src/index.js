// MarketDaily Agent Team — 寫入代理 Worker
//
// 雲端 CCR 環境封鎖 git push(CCR_TEST_GITPROXY),雲端 Worker 無法把結果寫回 GitHub。
// 改 POST 到這個 Worker:由它用 GitHub API 代為 commit,並用 Brevo 寄通知信。
//
// POST /  (header: X-Relay-Secret)
//   body: { message, files: [{path,content}|{path,delete:true}], email?: {subject,html} }
// GET  /  健康檢查

const REPO = "marketdaily/financial-daily-digest";
const BRANCH = "main";
const GH = "https://api.github.com";
const BREVO = "https://api.brevo.com/v3/smtp/email";

export default {
  async fetch(request, env) {
    if (request.method === "GET") {
      return json({ ok: true, service: "marketdaily-agent-relay" });
    }
    if (request.method !== "POST") {
      return json({ error: "POST only" }, 405);
    }
    if ((request.headers.get("X-Relay-Secret") || "") !== env.RELAY_SECRET) {
      return json({ error: "unauthorized" }, 401);
    }
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid json" }, 400);
    }

    const out = { ok: true };
    const files = body.files;
    if (Array.isArray(files) && files.length) {
      if (!body.message) return json({ error: "message required with files" }, 400);
      try {
        out.commit = await commitFiles(env, body.message, files);
      } catch (e) {
        return json({ error: String(e.message || e) }, 502);
      }
    }
    if (body.email && body.email.subject && body.email.html) {
      try {
        out.emailed = await sendEmail(env, body.email);
      } catch (e) {
        out.emailed = false;
        out.emailError = String(e.message || e);
      }
    }
    return json(out);
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}

async function gh(env, path, method = "GET", payload) {
  const r = await fetch(GH + path, {
    method,
    headers: {
      "Authorization": "Bearer " + env.GITHUB_TOKEN,
      "Accept": "application/vnd.github+json",
      "User-Agent": "marketdaily-agent-relay",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(payload ? { "content-type": "application/json" } : {}),
    },
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const text = await r.text();
  if (!r.ok) {
    const err = new Error(`GitHub ${method} ${path} -> ${r.status}: ${text}`);
    err.status = r.status;
    throw err;
  }
  return text ? JSON.parse(text) : {};
}

// 把一組檔案變更做成一個 atomic commit。main 被推進(非 fast-forward)時重試。
async function commitFiles(env, message, files) {
  let lastErr;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const ref = await gh(env, `/repos/${REPO}/git/ref/heads/${BRANCH}`);
      const baseSha = ref.object.sha;
      const baseCommit = await gh(env, `/repos/${REPO}/git/commits/${baseSha}`);
      const tree = [];
      for (const f of files) {
        if (f.delete) {
          tree.push({ path: f.path, mode: "100644", type: "blob", sha: null });
        } else {
          const blob = await gh(env, `/repos/${REPO}/git/blobs`, "POST", {
            content: f.content,
            encoding: "utf-8",
          });
          tree.push({ path: f.path, mode: "100644", type: "blob", sha: blob.sha });
        }
      }
      const newTree = await gh(env, `/repos/${REPO}/git/trees`, "POST", {
        base_tree: baseCommit.tree.sha,
        tree,
      });
      const commit = await gh(env, `/repos/${REPO}/git/commits`, "POST", {
        message,
        tree: newTree.sha,
        parents: [baseSha],
      });
      await gh(env, `/repos/${REPO}/git/refs/heads/${BRANCH}`, "PATCH", {
        sha: commit.sha,
        force: false,
      });
      return commit.sha;
    } catch (e) {
      lastErr = e;
      if (e.status === 422) continue; // 非 fast-forward,重抓 base 重試
      throw e;
    }
  }
  throw lastErr;
}

async function sendEmail(env, email) {
  const r = await fetch(BREVO, {
    method: "POST",
    headers: {
      "api-key": env.BREVO_API_KEY,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      sender: { name: "MarketDaily Agent Team", email: env.SENDER_EMAIL },
      to: [{ email: env.OWNER_EMAIL }],
      subject: email.subject,
      htmlContent: email.html,
    }),
  });
  if (!r.ok) throw new Error(`Brevo ${r.status}: ${await r.text()}`);
  return true;
}
