import requests
from config import BREVO_API_KEY, SENDER_EMAIL, SENDER_NAME

BREVO_SEND_URL = "https://api.brevo.com/v3/emailCampaigns"


def get_list_id() -> int:
    resp = requests.get(
        "https://api.brevo.com/v3/contacts/lists",
        headers={"api-key": BREVO_API_KEY},
        timeout=10
    )
    lists = resp.json().get("lists", [])
    return lists[0]["id"] if lists else 2


def publish_to_brevo(date: str, html_content: str) -> bool:
    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json"
    }
    list_id = get_list_id()
    payload = {
        "name": f"財經日報 {date}",
        "subject": f"📊 財經日報 {date} — AI 精選美股 + 台股",
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "type": "classic",
        "htmlContent": html_content,
        "recipients": {"listIds": [list_id]},
        "scheduledAt": None
    }
    try:
        resp = requests.post(BREVO_SEND_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        campaign_id = resp.json().get("id", "")
        send_resp = requests.post(
            f"{BREVO_SEND_URL}/{campaign_id}/sendNow",
            headers={"api-key": BREVO_API_KEY},
            timeout=30
        )
        send_resp.raise_for_status()
        print(f"發布成功：campaign_id={campaign_id}")
        return True
    except requests.HTTPError as e:
        print(f"發布失敗：{e.response.status_code} {e.response.text}")
        return False
    except Exception as e:
        print(f"發布失敗：{e}")
        return False
