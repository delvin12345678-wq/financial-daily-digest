// MarketDaily 日報雲端排程觸發器
//
// Cloudflare Cron Trigger 每天 22:55 UTC(台灣 06:55)觸發,呼叫 GitHub API
// 派發 daily_digest.yml workflow,由 GitHub Actions 跑 main.py 寄送日報。
// 全程在雲端,不依賴本機 Mac。觸發結果見 Cloudflare 的 Worker log(wrangler tail)。
//
// Secret:GITHUB_TOKEN — fine-grained PAT,對本 repo 有 Actions: Read and write。

const REPO = "marketdaily/financial-daily-digest";
const WORKFLOW = "daily_digest.yml";
const BRANCH = "main";

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(dispatch(env));
  },

  async fetch(request, env) {
    return json({ ok: true, service: "marketdaily-digest-cron", cron: "55 22 * * * (UTC)" });
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
          "User-Agent": "marketdaily-digest-cron",
          "X-GitHub-Api-Version": "2022-11-28",
          "content-type": "application/json",
        },
        body: JSON.stringify({ ref: BRANCH }),
      }
    );
    const text = await r.text();
    result = { ok: r.ok, status: r.status, error: r.ok ? null : text };
  } catch (e) {
    result = { ok: false, status: 0, error: String(e.message || e) };
  }
  console.log("digest dispatch:", JSON.stringify({ ...result, at: new Date().toISOString() }));
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}
