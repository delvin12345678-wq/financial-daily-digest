"""股票中英文名稱對照 — 讓日報顯示公司名,不只有代號。"""

import re

US_NAMES = {
    "AAPL": ("蘋果", "Apple"),
    "MSFT": ("微軟", "Microsoft"),
    "GOOGL": ("谷歌", "Alphabet"),
    "GOOG": ("谷歌", "Alphabet"),
    "AMZN": ("亞馬遜", "Amazon"),
    "META": ("Meta", "Meta"),
    "NVDA": ("輝達", "Nvidia"),
    "TSLA": ("特斯拉", "Tesla"),
    "AMD": ("超微", "AMD"),
    "TSM": ("台積電 ADR", "TSMC"),
    "ARM": ("安謀", "Arm"),
    "JPM": ("摩根大通", "JPMorgan"),
    "GS": ("高盛", "Goldman Sachs"),
    "BRK-B": ("波克夏", "Berkshire"),
    "AVGO": ("博通", "Broadcom"),
    "NFLX": ("網飛", "Netflix"),
    "INTC": ("英特爾", "Intel"),
    "MU": ("美光", "Micron"),
    "QCOM": ("高通", "Qualcomm"),
    "PLTR": ("Palantir", "Palantir"),
    "COST": ("好市多", "Costco"),
    "DIS": ("迪士尼", "Disney"),
    "BABA": ("阿里巴巴", "Alibaba"),
    "SMCI": ("美超微", "Supermicro"),
    "MSTR": ("微策略", "MicroStrategy"),
    "COIN": ("Coinbase", "Coinbase"),
    "UBER": ("優步", "Uber"),
    "CRM": ("賽富時", "Salesforce"),
    "ORCL": ("甲骨文", "Oracle"),
    "ADBE": ("奧多比", "Adobe"),
    "PYPL": ("PayPal", "PayPal"),
    "BA": ("波音", "Boeing"),
    "WMT": ("沃爾瑪", "Walmart"),
    "KO": ("可口可樂", "Coca-Cola"),
    "MCD": ("麥當勞", "McDonald's"),
    "NKE": ("耐吉", "Nike"),
    "V": ("Visa", "Visa"),
    "MA": ("萬事達卡", "Mastercard"),
    "XOM": ("艾克森美孚", "ExxonMobil"),
    "LLY": ("禮來", "Eli Lilly"),
    "JNJ": ("嬌生", "Johnson & Johnson"),
    "UNH": ("聯合健康", "UnitedHealth"),
    "IONQ": ("IonQ", "IonQ"),
    "QBTS": ("D-Wave", "D-Wave"),
    "QUBT": ("Quantum Computing", "Quantum Computing"),
    "RGTI": ("Rigetti", "Rigetti"),
}

TW_NAMES = {
    "2330": ("台積電", "TSMC"),
    "2454": ("聯發科", "MediaTek"),
    "2317": ("鴻海", "Hon Hai"),
    "2308": ("台達電", "Delta"),
    "2382": ("廣達", "Quanta"),
    "2379": ("瑞昱", "Realtek"),
    "2303": ("聯電", "UMC"),
    "3008": ("大立光", "Largan"),
    "2412": ("中華電", "Chunghwa Telecom"),
    "2881": ("富邦金", "Fubon"),
    "2882": ("國泰金", "Cathay"),
    "6531": ("精測", "CHPT"),
    "3711": ("日月光投控", "ASE"),
    "2891": ("中信金", "CTBC"),
    "2603": ("長榮", "Evergreen"),
    "2002": ("中鋼", "China Steel"),
    "1301": ("台塑", "Formosa Plastics"),
    "3034": ("聯詠", "Novatek"),
    "3037": ("欣興", "Unimicron"),
    "2357": ("華碩", "ASUS"),
    "3231": ("緯創", "Wistron"),
    "2376": ("技嘉", "Gigabyte"),
    "2615": ("萬海", "Wan Hai"),
    "2609": ("陽明", "Yang Ming"),
}


def _names(code, tw_hint=None):
    c = (code or "").strip().upper()
    if c in US_NAMES:
        return US_NAMES[c]
    if c in TW_NAMES:
        return TW_NAMES[c]
    if tw_hint:
        return (tw_hint.strip(), "")
    return ("", "")


def is_known(code):
    c = (code or "").strip().upper()
    return c in US_NAMES or c in TW_NAMES


def display_name(code, tw_hint=None):
    """回傳『中文 英文』,例如 '輝達 Nvidia';無資料回 code 本身。"""
    cn, en = _names(code, tw_hint)
    if cn and en and cn != en:
        return f"{cn} {en}"
    return cn or code


def label_with_code(code, tw_hint=None):
    """回傳『中文 代號』,例如 '輝達 NVDA'、'台積電 2330'。"""
    cn, _ = _names(code, tw_hint)
    if cn and cn != code:
        return f"{cn} {code}"
    return code


def badge_html(code, tw_hint=None):
    """ticker 徽章 HTML:公司中英文名 + 小灰代號。"""
    name = display_name(code, tw_hint)
    if name == code:
        return code
    return (
        '<span style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;'
        f'font-weight:800;">{name}</span>'
        '<span style="font-family:\'SF Mono\',ui-monospace,monospace;font-size:10px;'
        f'color:#8e8e93;margin-left:5px;font-weight:700;">{code}</span>'
    )


def pick_code(content):
    """從一段文字裡挑出第一個看起來像股票代號的 token。"""
    for tok in re.split(r'[\s（）()／/|｜·,，、]+', (content or "").strip()):
        t = tok.strip().upper()
        if not t:
            continue
        if is_known(t) or re.fullmatch(r'\d{4,6}', t) or re.fullmatch(r'[A-Z]{1,5}(?:-[A-Z])?', t):
            return t
    return (content or "").strip()
