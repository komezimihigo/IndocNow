import os
import json
import requests
from datetime import datetime, timedelta
from newspaper import build

CACHE_FILE = "articles_cache.json"
CACHE_DURATION = timedelta(hours=48)

# Stable, fetchable news sites (1 per country)
NEWS_SITES = [
    "https://igihe.com/amakuru/u-rwanda",
    "https://www.newtimes.co.rw/news",
    "https://rwandatoday.africa/",
    "https://www.umuseke.rw/",
    "https://www.kigalitoday.com/",
    "https://nation.africa/",
    "https://www.graphic.com.gh/",
    "https://www.news24.com/",
    "https://www.monitor.co.ug/",
    "https://www.thecitizen.co.tz/",
    "https://www.seneweb.com/",
    "https://www.fanabc.com/eng/",
    "https://www.herald.co.zw/",
    "https://news.abidjan.net/",
    "https://apnews.com/",
    "https://www.nytimes.com/",
    "https://www.bbc.com/news",
    "https://www.lemonde.fr/",
    "https://www.dw.com/en/",
    "https://elpais.com/",
    "https://www.repubblica.it/",
    "https://www.hindustantimes.com/",
    "https://english.news.cn/",
    "https://www.aljazeera.com/news/",
    "https://www.abc.net.au/news/",
    "https://www.cbc.ca/news",
    "https://g1.globo.com/",
    "https://www.clarin.com/",
    "https://gulfnews.com/",
    "https://www.timesofisrael.com/",
    "https://www3.nhk.or.jp/nhkworld/en/news/",
    "https://koreajoongangdaily.joins.com/",
    "https://www.eluniversal.com.mx/",
]

# Your API keys (replace with actual keys)
GNEWS_API = "f94e1941ef18c29c1367bd3915f12bbd"
CURRENTS_API = "XJUbhpHw8oAME4n0DyiXESKfGKb0ATXtLLi9hPkxL1RQUkjL"
NEWSAPI_KEY = "041126cca1ac4f92b1994db02635db3c"

def is_cache_fresh():
    if not os.path.exists(CACHE_FILE):
        return False
    cache_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    return datetime.now() - cache_time < CACHE_DURATION

def fetch_all_articles():
    if is_cache_fresh():
        print("Loading articles from cache...")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching fresh articles...")
    articles = []
    article_id = 0

    # Newspaper3k sources
    for site in NEWS_SITES:
        try:
            paper = build(site, memoize_articles=False)
            reject_keywords = ["category", "advertisement", "subscribe", "terms", "privacy", "404", "error"]
            for a in paper.articles[:4]:
                try:
                    a.download()
                    a.parse()

                    # Clean and filter
                    if (
                            a.title and len(a.title) > 10 and
                            a.text and len(a.text) > 2000 and
                            not any(word in a.title.lower() for word in reject_keywords)
                    ):
                        if a.top_image and "logo" not in a.top_image.lower():
                            articles.append({
                                "id": article_id,
                                "title": a.title.strip(),
                                "content": a.text.strip(),
                                "image": a.top_image
                            })
                            article_id += 1

                except Exception as e:
                    print("Parse error:", e)

                if a.title and len(a.title) > 10 and len(a.text) > 2000:
                    articles.append({
                        "id": article_id,
                        "title": a.title,
                        "content": a.text,
                        "image": a.top_image
                    })
                    article_id += 1
        except Exception as e:
            print(f"Newspaper error ({site}):", e)
    # Remove duplicate articles by title
    unique_titles = set()
    filtered_articles = []
    for art in articles:
        if art["title"] not in unique_titles:
            unique_titles.add(art["title"])
            filtered_articles.append(art)

    articles = filtered_articles
    # GNews
    try:
        print("Fetching GNews...")
        gresp = requests.get(f"https://gnews.io/api/v4/top-headlines?lang=en&token={GNEWS_API}")
        data = gresp.json()
        for a in data.get("articles", [])[:4]:
            articles.append({
                "id": article_id,
                "title": a['title'],
                "content": f"{a.get('description', '')}\n{a.get('content', '')}",
                "image": a.get("image", "")
            })
            article_id += 1
    except Exception as e:
        print("GNews API error:", e)

    # Currents
    try:
        print("Fetching Currents...")
        cresp = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API}")
        data = cresp.json()
        for a in data.get("articles", [])[:4]:
            articles.append({
                "id": article_id,
                "title": a['title'],
                "content": a.get("description", ""),
                "image": a.get("image", "")
            })
            article_id += 1
    except Exception as e:
        print("Currents API error:", e)

    # NewsAPI
    try:
        print("Fetching NewsAPI...")
        nresp = requests.get(f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWSAPI_KEY}")
        data = nresp.json()
        for a in data.get("articles", [])[:4]:
            articles.append({
                "id": article_id,
                "title": a['title'],
                "content": a.get("description", ""),
                "image": a.get("urlToImage", "")
            })
            article_id += 1
    except Exception as e:
        print("NewsAPI error:", e)



    # Save to cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f,ensure_ascii=False, indent=2)

    print(f"Fetched and cached {len(articles)} articles.")
    return articles

def get_article_by_id(articles, article_id):
    for a in articles:
        if a["id"] == article_id:
            return a
    return None
