import requests
from config import GROQ_API_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _format_market_data(data: dict) -> str:
    lines = []
    us = data.get("us_market", {})
    tw = data.get("tw_market", {})

    index_names = {
        "^GSPC": "S&P500", "^IXIC": "NASDAQ", "^DJI": "道瓊",
        "DX-Y.NYB": "美元指數", "^TWII": "台灣加權指數"
    }

    lines.append("【美股指數】")
    for sym in ["^GSPC", "^IXIC", "^DJI", "DX-Y.NYB"]:
        if sym in us:
            d = us[sym]
            lines.append(f"  {index_names[sym]}: {d['price']} ({d['change_pct']:+.2f}%)")

    lines.append("\n【台股指數】")
    if "^TWII" in tw:
        d = tw["^TWII"]
        lines.append(f"  台灣加權指數: {d['price']} ({d['change_pct']:+.2f}%)")

    lines.append("\n【美股個股】")
    us_stocks = ["AAPL","MSFT","GOOGL","AMZN","META","NVDA","TSLA","AMD","TSM","ARM","JPM","GS","BRK-B"]
    for sym in us_stocks:
        if sym in us:
            d = us[sym]
            lines.append(f"  {sym}: {d['price']} ({d['change_pct']:+.2f}%)")

    lines.append("\n【台股個股】")
    for sym, d in tw.items():
        if sym != "^TWII":
            lines.append(f"  {d.get('name', sym)}: {d['price']} ({d['change_pct']:+.2f}%)")

    return "\n".join(lines)


def _format_news(articles: list, max_items: int = 8) -> str:
    lines = []
    for a in articles[:max_items]:
        tag = "✅" if a.get("verified") else "⚠️"
        url = a.get("url", "")
        sources = ", ".join(a.get("sources", []))
        lines.append(f"  {tag} {a.get('title', '')} [{sources}] URL:{url}")
    return "\n".join(lines)


def generate_report(data: dict) -> str:
    market_text = _format_market_data(data)
    us_news_text = _format_news(data.get("us_news", []))
    tw_news_text = _format_news(data.get("tw_news", []))
    date = data.get("date", "")

    prompt = f"""你是一個很懂財經、但說話很生活化的朋友。你的讀者是台灣上班族，每天早上 7 點看你的日報，他們沒時間讀長文，但想快速知道「今天股市有什麼大事、我手上的股票怎麼了」。

寫作風格：
- 像聰明的朋友在傳訊息，不是在寫分析報告
- 可以用 emoji，但不要氾濫
- 數字要具體（不要說「大幅上漲」，要說「漲了 3.2%」）
- 每個重點用一兩句話說清楚，不廢話
- 偶爾可以加一點幽默感或生活化比喻，但不要過頭
- 繁體中文，可以夾帶少量英文股票代號

日期：{date}

{market_text}

【今日新聞（已過濾假訊息，75 則中精選）】
{us_news_text}

優先挑選最可能影響股市的事件：
- Fed 官員發言 / 利率動向
- 重大財報與超預期數據
- AI / 科技產品重大消息
- 地緣政治 / 貿易戰
- CPI、就業、GDP 等總經數據
- 個股大漲大跌原因

請輸出以下 HTML 結構（直接輸出 HTML，不加 markdown code block，不加 ```html）：

<div class="tldr">
<div class="tldr-title">☕ 30 秒看完今天重點</div>
<ul>
  <li>（最重要的事，一句話）</li>
  <li>（第二重要的事）</li>
  <li>（第三重要的事）</li>
</ul>
</div>

<div class="section-label">📈 大盤怎麼了</div>
（用 2-3 句話說大盤狀況，口語化。例如：「昨天整體偏樂觀，S&P500 漲了 0.8%，主要是因為...」）

<div class="section-label">🔥 今天最重要的 5 件事</div>
（每件事格式如下，挑最可能影響股市的）
<div class="news-card">
  <div class="news-tag verified">✅ 多源確認</div>
  <div class="news-headline">（標題，口語化改寫，不超過 25 字）</div>
  <div class="news-why">💡 為什麼重要：（一句話說清楚這對股市的影響）</div>
  <a class="read-more" href="（該新聞的 URL）" target="_blank">閱讀原文 →</a>
</div>
（重複 5 次，⚠️ 單一來源的用 <div class="news-tag single">⚠️ 單一來源</div>）

<div class="section-label">🏢 你的持股今天怎樣</div>
（每檔股票格式）
<div class="stock-card">
  <span class="ticker">NVDA</span>
  <span class="stock-move up">▲ +4.2%</span>
  <div class="stock-comment">（一句話：漲/跌原因 + 要不要擔心）</div>
</div>
（涵蓋 AAPL MSFT GOOGL AMZN META NVDA TSLA AMD TSM JPM，有數據的才寫）

<div class="section-label">🌍 大環境訊號</div>
（2-3 個 bullet，只挑真正重要的總經信號，口語化）

<div class="section-label">🎯 今天的結論</div>
<div class="verdict SENTIMENT">
  <div class="verdict-emoji">（根據情緒選：📈 偏多 / 📉 偏空 / 😐 觀望）</div>
  <div class="verdict-text">（2-3 句話，口語說出今天市場情緒 + 普通人應該注意什麼）</div>
</div>
<div class="watch-list">
  <div class="watch-title">📌 本週還要注意</div>
  （2-4 個即將發生的重要事件，格式：日期 · 事件名稱）
</div>

注意：SENTIMENT 請換成實際情緒的 CSS class（bullish / bearish / neutral）
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
