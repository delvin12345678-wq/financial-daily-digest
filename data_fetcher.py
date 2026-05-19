import yfinance as yf
import requests
from datetime import datetime, timedelta
from config import (
    NEWS_API_KEY, US_STOCKS, TW_STOCKS, US_INDICES, TW_INDICES,
    NEWS_WHITELIST_DOMAINS, TW_NEWS_WHITELIST_DOMAINS
)


def fetch_us_market():
    result = {}
    for symbol in US_INDICES + US_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_close = hist["Close"].iloc[-1]
                change_pct = (last_close - prev_close) / prev_close * 100
                result[symbol] = {
                    "price": round(last_close, 2),
                    "change_pct": round(change_pct, 2)
                }
        except Exception:
            continue
    return result


def fetch_tw_market():
    result = {}
    try:
        ticker = yf.Ticker("^TWII")
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            prev_close = hist["Close"].iloc[-2]
            last_close = hist["Close"].iloc[-1]
            change_pct = (last_close - prev_close) / prev_close * 100
            result["^TWII"] = {
                "price": round(last_close, 2),
                "change_pct": round(change_pct, 2)
            }
    except Exception:
        pass

    for stock in TW_STOCKS:
        try:
            symbol = f"{stock['symbol']}.TW"
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_close = hist["Close"].iloc[-1]
                change_pct = (last_close - prev_close) / prev_close * 100
                result[stock["symbol"]] = {
                    "name": stock["name"],
                    "price": round(last_close, 2),
                    "change_pct": round(change_pct, 2)
                }
        except Exception:
            continue
    return result


def fetch_us_news():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    domains = ",".join(NEWS_WHITELIST_DOMAINS)
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q=stock+market+economy+fed+earnings"
        f"&domains={domains}"
        f"&from={yesterday}"
        f"&language=en"
        f"&sortBy=relevancy"
        f"&pageSize=20"
        f"&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("articles", [])
    except Exception:
        return []


def fetch_tw_news():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q=Taiwan+stock+TSMC+TWD+Taiwan+economy"
        f"&from={yesterday}"
        f"&language=en"
        f"&sortBy=relevancy"
        f"&pageSize=20"
        f"&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("articles", [])
    except Exception:
        return []


def fetch_all():
    return {
        "us_market": fetch_us_market(),
        "tw_market": fetch_tw_market(),
        "us_news": fetch_us_news(),
        "tw_news": fetch_tw_news(),
        "date": datetime.now().strftime("%Y-%m-%d")
    }
