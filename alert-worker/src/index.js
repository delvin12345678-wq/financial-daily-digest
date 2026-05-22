// MarketDaily — Premium 即時 LINE 重大新聞提醒 alert-worker
// 每 2 分鐘:抓新聞 → 去重 → 規則粗篩 → 比對 Premium 持股 → AI 嚴重度 → LINE 推播。
// 設計規格:specs/2026-05-22-premium-realtime-line-alerts-design.md

import { fetchNews } from "./news_source.js";
import { displayName } from "./stock_names.js";

const SEVERITY_THRESHOLD = 7;
const DAILY_CAP = 5;
const MAX_AGE_HOURS = 24;     // 超過此時數的新聞視為舊聞,不評分、不推(即時提醒只推新鮮事)
const PRESCORE_FLOOR = 40;    // 規則預評分低於此值直接跳過 AI;調高=更省 AI,調低=更不漏新聞
const CLUSTER_WINDOW_MS = 6 * 3600 * 1000;
const LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push";
const SEEN_TTL = 48 * 3600;
const PUSHED_TTL = 48 * 3600;
const COUNT_TTL = 26 * 3600;

// 規則粗篩:重大事件關鍵字分組,命中才往下走。type 也用於 story cluster 去重。
const EVENT_RULES = [
  { type: "earnings", kw: ["earnings", "beats estimates", "misses estimates", "quarterly results", "profit jump", "profit drop"] },
  { type: "guidance", kw: ["guidance", "outlook", "forecast", "profit warning", "cuts target", "lowers", "slashes"] },
  { type: "mna", kw: ["acquire", "acquisition", "merger", "buyout", "takeover", "to buy ", "agrees to buy"] },
  { type: "regulatory", kw: ["fda", "approval", "recall", "antitrust", "investigation", "probe", "subpoena", "regulator", "fines"] },
  { type: "legal", kw: ["lawsuit", "sues", "sued", "settlement", "verdict", "court ruling"] },
  { type: "trading", kw: ["halt", "halted", "suspended", "plunge", "soar", "surge", "tumble", "crash", "spike", "sell-off"] },
  { type: "distress", kw: ["bankruptcy", "chapter 11", "insolvency", "default", "delist"] },
  { type: "rating", kw: ["downgrade", "upgrade", "price target", "initiated coverage", "cut to"] },
  { type: "leadership", kw: ["ceo", "chief executive", "resign", "steps down", "ousted", "appoints", "fired"] },
  { type: "incident", kw: ["data breach", "hacked", "outage", "strike", "production halt"] },
];

// 各事件類型的平均重大度權重 —— 規則預評分用,只擋明顯偏弱的,真正嚴重度仍交給 AI 判。
const EVENT_WEIGHT = {
  distress: 95, mna: 88, guidance: 82, regulatory: 76, earnings: 72,
  incident: 66, legal: 62, leadership: 56, rating: 48, trading: 46,
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

// 台灣日期(UTC+8),用於每日推播上限的 key。
function twDate(d = new Date()) {
  return new Date(d.getTime() + 8 * 3600 * 1000).toISOString().slice(0, 10);
}

// 詞界比對,避免 "issues" 命中 "sues"、"followers" 命中 "lowers" 之類的子字串誤判。
const EVENT_MATCHERS = EVENT_RULES.map((r) => ({
  type: r.type,
  re: new RegExp("\\b(?:" + r.kw.map((k) => k.trim()).join("|") + ")", "i"),
}));

function classify(text) {
  const t = text || "";
  for (const m of EVENT_MATCHERS) {
    if (m.re.test(t)) return m.type;
  }
  return null;
}

function clusterKey(ticker, eventType, publishedAt) {
  let ms = Date.parse(publishedAt);
  if (isNaN(ms)) ms = Date.now();
  return `${ticker}:${eventType}:${Math.floor(ms / CLUSTER_WINDOW_MS)}`;
}

// 新聞距今幾小時(無法解析時間 → 0,當作新的)。
function newsAgeHours(publishedAt) {
  const ms = Date.parse(publishedAt);
  if (isNaN(ms)) return 0;
  return (Date.now() - ms) / 3600000;
}

// 規則預評分(0-100,不花 AI):事件權重 × 時效新鮮度。
// 6 小時內滿分,之後線性衰減,到 MAX_AGE_HOURS 時為 0.6 倍。
function ruleScore(eventType, ageHours) {
  const base = EVENT_WEIGHT[eventType] || 50;
  const decay = Math.min(1, Math.max(0, ageHours - 6) / (MAX_AGE_HOURS - 6));
  return Math.round(base * (1 - 0.4 * decay));
}

// 列出所有已綁定 LINE 且 plan=premium 的用戶與其持股。
async function premiumRecipients(env) {
  const recipients = [];
  let cursor;
  do {
    const page = await env.USER_PREFS.list({ prefix: "line:", cursor });
    for (const k of page.keys) {
      const email = k.name.slice(5);
      const plan = await env.USER_PREFS.get(`plan:${email}`);
      if (plan !== "premium") continue;
      const userId = await env.USER_PREFS.get(k.name);
      if (!userId) continue;
      let holdings = new Set();
      const raw = await env.USER_PREFS.get(email);
      if (raw) {
        try {
          const p = JSON.parse(raw);
          for (const s of [...(p.us_stocks || []), ...(p.tw_stocks || [])]) {
            holdings.add(String(s).trim().toUpperCase());
          }
        } catch {}
      }
      recipients.push({ email, userId, holdings });
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return recipients;
}

// Claude 嚴重度判定:輸入新聞 + 相關 ticker,輸出 {severity 0-10, reason}。
async function aiSeverity(env, news, tickers) {
  if (!env.ANTHROPIC_API_KEY) return { severity: null, reason: "AI 未設定", skipped: true };
  const names = tickers.map((t) => `${t}(${displayName(t)})`).join("、");
  const prompt = `你是財經新聞嚴重度評分員。判斷這則新聞對「持有 ${names} 的投資人」有多重大。

標題:${news.title}
摘要:${news.summary || "(無)"}
來源:${news.source}

評分標準(severity 0-10):
- 9-10:破產、重大併購、財測大幅下修、CEO 突然去職、重大訴訟敗訴等,股價可能立即大幅變動。
- 7-8:財報明顯優於/低於預期、重要評等調整、監管調查、產品重大事件。
- 4-6:一般財經報導、分析師例行評論、影響有限。
- 0-3:無實質影響、舊聞、與該公司關聯薄弱。

只輸出 JSON,格式:{"severity": <0-10 整數>, "reason": "<一句繁體中文,說明為何重大>"}`;
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 256,
        messages: [{ role: "user", content: prompt }],
      }),
    });
    if (!res.ok) return { severity: null, reason: `AI 錯誤 ${res.status}`, error: true };
    const data = await res.json();
    const text = (data.content || []).map((c) => c.text || "").join("");
    const m = text.match(/\{[\s\S]*\}/);
    if (!m) return { severity: null, reason: "AI 回應無法解析", error: true };
    const parsed = JSON.parse(m[0]);
    let sev = Math.round(Number(parsed.severity));
    if (isNaN(sev)) sev = 0;
    return { severity: Math.max(0, Math.min(10, sev)), reason: String(parsed.reason || "").slice(0, 200) };
  } catch (e) {
    return { severity: null, reason: `AI 例外:${e.message}`, error: true };
  }
}

// 取 LINE Messaging API 推播 token:優先用長期 token,否則用 channel id+secret 動態換並快取。
async function lineToken(env) {
  if (env.LINE_CHANNEL_ACCESS_TOKEN) return env.LINE_CHANNEL_ACCESS_TOKEN;
  const cached = await env.USER_PREFS.get("alert:linetoken");
  if (cached) return cached;
  if (!env.LINE_CHANNEL_ID || !env.LINE_CHANNEL_SECRET) return null;
  const res = await fetch("https://api.line.me/v2/oauth/accessToken", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: env.LINE_CHANNEL_ID,
      client_secret: env.LINE_CHANNEL_SECRET,
    }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  if (!data.access_token) return null;
  await env.USER_PREFS.put("alert:linetoken", data.access_token, { expirationTtl: 24 * 24 * 3600 });
  return data.access_token;
}

function alertMessage(news, ticker, severity, reason) {
  const head = severity >= 9 ? "🚨 重大消息｜⚠️ 高度重大" : "🚨 重大消息";
  const name = displayName(ticker);
  return [
    `${head}｜你的持股 ${name}`,
    "",
    news.title,
    "",
    "💡 為什麼跟你有關",
    reason || `這則新聞與你持有的 ${name} 相關,留意股價反應。`,
    "",
    `🔗 原文:${news.url}`,
    "—— MarketDaily 即時提醒｜僅供參考,非投資建議",
  ].join("\n");
}

async function linePush(token, userId, text) {
  const res = await fetch(LINE_PUSH_URL, {
    method: "POST",
    headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
    body: JSON.stringify({ to: userId, messages: [{ type: "text", text }] }),
  });
  if (res.ok) return { ok: true };
  return { ok: false, status: res.status, body: (await res.text()).slice(0, 300) };
}

// 完整偵測→推播管線。
//   push    —— true 才真的呼叫 LINE 推播。
//   persist —— true 才寫入 KV(seen / 推播計數 / 狀態紀錄)。
// scheduled() 一律 persist:true(每則新聞只評估一次,避免 AI 成本爆炸);
// /dry-run 端點 persist:false(純檢視,每次重新評估)。
async function runPipeline(env, { push, persist }) {
  const report = {
    ts: new Date().toISOString(),
    push, persist,
    counts: { fetched: 0, alreadySeen: 0, rulePassed: 0, preFiltered: 0, premiumMatched: 0, aiEvaluated: 0, wouldPush: 0, pushed: 0 },
    premiumUniverse: [],
    candidates: [],
    fired: [],
    errors: [],
  };

  const recipients = await premiumRecipients(env);
  const universe = [...new Set(recipients.flatMap((r) => [...r.holdings]))];
  report.premiumUniverse = universe;

  // 有 Premium 持股 → 用個股 RSS 精準抓;沒有 → 抓大盤綜合 feed(供觀察粗篩用)。
  const usUniverse = universe.filter((t) => /^[A-Z.\-]{1,6}$/.test(t));
  const { items, errors } = await fetchNews(usUniverse.length ? { tickers: usUniverse } : {});
  report.errors.push(...errors);
  report.counts.fetched = items.length;

  for (const news of items) {
    const seenKey = `seen:${news.id}`;
    if (await env.USER_PREFS.get(seenKey)) {
      report.counts.alreadySeen++;
      continue;
    }

    const eventType = classify(`${news.title} ${news.summary}`);
    if (!eventType) {
      if (persist) await env.USER_PREFS.put(seenKey, report.ts, { expirationTtl: SEEN_TTL });
      continue;
    }
    report.counts.rulePassed++;

    // 規則預評分閘門 —— 不花 AI:擋掉舊聞與明顯偏弱的新聞,壓低 AI 呼叫量。
    const ageHours = newsAgeHours(news.publishedAt);
    const preScore = ruleScore(eventType, ageHours);
    if (ageHours > MAX_AGE_HOURS || preScore < PRESCORE_FLOOR) {
      if (persist) await env.USER_PREFS.put(seenKey, report.ts, { expirationTtl: SEEN_TTL });
      report.counts.preFiltered++;
      report.candidates.push({
        title: news.title, source: news.source, url: news.url,
        tickers: news.tickers, eventType, preScore, severity: null,
        reason: ageHours > MAX_AGE_HOURS
          ? `規則預篩:新聞已 ${Math.round(ageHours)} 小時,過舊`
          : `規則預篩:預評分 ${preScore} 未達 ${PRESCORE_FLOOR}`,
        recipients: [],
      });
      continue;
    }

    // 比對 Premium 持有者
    const holders = recipients.filter((r) => news.tickers.some((t) => r.holdings.has(t)));
    if (!holders.length) {
      if (persist) await env.USER_PREFS.put(seenKey, report.ts, { expirationTtl: SEEN_TTL });
      report.candidates.push({
        title: news.title, source: news.source, url: news.url,
        tickers: news.tickers, eventType, preScore, severity: null,
        reason: "通過粗篩但無 Premium 持有者", recipients: [],
      });
      continue;
    }
    report.counts.premiumMatched++;

    // AI 嚴重度
    const { severity, reason, skipped, error } = await aiSeverity(env, news, news.tickers);
    if (!skipped) report.counts.aiEvaluated++;
    const cand = {
      title: news.title, source: news.source, url: news.url,
      tickers: news.tickers, eventType, preScore, severity, reason,
      recipients: [],
    };

    if (error) {
      // AI 失敗:不標 seen,下一輪重試。
      report.errors.push(`ai:${news.id}:${reason}`);
      report.candidates.push(cand);
      continue;
    }
    if (skipped) {
      // 沒有 AI key:列出候選但不判定、不標 seen(待補 key 後重評)。
      report.candidates.push(cand);
      continue;
    }
    if (severity < SEVERITY_THRESHOLD) {
      if (persist) await env.USER_PREFS.put(seenKey, report.ts, { expirationTtl: SEEN_TTL });
      report.candidates.push(cand);
      continue;
    }

    // 通過門檻 → 逐持有者推播(去重 + 每日上限)
    const today = twDate();
    const token = push ? await lineToken(env) : null;
    if (push && !token) {
      report.errors.push("line:無推播 token");
      report.candidates.push(cand);
      continue;
    }
    for (const h of holders) {
      const hit = news.tickers.find((t) => h.holdings.has(t));
      const cluster = `pushed:${h.email}:${clusterKey(hit, eventType, news.publishedAt)}`;
      if (await env.USER_PREFS.get(cluster)) {
        cand.recipients.push({ email: h.email, status: "skip:已收過此事件" });
        continue;
      }
      const countKey = `alertcount:${h.email}:${today}`;
      const count = parseInt((await env.USER_PREFS.get(countKey)) || "0", 10);
      if (count >= DAILY_CAP) {
        cand.recipients.push({ email: h.email, status: "skip:已達每日上限" });
        continue;
      }
      report.counts.wouldPush++;
      if (!push) {
        cand.recipients.push({ email: h.email, ticker: hit, status: "would-push" });
        continue;
      }
      const msg = alertMessage(news, hit, severity, reason);
      const pushed = await linePush(token, h.userId, msg);
      if (pushed.ok) {
        await env.USER_PREFS.put(cluster, report.ts, { expirationTtl: PUSHED_TTL });
        await env.USER_PREFS.put(countKey, String(count + 1), { expirationTtl: COUNT_TTL });
        report.counts.pushed++;
        cand.recipients.push({ email: h.email, ticker: hit, status: "pushed" });
      } else if (pushed.status === 400 || pushed.status === 403) {
        // userId 失效 / 未加好友 → 標記 stale,提示重新綁定。
        await env.USER_PREFS.put(`linestale:${h.email}`, report.ts);
        cand.recipients.push({ email: h.email, status: `fail:${pushed.status} 已標記重新綁定` });
        report.errors.push(`push:${h.email}:${pushed.status}`);
      } else {
        cand.recipients.push({ email: h.email, status: `fail:${pushed.status}` });
        report.errors.push(`push:${h.email}:${pushed.status}`);
      }
    }

    report.candidates.push(cand);
    report.fired.push({
      ts: report.ts, title: news.title, url: news.url, source: news.source,
      severity, reason, tickers: news.tickers, eventType, recipients: cand.recipients,
    });
    // 全部持有者處理完才標 seen(推播失敗的會在 errors,但 seen 仍標,避免重複轟炸;
    // 失敗者個別重綁後由新事件觸發)。
    if (persist) await env.USER_PREFS.put(seenKey, report.ts, { expirationTtl: SEEN_TTL });
  }

  if (persist) {
    await env.USER_PREFS.put("alert:laststatus", JSON.stringify({
      ts: report.ts, push, counts: report.counts, errors: report.errors.slice(0, 10),
    }));
    if (report.fired.length) {
      let recent = [];
      try { recent = JSON.parse((await env.USER_PREFS.get("alert:recent")) || "[]"); } catch {}
      await env.USER_PREFS.put("alert:recent", JSON.stringify([...report.fired, ...recent].slice(0, 40)));
    }
  }
  return report;
}

export default {
  async scheduled(event, env, ctx) {
    const enabled = (await env.USER_PREFS.get("alert:enabled")) === "true";
    // 不論 dry/live 都 persist:每則新聞只評估一次,控 AI 成本。
    ctx.waitUntil(runPipeline(env, { push: enabled, persist: true }));
  },

  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/check") {
      let kvOk = true;
      try { await env.USER_PREFS.get("alert:enabled"); } catch { kvOk = false; }
      const lastRaw = await env.USER_PREFS.get("alert:laststatus");
      return json({
        ok: true,
        ts: new Date().toISOString(),
        mode: (await env.USER_PREFS.get("alert:enabled")) === "true" ? "live" : "dry",
        kv: kvOk,
        secrets: {
          ANTHROPIC_API_KEY: !!env.ANTHROPIC_API_KEY,
          LINE_CHANNEL_ACCESS_TOKEN: !!env.LINE_CHANNEL_ACCESS_TOKEN,
          LINE_CHANNEL_ID: !!env.LINE_CHANNEL_ID,
          LINE_CHANNEL_SECRET: !!env.LINE_CHANNEL_SECRET,
        },
        config: {
          severityThreshold: SEVERITY_THRESHOLD, dailyCap: DAILY_CAP,
          maxAgeHours: MAX_AGE_HOURS, preScoreFloor: PRESCORE_FLOOR, cron: "*/2 * * * *",
        },
        lastRun: lastRaw ? JSON.parse(lastRaw) : null,
      });
    }

    if (url.pathname === "/dry-run") {
      try {
        return json(await runPipeline(env, { push: false, persist: false }));
      } catch (e) {
        return json({ ok: false, error: e.message, stack: e.stack }, 500);
      }
    }

    // 近期達標(severity≥7)的提醒紀錄 —— dry-run 觀察期用來看「會推什麼」。
    if (url.pathname === "/recent") {
      const raw = await env.USER_PREFS.get("alert:recent");
      return json({ recent: raw ? JSON.parse(raw) : [] });
    }

    return new Response("MarketDaily alert-worker — /check /dry-run /recent", {
      status: 200,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
