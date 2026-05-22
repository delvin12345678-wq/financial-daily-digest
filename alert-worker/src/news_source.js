// 標準化新聞來源模組 —— 介面固定:fetchNews() → [{id,title,summary,url,source,publishedAt,tickers[]}]
// 初期實作為免費 RSS。日後可整支抽換為付費 API,不動 index.js。

import { extractTickers } from "./stock_names.js";

// 大盤綜合 feed —— 僅在無 Premium 持股(dry-run 觀察)時使用;
// 有持股時改走 fetchNews({tickers}) 的 Yahoo 個股 RSS。
const GENERAL_FEEDS = [
  { url: "https://feeds.content.dowjones.io/public/rss/mw_topstories", source: "MarketWatch" },
  { url: "https://www.cnbc.com/id/100003114/device/rss/rss.html", source: "CNBC" },
];

function djb2(str) {
  let h = 5381;
  for (let i = 0; i < str.length; i++) h = ((h << 5) + h + str.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}

function decode(s) {
  return (s || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#0?39;/g, "'").replace(/&apos;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(+n))
    .replace(/\s+/g, " ")
    .trim();
}

function tag(block, name) {
  const m = block.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)</${name}>`, "i"));
  return m ? decode(m[1]) : "";
}

function parseFeed(xml, source) {
  const items = [];
  const blocks = xml.match(/<(item|entry)[\s>][\s\S]*?<\/(item|entry)>/gi) || [];
  for (const block of blocks) {
    const title = tag(block, "title");
    let link = tag(block, "link");
    if (!link) {
      const m = block.match(/<link[^>]*href="([^"]+)"/i);
      if (m) link = m[1];
    }
    const summary = tag(block, "description") || tag(block, "summary") || tag(block, "content");
    const published = tag(block, "pubDate") || tag(block, "published") || tag(block, "updated");
    if (!title || !link) continue;
    items.push({
      id: djb2(link),
      title,
      summary,
      url: link,
      source,
      publishedAt: published || new Date().toISOString(),
      tickers: [],
    });
  }
  return items;
}

async function fetchFeed(feed) {
  try {
    const res = await fetch(feed.url, {
      headers: { "User-Agent": "MarketDaily-AlertWorker/1.0 (+https://marketdaily.ai)" },
      cf: { cacheTtl: 0 },
    });
    if (!res.ok) return { items: [], error: `${feed.source}:${res.status}` };
    return { items: parseFeed(await res.text(), feed.source), error: null };
  } catch (e) {
    return { items: [], error: `${feed.source}:${e.message || "fetch failed"}` };
  }
}

function dedupe(items) {
  const byId = new Map();
  for (const it of items) {
    const ex = byId.get(it.id);
    if (ex) {
      ex.tickers = [...new Set([...ex.tickers, ...it.tickers])];
    } else {
      byId.set(it.id, it);
    }
  }
  return [...byId.values()];
}

// tickers 提供時:用 Yahoo 個股 RSS(已預先標好 ticker、可靠);否則抓大盤綜合 feed + 文字比對。
export async function fetchNews({ tickers } = {}) {
  const errors = [];
  if (Array.isArray(tickers) && tickers.length) {
    const feeds = tickers.map((t) => ({
      url: `https://feeds.finance.yahoo.com/rss/2.0/headline?s=${encodeURIComponent(t)}&region=US&lang=en-US`,
      source: "Yahoo Finance",
      ticker: t,
    }));
    const results = await Promise.all(feeds.map(async (f) => {
      const r = await fetchFeed(f);
      if (r.error) errors.push(r.error);
      for (const it of r.items) it.tickers = [f.ticker];
      return r.items;
    }));
    return { items: dedupe(results.flat()), errors };
  }
  const results = await Promise.all(GENERAL_FEEDS.map(fetchFeed));
  const items = [];
  for (const r of results) {
    if (r.error) errors.push(r.error);
    for (const it of r.items) {
      it.tickers = extractTickers(`${it.title} ${it.summary}`);
      items.push(it);
    }
  }
  return { items: dedupe(items), errors };
}
