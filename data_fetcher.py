import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
from config import (
    NEWS_API_KEY, US_STOCKS, TW_STOCKS, US_INDICES, TW_INDICES,
    NEWS_WHITELIST_DOMAINS, TW_NEWS_WHITELIST_DOMAINS
)

RSS_FEEDS = [
    # 美股財經
    ("reuters.com",     "https://feeds.reuters.com/reuters/businessNews"),
    ("cnbc.com",        "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("cnbc.com",        "https://www.cnbc.com/id/15839069/device/rss/rss.html"),  # tech
    ("cnbc.com",        "https://www.cnbc.com/id/20910258/device/rss/rss.html"),  # earnings
    ("marketwatch.com", "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("marketwatch.com", "https://feeds.marketwatch.com/marketwatch/marketpulse/"),
    ("finance.yahoo.com","https://finance.yahoo.com/news/rssindex"),
    ("investing.com",   "https://www.investing.com/rss/news.rss"),
    ("investing.com",   "https://www.investing.com/rss/stock_market_news.rss"),
    ("seekingalpha.com","https://seekingalpha.com/market_currents.xml"),
    ("ft.com",          "https://www.ft.com/?format=rss"),
]

def fetch_rss_news() -> list:
    articles = []
    cutoff = datetime.now() - timedelta(hours=36)
    for domain, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    import time
                    published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                if published and published < cutoff:
                    continue
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", "")[:200],
                    "url": entry.get("link", f"https://{domain}"),
                    "source": {"name": domain},
                    "publishedAt": published.isoformat() if published else "",
                })
        except Exception:
            continue
    return articles


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


def fetch_ticker_news() -> list:
    articles = []
    seen = set()
    for symbol in ["NVDA", "AAPL", "MSFT", "TSLA", "META", "GOOGL", "TSM", "AMD"]:
        try:
            ticker = yf.Ticker(symbol)
            for item in ticker.news[:5]:
                title = item.get("title", "")
                if title in seen:
                    continue
                seen.add(title)
                url = item.get("link", "")
                domain = url.split("/")[2].replace("www.", "") if url else "finance.yahoo.com"
                articles.append({
                    "title": title,
                    "description": item.get("summary", ""),
                    "url": url,
                    "source": {"name": domain},
                    "publishedAt": "",
                    "relatedTicker": symbol,
                })
        except Exception:
            continue
    return articles


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
        api_articles = data.get("articles", [])
    except Exception:
        api_articles = []

    rss_articles = fetch_rss_news()
    ticker_articles = fetch_ticker_news()
    return api_articles + rss_articles + ticker_articles


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
