// MarketDaily 社群每日發文雲端排程觸發器
//
// Cloudflare Cron Trigger 每天 06:00 UTC(台灣 14:00)觸發,呼叫 GitHub API
// 派發 social_post.yml workflow,由 GitHub Actions 跑 marketing/daily_run.py 發下一篇貼文。
// 取代本機 launchd com.marketdaily.socialpost(Mac 睡眠 missed firing 導致時間亂掉)。
//
// Secret:GITHUB_TOKEN — fine-grained PAT,對本 repo 有 Actions: Read and write。

const REPO = "marketdaily/financial-daily-digest";
const WORKFLOW = "social_post.yml";
const BRANCH = "main";

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(dispatch(env));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/check") {
      if (!env.GITHUB_TOKEN) {
        return json({ token_present: false, token_ok: false, hint: "Worker 還沒設 GITHUB_TOKEN secret" });
      }
      const r = await fetch(
        `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}`,
        {
          headers: {
            "Authorization": "Bearer " + env.GITHUB_TOKEN,
            "Accept": "application/vnd.github+json",
            "User-Agent": "marketdaily-social-post-cron",
          },
        }
      );
      let detail = null;
      try { const d = await r.json(); detail = d.state || d.message; } catch {}
      return json({
        token_present: true,
        github_status: r.status,
        token_ok: r.ok,
        workflow: detail,
      });
    }
    if (url.pathname === "/trigger") {
      // 手動觸發(便於補發);需帶 ?token=<INTERNAL_TOKEN>
      if (!env.INTERNAL_TOKEN || url.searchParams.get("token") !== env.INTERNAL_TOKEN) {
        return json({ ok: false, error: "unauthorized" }, 401);
      }
      await dispatch(env);
      return json({ ok: true, dispatched: WORKFLOW });
    }
    return json({ ok: true, service: "marketdaily-social-post-cron", cron: "0 6 * * * (UTC) = 14:00 TW" });
  },
};

async function dispatch(env) {
  let result;
  try {
    const r = await fetch(
      `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`,
      {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + env.GITHUB_TOKEN,
          "Accept": "application/vnd.github+json",
          "User-Agent": "marketdaily-social-post-cron",
          "X-GitHub-Api-Version": "2022-11-28",
          "content-type": "application/json",
        },
        body: JSON.stringify({ ref: BRANCH, inputs: { mode: "post" } }),
      }
    );
    const text = await r.text();
    result = { ok: r.ok, status: r.status, error: r.ok ? null : text };
  } catch (e) {
    result = { ok: false, status: 0, error: String(e.message || e) };
  }
  console.log("social-post dispatch:", JSON.stringify({ ...result, at: new Date().toISOString() }));
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}
