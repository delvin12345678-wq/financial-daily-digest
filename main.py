import os
import re
from data_fetcher import fetch_all
from fake_news_filter import filter_us_news, filter_tw_news
from analyzer import generate_report
from publisher import publish_to_brevo


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif; background: #f2f2f7; color: #1d1d1f; }
.wrapper { max-width: 620px; margin: 0 auto; background: #fff; }

.header { background: #0a0a0a; color: #fff; padding: 26px 20px 20px; }
.header-meta { font-size: 10px; color: rgba(255,255,255,0.38); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.header h1 { font-size: 21px; font-weight: 700; letter-spacing: -0.3px; }
.header-tagline { font-size: 11px; color: rgba(255,255,255,0.32); margin-top: 5px; }

.tldr { background: #fff9f0; border-left: 3px solid #ff9500; margin: 18px 20px 0; padding: 13px 15px; border-radius: 0 10px 10px 0; }
.tldr-title { font-size: 11px; font-weight: 700; color: #c25e00; margin-bottom: 8px; letter-spacing: 0.8px; text-transform: uppercase; }
.tldr ul { list-style: none; }
.tldr ul li { font-size: 14px; color: #3a3a3c; padding: 3px 0 3px 14px; position: relative; line-height: 1.6; }
.tldr ul li::before { content: "→"; position: absolute; left: 0; color: #ff9500; font-weight: 600; font-size: 12px; }

.section-label { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #8e8e93; padding: 20px 20px 9px; }

.market-summary { padding: 0 20px 14px; font-size: 14px; color: #3a3a3c; line-height: 1.75; }

.news-card { margin: 0 20px 10px; padding: 13px 15px; border: 1px solid #e5e5ea; border-radius: 10px; background: #fff; }
.news-tag { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px; margin-bottom: 7px; letter-spacing: 0.3px; }
.news-tag.verified { background: #e3f9e5; color: #1a6b30; }
.news-tag.single { background: #fff4e0; color: #8a4500; }
.news-headline { font-size: 14px; font-weight: 700; color: #1d1d1f; line-height: 1.45; margin-bottom: 7px; }
.news-why { font-size: 13px; color: #48484a; line-height: 1.55; background: #f2f2f7; padding: 7px 10px; border-radius: 8px; }
.read-more { display: inline-block; margin-top: 8px; font-size: 12px; font-weight: 600; color: #0066cc; text-decoration: none; }
.read-more:hover { text-decoration: underline; }

.stock-card { display: flex; align-items: flex-start; gap: 10px; margin: 0 20px 8px; padding: 11px 13px; border-radius: 10px; background: #f2f2f7; border: 1px solid #e5e5ea; }
.ticker { font-size: 13px; font-weight: 800; color: #0a0a0a; min-width: 56px; padding-top: 2px; font-family: "SF Mono", ui-monospace, monospace; }
.stock-move { font-size: 14px; font-weight: 700; min-width: 76px; padding-top: 2px; }
.stock-move.up { color: #30d158; }
.stock-move.down { color: #ff3b30; }
.stock-comment { font-size: 13px; color: #48484a; line-height: 1.55; flex: 1; }

.macro-list { padding: 0 20px 14px; }
.macro-item { font-size: 14px; color: #3a3a3c; padding: 6px 0; border-bottom: 1px solid #f2f2f7; line-height: 1.65; }

.verdict { margin: 0 20px 12px; padding: 15px; border-radius: 12px; }
.verdict.bullish { background: #f0fdf4; border: 1px solid #bbf7d0; }
.verdict.bearish { background: #fff1f2; border: 1px solid #fecdd3; }
.verdict.neutral { background: #f2f2f7; border: 1px solid #e5e5ea; }
.verdict-emoji { font-size: 24px; margin-bottom: 8px; }
.verdict-text { font-size: 14px; color: #3a3a3c; line-height: 1.75; }

.watch-list { margin: 0 20px 22px; padding: 13px 15px; background: #f2f2f7; border-radius: 10px; }
.watch-title { font-size: 10px; font-weight: 700; color: #8e8e93; margin-bottom: 8px; letter-spacing: 1.2px; text-transform: uppercase; }
.watch-item { font-size: 13px; color: #3a3a3c; padding: 5px 0; border-bottom: 1px solid #e5e5ea; }
.watch-item:last-child { border-bottom: none; }

.indicator-bar { display: flex; gap: 8px; margin: 0 20px 14px; flex-wrap: wrap; }
.indicator-item { flex: 0 0 calc(20% - 7px); min-width: 88px; padding: 11px 10px; background: #f2f2f7; border: 1px solid #e5e5ea; border-radius: 10px; text-align: center; }
.indicator-label { font-size: 9px; font-weight: 700; color: #8e8e93; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 4px; }
.indicator-value { font-size: 16px; font-weight: 800; color: #1d1d1f; }
.indicator-sub { font-size: 10px; color: #8e8e93; margin-top: 2px; }
.indicator-fear { color: #ff3b30; }
.indicator-greed { color: #30d158; }
.indicator-neutral { color: #ff9500; }

.second-order { margin: 0 20px 14px; padding: 13px 15px; background: #f0f0ff; border-left: 3px solid #5e5ce6; border-radius: 0 10px 10px 0; font-size: 13px; color: #3a3a3c; line-height: 1.75; }

.crypto-bar { display: flex; gap: 8px; margin: 0 20px 14px; }
.crypto-item { flex: 1; padding: 12px; background: #f2f2f7; border: 1px solid #e5e5ea; border-radius: 10px; text-align: center; }
.crypto-name { font-size: 10px; font-weight: 700; color: #8e8e93; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
.crypto-price { font-size: 17px; font-weight: 800; }
.crypto-price.up { color: #30d158; }
.crypto-price.down { color: #ff3b30; }
.crypto-change { font-size: 11px; color: #8e8e93; margin-top: 2px; }

.sector-bar { padding: 0 20px 14px; }
.sector-item { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-bottom: 1px solid #f2f2f7; }
.sector-name { font-size: 13px; font-weight: 600; color: #1d1d1f; min-width: 110px; }
.sector-move { font-size: 13px; font-weight: 700; min-width: 68px; }
.sector-move.up { color: #30d158; }
.sector-move.down { color: #ff3b30; }
.sector-comment { font-size: 12px; color: #8e8e93; flex: 1; }

.earnings-list { padding: 0 20px 14px; }
.earnings-item { display: flex; align-items: baseline; gap: 10px; padding: 7px 0; border-bottom: 1px solid #f2f2f7; }
.earnings-ticker { font-size: 13px; font-weight: 800; color: #0a0a0a; min-width: 52px; font-family: "SF Mono", ui-monospace, monospace; }
.earnings-date { font-size: 12px; color: #8e8e93; min-width: 80px; }
.earnings-note { font-size: 13px; color: #48484a; flex: 1; }

.stock-news-item { margin: 0 20px 10px; padding: 13px 15px; border: 1px solid #e0e0ff; border-radius: 10px; background: #f8f8ff; display: flex; gap: 12px; align-items: flex-start; }
.stock-news-ticker { font-size: 12px; font-weight: 800; color: #5e5ce6; min-width: 52px; padding-top: 2px; font-family: "SF Mono", ui-monospace, monospace; }
.stock-news-content { flex: 1; }
.stock-news-headline { font-size: 14px; font-weight: 600; color: #1d1d1f; line-height: 1.4; margin-bottom: 6px; }
.stock-news-impact { font-size: 13px; color: #48484a; background: #ebebff; padding: 6px 10px; border-radius: 8px; line-height: 1.55; }
.stock-news-empty { margin: 0 20px 14px; font-size: 13px; color: #aeaeb2; padding: 8px 0; }

.footer { background: #0a0a0a; color: rgba(255,255,255,0.28); text-align: center; padding: 18px 20px; font-size: 11px; line-height: 2; }
"""


def build_email_html(date: str, html_report: str) -> str:
    full = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>財經日報 {date}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="header-meta">{date}</div>
    <h1>📊 財經日報</h1>
    <div class="header-tagline">AI 精選 · 假訊息過濾 · 美股 + 台股</div>
  </div>
  {html_report}
  <div class="footer">
    財經日報 · AI 精選 · 假訊息過濾<br>
    ✅ 多源確認 = 2個以上白名單媒體報導 &nbsp;|&nbsp; ⚠️ 單一來源 = 請自行查證<br>
    本報告為 AI 生成，僅供參考，不構成投資建議<br><br>
    <a href="https://marketdaily.github.io/financial-daily-digest/" style="color:#6366f1;text-decoration:none;font-weight:700;">🌐 marketdaily.github.io/financial-daily-digest</a> &nbsp;·&nbsp;
    <a href="https://marketdaily.github.io/financial-daily-digest/dashboard.html" style="color:#a5b4fc;text-decoration:none;">⚙️ 我的專區</a>
  </div>
</div>
</body>
</html>"""
    try:
        from premailer import transform
        return transform(full, remove_classes=False, preserve_internal_links=True)
    except Exception:
        return full


def save_local(date: str, html_report: str):
    os.makedirs("output", exist_ok=True)
    path = f"output/digest_{date}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>財經日報 {date}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="header-meta">{date}</div>
    <h1>📊 財經日報</h1>
    <div class="header-tagline">AI 精選 · 假訊息過濾 · 美股 + 台股</div>
  </div>
  {html_report}
  <div class="footer">
    財經日報 · AI 精選 · 假訊息過濾<br>
    ✅ 多源確認 = 2個以上白名單媒體報導 &nbsp;|&nbsp; ⚠️ 單一來源 = 請自行查證<br>
    本報告為 AI 生成，僅供參考，不構成投資建議<br><br>
    <a href="https://marketdaily.github.io/financial-daily-digest/" style="color:#6366f1;text-decoration:none;font-weight:700;">🌐 marketdaily.github.io/financial-daily-digest</a> &nbsp;·&nbsp;
    <a href="https://marketdaily.github.io/financial-daily-digest/dashboard.html" style="color:#a5b4fc;text-decoration:none;">⚙️ 我的專區</a>
  </div>
</div>
</body>
</html>""")
    print(f"   本地預覽已儲存：{path}")
    return path


WORKER_URL = "https://marketdaily-webhook.delvin-12345678.workers.dev"


def _extract_sentiment(inner_html: str) -> str:
    m = re.search(r'class="verdict\s+(bullish|bearish|neutral)"', inner_html)
    return m.group(1) if m else "neutral"


def _inject_ai_banner(inner_html: str, date: str) -> str:
    """Generate and inject a sentiment banner image. Non-fatal if Muapi unavailable."""
    try:
        from image_generator import generate_digest_banner, inject_banner_into_html
        sentiment = _extract_sentiment(inner_html)
        image_url = generate_digest_banner(sentiment, date)
        if image_url:
            return inject_banner_into_html(inner_html, image_url)
    except Exception as e:
        print(f"  [Banner] 略過（{e}）")
    return inner_html


def get_user_preferences(email: str) -> dict:
    import requests
    try:
        res = requests.post(
            f"{WORKER_URL}/get-preferences",
            json={"email": email},
            timeout=5
        )
        if res.ok:
            return res.json()
    except Exception:
        pass
    return {"us_stocks": [], "tw_stocks": []}


def run():
    from config import BREVO_API_KEY
    from publisher import get_list_id, check_subscriber_count, get_all_subscribers, send_transactional_email

    if not BREVO_API_KEY:
        print("① 抓取市場數據與新聞...")
        data = fetch_all()
        print("② 過濾假訊息...")
        data["us_news"] = filter_us_news(data["us_news"])
        data["tw_news"] = filter_tw_news(data["tw_news"])
        print("③ AI 生成報告（預設版）...")
        inner = generate_report(data)
        print("④ 生成 AI 市場情緒 Banner...")
        inner = _inject_ai_banner(inner, data["date"])
        print("⑤ 儲存本地預覽...")
        save_local(data["date"], inner)
        return

    print("① 取得訂閱者名單與持倉偏好...")
    list_id = get_list_id()
    check_subscriber_count(list_id)
    subscribers = get_all_subscribers(list_id)
    print(f"   共 {len(subscribers)} 位訂閱者")

    subscriber_prefs = {}
    all_us_extra, all_tw_extra = set(), set()
    for email in subscribers:
        prefs = get_user_preferences(email)
        subscriber_prefs[email] = prefs
        for s in prefs.get("us_stocks") or []:
            all_us_extra.add(s)
        for s in prefs.get("tw_stocks") or []:
            all_tw_extra.add(s)

    print(f"② 抓取市場數據（含用戶個股：美股 +{len(all_us_extra)}，台股 +{len(all_tw_extra)}）...")
    data = fetch_all(
        extra_us_stocks=list(all_us_extra) if all_us_extra else None,
        extra_tw_stocks=list(all_tw_extra) if all_tw_extra else None
    )

    print("③ 過濾假訊息...")
    data["us_news"] = filter_us_news(data["us_news"])
    data["tw_news"] = filter_tw_news(data["tw_news"])
    print(f"   美股新聞：{len(data['us_news'])} 則通過過濾")
    print(f"   台股新聞：{len(data['tw_news'])} 則通過過濾")

    print("④ 生成 AI 市場情緒 Banner...")
    default_report = generate_report(data)
    default_report = _inject_ai_banner(default_report, data["date"])
    print("⑤ 儲存本地預覽（預設版）...")
    save_local(data["date"], default_report)

    print("⑥ 個人化發送...")
    from analyzer import get_personalized_subject
    success_count = 0
    for email in subscribers:
        prefs = subscriber_prefs[email]
        us_stocks = prefs.get("us_stocks") or []
        tw_stocks = prefs.get("tw_stocks") or []

        if us_stocks or tw_stocks:
            print(f"   {email} → 個人化（美股:{len(us_stocks)}, 台股:{len(tw_stocks)}）")
            inner = generate_report(data, us_stocks or None, tw_stocks or None)
            inner = _inject_ai_banner(inner, data["date"])
            subject = get_personalized_subject(data, us_stocks, tw_stocks, data["date"])
        else:
            inner = default_report
            subject = None

        html = build_email_html(data["date"], inner)
        ok = send_transactional_email(email, data["date"], html, BREVO_API_KEY, subject=subject)
        if ok:
            success_count += 1
        else:
            print(f"   ❌ 發送失敗：{email}")

    print(f"✅ 今日財經日報發送完成！成功 {success_count}/{len(subscribers)} 位")


if __name__ == "__main__":
    run()
