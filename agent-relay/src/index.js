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

// UTF-8 字串轉 base64(Contents API 要求 base64 內容)。
function b64(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

// 路徑逐段 URL-encode(斜線保留)。
function encPath(p) {
  return p.split("/").map(encodeURIComponent).join("/");
}

// 取現有檔案的 blob SHA;不存在回 null。
async function fileSha(env, path) {
  try {
    const cur = await gh(env, `/repos/${REPO}/contents/${encPath(path)}?ref=${BRANCH}`);
    return cur.sha;
  } catch (e) {
    if (e.status === 404) return null;
    throw e;
  }
}

// 用 Contents API 逐檔 commit(fine-grained token 對 Git Data API 會 403)。
// SHA 過期(409,main 被推進)時重抓重試。
async function commitFiles(env, message, files) {
  let last = null;
  for (const f of files) {
    const url = `/repos/${REPO}/contents/${encPath(f.path)}`;
    for (let attempt = 0; attempt < 3; attempt++) {
      const sha = await fileSha(env, f.path);
      try {
        if (f.delete) {
          if (!sha) break; // 已不存在,免刪
          const r = await gh(env, url, "DELETE", { message, sha, branch: BRANCH });
          last = (r.commit && r.commit.sha) || last;
        } else {
          const body = { message, content: b64(f.content), branch: BRANCH };
          if (sha) body.sha = sha;
          const r = await gh(env, url, "PUT", body);
          last = (r.commit && r.commit.sha) || last;
        }
        break;
      } catch (e) {
        if (e.status === 409 && attempt < 2) continue; // SHA 過期,重抓重試
        throw e;
      }
    }
  }
  return last;
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
