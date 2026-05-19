import os
from data_fetcher import fetch_all
from fake_news_filter import filter_us_news, filter_tw_news
from analyzer import generate_report
from publisher import publish_to_brevo


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
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; color: #222; }}
  h2 {{ color: #1a1a2e; border-bottom: 2px solid #e0e0e0; padding-bottom: 6px; }}
</style>
</head>
<body>
<h1>📊 財經日報 {date}</h1>
{html_report}
</body>
</html>""")
    print(f"   本地預覽已儲存：{path}")
    return path


def run():
    print("① 抓取市場數據與新聞...")
    data = fetch_all()

    print("② 過濾假訊息...")
    data["us_news"] = filter_us_news(data["us_news"])
    data["tw_news"] = filter_tw_news(data["tw_news"])
    print(f"   美股新聞：{len(data['us_news'])} 則通過過濾")
    print(f"   台股新聞：{len(data['tw_news'])} 則通過過濾")

    print("③ AI 生成報告...")
    html_report = generate_report(data)

    print("④ 儲存本地預覽...")
    save_local(data["date"], html_report)

    print("⑤ 發布到 Brevo...")
    from config import BREVO_API_KEY
    if not BREVO_API_KEY:
        print("   Brevo API key 尚未設定，跳過發布")
    else:
        success = publish_to_brevo(data["date"], html_report)
        if success:
            print("✅ 今日財經日報發布完成！")
        else:
            print("❌ Brevo 發布失敗，本地預覽仍可查看")


if __name__ == "__main__":
    run()
