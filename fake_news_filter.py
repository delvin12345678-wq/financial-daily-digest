from collections import defaultdict
from config import NEWS_WHITELIST_DOMAINS, TW_NEWS_WHITELIST_DOMAINS, VAGUE_KEYWORDS


def _domain_from_url(url: str) -> str:
    try:
        return url.split("/")[2].replace("www.", "")
    except Exception:
        return ""


def _has_vague_language(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in VAGUE_KEYWORDS)


def filter_and_label(articles: list, whitelist: list) -> list:
    title_map = defaultdict(list)
    for article in articles:
        domain = _domain_from_url(article.get("url", ""))
        if domain not in whitelist:
            continue
        title = article.get("title", "")
        if _has_vague_language(title + " " + article.get("description", "")):
            continue
        title_map[title].append(article)

    result = []
    for title, group in title_map.items():
        article = group[0]
        sources = list({_domain_from_url(a["url"]) for a in group})
        article["verified"] = len(sources) >= 2
        article["sources"] = sources
        result.append(article)

    result.sort(key=lambda a: a["verified"], reverse=True)
    return result


def filter_us_news(articles: list) -> list:
    return filter_and_label(articles, NEWS_WHITELIST_DOMAINS)


def filter_tw_news(articles: list) -> list:
    # Taiwan news is fetched in English from US whitelist sources
    return filter_and_label(articles, NEWS_WHITELIST_DOMAINS)
