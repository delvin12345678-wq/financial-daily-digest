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
        lines.append(f"  {tag} {a.get('title', '')} [{', '.join(a.get('sources', []))}]")
    return "\n".join(lines)


def generate_report(data: dict) -> str:
    market_text = _format_market_data(data)
    us_news_text = _format_news(data.get("us_news", []))
    tw_news_text = _format_news(data.get("tw_news", []))
    date = data.get("date", "")

    prompt = f"""你是一位專業的財經分析師。請根據以下數據，用繁體中文撰寫一份今日財經日報。

日期：{date}

{market_text}

【今日美股新聞（已過濾假訊息）】
{us_news_text}

【今日台股新聞（已過濾假訊息）】
{tw_news_text}

請依照以下格式輸出 HTML 報告（直接輸出 HTML，不要加 markdown code block）：

<h2>① 大盤總覽</h2>
（用表格呈現指數漲跌，加上一句話整體判斷）

<h2>② 今日重點新聞</h2>
（列出最重要的 5 則新聞，✅ 代表多源確認，⚠️ 代表單一來源，需謹慎）

<h2>③ 個股動態</h2>
（針對每檔個股，一句話解讀今日表現與相關新聞）

<h2>④ 總體經濟信號</h2>
（從新聞中萃取 Fed、利率、通膨相關訊號）

<h2>⑤ 今日操作參考</h2>
（給出市場情緒判斷：偏多 / 偏空 / 觀望，並列出本週需注意的風險事件）

注意：⚠️ 標記的新聞請在呈現時提醒讀者「此消息僅見於單一來源，請謹慎判斷」。
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
