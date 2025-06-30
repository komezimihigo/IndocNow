import os
import json
import requests
from datetime import datetime, timedelta
from newspaper import build

# Cache file for saving fetched articles
CACHE_FILE = "articles_cache.json"
CACHE_DURATION = timedelta(hours=48)  # Cache is valid for 48 hours

# Stable, fetchable news sites (1 per country)
NEWS_SITES = [

    "https://www.umuseke.rw/",
    "https://www.kigalitoday.com/",
    "https://nation.africa/",
    "https://www.graphic.com.gh/",
    "https://igihe.com/amakuru/u-rwanda",
    "https://www.newtimes.co.rw/news",
    "https://rwandatoday.africa/",
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
    "https://www.eluniversal.com.mx/"
]

# Your API keys (replace with actual keys)
GNEWS_API = "f94e1941ef18c29c1367bd3915f12bbd"
CURRENTS_API = "XJUbhpHw8oAME4n0DyiXESKfGKb0ATXtLLi9hPkxL1RQUkjL"
NEWSAPI_KEY = "041126cca1ac4f92b1994db02635db3c"


# Load from saved local JSON
def load_articles():
    try:
        with open('articles.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("Error loading articles.json:", e)
        return []


# Check if cached data is still fresh
def is_cache_fresh():
    if not os.path.exists(CACHE_FILE):
        return False
    cache_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    return datetime.now() - cache_time < CACHE_DURATION


# Fetch all articles from APIs and websites
def fetch_all_articles():
    if is_cache_fresh():
        print("Loading articles from cache...")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching fresh articles...")
    articles = []
    article_id = 0
    unique_titles = set()

    # Newspaper3k websites
    for site in NEWS_SITES:
        try:
            paper = build(site, memoize_articles=False)
            for a in paper.articles[:6]:
                try:
                    a.download()
                    a.parse()
                    title = a.title.strip() if a.title else ""
                    content = a.text.strip() if a.text else ""
                    image = a.top_image if a.top_image else ""

                    if (len(title) > 10 and len(content) > 2000 and
                            not any(word in title.lower() for word in
                                    ["advertisement", "kwamamaza","keza" "subscribe", "terms", "404", "privacy", "error"]) and
                            title not in unique_titles):
                        articles.append({
                            "id": article_id,
                            "title": title,
                            "content": content,
                            "image": image
                        })
                        unique_titles.add(title)
                        article_id += 1
                except Exception as e:
                    print("Parse error:", e)
        except Exception as e:
            print(f"Newspaper error ({site}):", e)

    # GNews API
    try:
        print("Fetching GNews...")
        gresp = requests.get(f"https://gnews.io/api/v4/top-headlines?lang=en&token={GNEWS_API}")
        data = gresp.json()
        for a in data.get("articles", [])[:6]:
            title = a.get("title", "")
            if title and title not in unique_titles:
                articles.append({
                    "id": article_id,
                    "title": title,
                    "content": f"{a.get('description', '')}\n{a.get('content', '')}",
                    "image": a.get("image", "")
                })
                unique_titles.add(title)
                article_id += 1
    except Exception as e:
        print("GNews API error:", e)

    # Currents API
    try:
        print("Fetching Currents...")
        cresp = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API}")
        data = cresp.json()
        for a in data.get("news", [])[:6]:
            title = a.get("title", "")
            if title and title not in unique_titles:
                articles.append({
                    "id": article_id,
                    "title": title,
                    "content": a.get("description", ""),
                    "image": a.get("image", "")
                })
                unique_titles.add(title)
                article_id += 1
    except Exception as e:
        print("Currents API error:", e)

    # NewsAPI
    try:
        print("Fetching NewsAPI...")
        nresp = requests.get(f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWSAPI_KEY}")
        data = nresp.json()
        for a in data.get("articles", [])[:6]:
            title = a.get("title", "")
            if title and title not in unique_titles:
                articles.append({
                    "id": article_id,
                    "title": title,
                    "content": a.get("description", ""),
                    "image": a.get("urlToImage", "")
                })
                unique_titles.add(title)
                article_id += 1
    except Exception as e:
        print("NewsAPI error:", e)

    # Save to cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Fetched and cached {len(articles)} articles.")
    return articles


# Get a single article by ID
def get_article_by_id(articles, article_id):
    for a in articles:
        if str(a["id"]) == str(article_id):
            return a
    return None

