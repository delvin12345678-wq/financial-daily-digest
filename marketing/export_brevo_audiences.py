"""
Brevo → Meta Custom Audience CSV exporter

產出 3 個 CSV 給 Meta Ads Manager 上傳:
1. premium_subscribers.csv    — 已升 Premium 者(用於 Exclude + Lookalike seed)
2. free_subscribers.csv       — 免費訂戶(用於 Exclude cold campaign)
3. all_subscribers.csv        — 所有訂戶(用於整體 Exclude)

Meta Custom Audience 要求格式:
  - 標頭:email,phone,fn,ln,ct,st,country,zip,dob,gen,madid
  - email 可選 hashed(我們用 raw 讓 Meta 自己 hash,因為我們也沒有其他欄位)
  - 一行一個 user
  - UTF-8

使用:
  cd marketing && python3 export_brevo_audiences.py

輸出:
  marketing/meta_audiences/{premium,free,all}_subscribers.csv
"""
import os
import csv
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
LIST_ID = int(os.getenv("BREVO_LIST_ID", "2"))
WORKER_URL = "https://marketdaily-webhook.delvin-12345678.workers.dev"
OUT_DIR = Path(__file__).parent / "meta_audiences"
OUT_DIR.mkdir(exist_ok=True)


def fetch_brevo_contacts(list_id: int) -> list[dict]:
    """Paginate Brevo list contacts."""
    all_contacts = []
    offset = 0
    limit = 500
    while True:
        url = f"https://api.brevo.com/v3/contacts/lists/{list_id}/contacts?limit={limit}&offset={offset}"
        req = urllib.request.Request(url, headers={"api-key": BREVO_API_KEY, "accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            print(f"Brevo fetch error at offset {offset}: {e.code} {e.read()[:200]!r}")
            break
        batch = data.get("contacts", [])
        if not batch:
            break
        all_contacts.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return all_contacts


def get_plan_for(email: str) -> str:
    """Worker KV plan:${email} 才是 plan 唯一真實來源。"""
    url = f"{WORKER_URL}/check-subscriber"
    body = json.dumps({"email": email}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
            return d.get("plan", "free")
    except Exception:
        return "free"


META_HEADER = ["email", "phone", "fn", "ln", "ct", "st", "country", "zip", "dob", "gen", "madid"]


def write_csv(path: Path, emails: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(META_HEADER)
        for em in emails:
            row = [em] + [""] * (len(META_HEADER) - 1)
            w.writerow(row)
    print(f"  ✓ {path.name}: {len(emails)} rows")


def main():
    if not BREVO_API_KEY:
        print("✗ BREVO_API_KEY missing in .env")
        return

    print("① 拉 Brevo 訂閱者...")
    contacts = fetch_brevo_contacts(LIST_ID)
    print(f"   共 {len(contacts)} 位")

    # 不依賴 Brevo PAID attribute(常 desync),用 worker KV 為真實 plan 來源 — 但因為 N 大時太慢,
    # 用 contact.attributes.PLAN_TIER 當 fast-path,只有 KV 沒 sync 的少數 mismatch 在 KV→Brevo 一次性
    # 同步後就會自動修。Premium 寧可多列(因為 Exclude 邏輯下多列是 safe 的,少列才會浪費 ad spend)。
    print("② 分流 plan(用 Brevo attribute,假設 KV 已同步)...")
    all_emails = []
    premium_emails = []
    free_emails = []
    for c in contacts:
        em = (c.get("email") or "").strip().lower()
        if not em:
            continue
        all_emails.append(em)
        plan_tier = (c.get("attributes", {}).get("PLAN_TIER") or "").lower()
        paid = c.get("attributes", {}).get("PAID")
        if plan_tier == "premium" or paid is True:
            premium_emails.append(em)
        else:
            free_emails.append(em)

    print(f"   premium={len(premium_emails)} · free={len(free_emails)} · all={len(all_emails)}")

    print("③ 寫出 Meta 上傳格式 CSV...")
    write_csv(OUT_DIR / "premium_subscribers.csv", premium_emails)
    write_csv(OUT_DIR / "free_subscribers.csv", free_emails)
    write_csv(OUT_DIR / "all_subscribers.csv", all_emails)

    print(f"\n✓ 完成 → {OUT_DIR}")
    print("\n下一步:")
    print("1. 開 Meta Ads Manager → Audiences:")
    print("   https://business.facebook.com/adsmanager/audiences")
    print("2. 點 Create Audience → Custom Audience → Customer List")
    print("3. Upload all_subscribers.csv → Name: 'MD All Subscribers'(Exclude 用)")
    print("4. Upload premium_subscribers.csv → Name: 'MD Premium'(Lookalike seed)")
    print("5. 等 ~1 小時 match,然後在 LAL 介面建 1% Lookalike of Premium")


if __name__ == "__main__":
    main()
