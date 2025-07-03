from flask import Flask, render_template, request, redirect, url_for, session
from fetch_news import fetch_all_articles, get_article_by_id
from voice_reader import generate_voice
from translator import translate_text
from protect import protect_route
import datetime
import uuid
import json
from flask_mail import Mail, Message
from flask import make_response, send_from_directory
from collections import Counter
from flask import send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ADMIN_PASSWORD'] = 'food12345'

app.secret_key = "eat me penny"

# Email configuration
app.config.update(
MAIL_SERVER = 'smtp.gmail.com',
MAIL_PORT = 587,
MAIL_USE_TLS = True,
MAIL_USERNAME = 'indocnow@gmail.com',
MAIL_PASSWORD = 'indocnow@123'  # App password should be used here
)
mail = Mail(app)
subscribers = []

# Cached articles
articles_store = fetch_all_articles()

views = Counter()
# Categories
CATEGORIES = [
    "technology", "sports", "politics", "entertainment",
    "health", "business", "world", "education"
]

def load_breaking_news():
    try:
        with open("breaking.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_breaking_news(news_list):
    with open("breaking.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, indent=2)

def load_comments():
    try:
        with open("comments.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_comments(comments):
    with open("comments.json", "w") as f:
        json.dump(comments, f, indent=2)


# Load articles
def load_articles():
    try:
        with open("articles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading articles:", e)
        return []


# Save articles
def save_articles(articles):
    try:
        with open("articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2)
    except Exception as e:
        print("Error saving articles:", e)


@app.route("/", methods=["GET"])
@protect_route
def index():
    filtered_articles = articles_store
    query = request.args.get("q")
    category = request.args.get("category")
    language = session.get("language", "en")
    articles = load_articles()
    breaking_news = [a for a in articles if a.get("is_breaking") == True]


    if query:
        filtered_articles = [
            a for a in articles_store if query.lower() in a["title"].lower()
        ]
    elif category:
        filtered_articles = [
            a for a in articles_store if category.lower() in a["title"].lower()
        ]

    translated = []
    for article in filtered_articles:
        translated.append({
            "id": article["id"],
            "title": translate_text(article["title"], language),
            "content": translate_text((article.get("content") or "")[:200], language),
            "image": article["image"]
        })

        braking_news = load_breaking_news()

    trending_ids = [item[0] for item in views.most_common(5)]
    trending_articles = [a for a in articles_store if str(a["id"]) in trending_ids]

    return render_template("index.html",
                           articles=translated,
                           raw_articles=articles,
                                categories=CATEGORIES,
                                current_year=datetime.datetime.now().year,
                                breaking_news=breaking_news)
                                
@app.route("/comment/<id>", methods=["POST"])
def comment(id):
    name = request.form["name"]
    text = request.form["text"]
    comments = load_comments()
    if id not in comments:
        comments[id] = []
    comments[id].append({"name": name, "text": text})
    save_comments(comments)
    return redirect(f"/article_raw/{id}")


@app.route("/article/<int:id>")
@protect_route
def article(id):
    views[id] += 1
    article = get_article_by_id(articles_store, id)

    # ✅ Protect against string errors
    if not article or not isinstance(article, dict):
        return "Invalid or missing article", 404

    # ✅ Set default image if missing
    if not article.get("image") or article["image"].strip() == "":
        article["image"] = "/static/images/default.jpg"

    # ✅ Translate content
    language = session.get("language", "en")
    translated_title = translate_text(article["title"], language)
    translated_content = translate_text(article["content"], language)
    audio_path = generate_voice(translated_content, id)
    tags = request.form.get("tags", "")

    print("LENGTH:", len(article["content"]))

    return render_template("article.html", article={
        "title": translated_title,
        "content": translated_content,
        "image": article["image"],
        "audio_path": audio_path,
        "tags": [t.strip() for t in tags.split(",") if t]
    }, current_year=datetime.datetime.now().year)

@app.route("/set_language", methods=["POST"])
@protect_route
def set_language():
    session["language"] = request.form.get("language", "en")
    return redirect(url_for("index"))


@app.route('/article_raw/<article_id>')
@protect_route
def show_article(article_id):
    views[id] += 1
    with open("articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    # Find article by string ID
    article = next((a for a in articles if a["id"] == article_id), None)
    tags = request.form.get("tags", "")
    if not article:
        return "Article not found", 404
    audio_path = generate_voice(article["content"], article["id"])
    article["audio_path"] = audio_path


    return render_template("article1.html", article=article)


@app.route('/admin', methods=['GET', 'POST'])
@protect_route
def admin():
    if request.method == 'POST':
        # Check for login first
        if not session.get("is_admin"):
            password = request.form.get("password")
            if password == app.config['ADMIN_PASSWORD']:
                session["is_admin"] = True
                return render_template("admin.html", show_form=True)
            else:
                return render_template("admin.html", error="Wrong password", show_form=False)

        if request.form.get("action") == "breaking":
            text = request.form.get("breaking_text")
            breaking = load_breaking_news()
            breaking.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "timestamp": str(datetime.datetime.now())
            })
            save_breaking_news(breaking)
            return redirect(url_for("admin"))

        # Admin is logged in — post article
        title = request.form.get("title")
        content = request.form.get("content")
        image_url = request.form.get("image_url")
        tags = request.form.get("tags", "")
        video = request.form.get("video")
        article["video"] = video

        new_article = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "image": image_url,
            "video": video,
            "tags": [t.strip() for t in tags.split(",") if t],

        }

        try:
            with open("articles.json", "r", encoding="utf-8") as f:
                articles = json.load(f)
        except:
            articles = []

        articles.append(new_article)

        with open("articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2)

        return redirect(url_for('index'))

    # GET request
    return render_template("admin.html", show_form=session.get("is_admin", False))


@app.route("/subscribe", methods=["POST"])
@protect_route
def subscribe():
    email = request.form.get("email")
    if email and email not in subscribers:
        subscribers.append(email)
        print("Subscribed:", email)
    return redirect("/")


def send_headlines_email(articles):
    if not subscribers:
        return

    body = ""
    for article in articles[:5]:
        body += f"- {article['title']}\nhttp://127.0.0.1:5000/article/{article['id']}\n\n"

    msg = Message("Your IndocNow Headlines",
                  sender="indocnow@gmail.com",
                  recipients=subscribers,
                  body=body)

    try:
        mail.send(msg)
        print("Headline email sent.")
    except Exception as e:
        print("Mail Error:", e)


@app.route("/about")
@protect_route
def about():
    return render_template("about.html", current_year=datetime.datetime.now().year)

@app.route('/static/<path:filename>')
@protect_route
def custom_static(filename):
    response = make_response(send_from_directory('static', filename))
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
    return response


@app.route("/live")
@protect_route
def live():
    matches = [
        {"team1": "Man City", "team2": "Wydad Casablanca", "date": "June 18, 2025", "time": "Local evening ",
         "location": "venue TBD (US)"},
        {"team1": "Rwanda", "team2": "Benin", "date": "Oct 6, 2025", "time": "9:00  CAT",
         "location": "kigali pele stadium"},
        {"team1": "Man City", "team2": "Al Ain ", "date": "June 23, 2025", "time": "",
         "location": "US stadium to be confirmed "},
        {"team1": "Man City", "team2": "Juventus", "date": ", 2025", "time": "",
         "location": ""}, {"team1": "Chelsea", "team2": "ES Tunis", "date": "June 30, 2025", "time": "9:30 AM",
         "location": "TBD (USA)"},
        {"team1": "Manchester City", "team2": "Juventus", "date": "July , 2025", "time": "9:30 AM",
         "location": "TBD (USA)"},
        {"team1": "England", "team2": "France(Women's EURO)", "date": "July 5, 2025", "time": "",
         "location": "king Power Stadium, Leicester"},
        {"team1": "PSG", "team2": "Tottenham", "date": "Aug 13, 2025", "time": "9:30 AM",
         "location": "Stadoi Friuli, Udine"},
        {"team1": "Crystal Palace", "team2": "Liverpool", "date": "Aug 10, 2025", "time": "9:30 AM",
         "location": "Wembley Stadium, Londan"},
        {"team1": "Sevilla", "team2": "Birmingham City", "date": "July 12, 2025", "time": "9:30 AM",
         "location": "Algrve Stadium, Portugal"},
        {"team1": "Arsenal", "team2": "Tottenham Hotspur", "date": "July 31, 2025", "time": "9:30 AM",
         "location": "Kai Tak Sports Park, Hong Kong"},
        {"team1": "Arsenal", "team2": "AC Milan", "date": "July 23, 2025", "time": "9:30 AM",
         "location": "National Stadium, Singapore"},
        {"team1": "Bayern Munich", "team2": "SL Benfica", "date": "June 24, 2025", "time": "TBD ",
         "location": "Bank of America Stadium"},
        {"team1": "Mexico", "team2": "US contenders", "date": "July 6, 2025", "time": "time TBD ",
         "location": "NRG Stadium, Houston, TX"},
        {"team1": "Chiefs", "team2": "Chargers", "date": "Sept 5, 2025", "time": "PM ET ",
         "location": "Corinthians Arena, São Paulo, Brazi"},
        {"team1": "Vikings", "team2": "Steelers", "date": "Sept 28, 2025", "time": "9:30 AM ET ",
         "location": "Croke Park, Dublin, Ireland"},
        {"team1": "Browns", "team2": "Vikings", "date": "Oct 5, 2025", "time": "9:30 AM ET ",
         "location": "Tottenham Hotspur Stadium"},
        {"team1": "Broncos", "team2": "Jets", "date": "Oct 12, 2025", "time": "9:30 AM ET ",
         "location": "Tottenham Hotspur Stadium"},
        {"team1": "Rams", "team2": "Jaguars", "date": "Oct 19, 2025", "time": "9:30 AM ET ",
         "location": "Wembley Stadium, London"},
        {"team1": "Falcons", "team2": "Colts", "date": "Nov 9, 2025", "time": "9:30 AM ET ",
         "location": "Olympic Stadium, Berlin"},
        {"team1": "Commanders", "team2": "Dolphins", "date": "Nov 16, 2025", "time": "9:30 AM ET ",
         "location": "Santiago Bernabéu Stadium, Madrid"},

        {"team1": "Rwanda", "team2": "South Africa", "date": "Oct 13, 2025", "time": "9:00 AM CAT",
         "location": "unknown"},
        {"team1": "Nigeria", "team2": "Rwanda", "date": "Sept 1, 2025", "time": "9:00 AM CAT",
         "location": ""},
    ]
    return render_template("live.html", matches=matches)


@app.route("/events")
@protect_route
def events():
    return render_template("events.html", current_year=datetime.datetime.now().year)

@app.route('/OneSignalSDKWorker.js')
def onesignal_worker():
    return send_from_directory('.', 'OneSignalSDKWorker.js')

@app.route('/OneSignalSDKUpdaterWorker.js')
def onesignal_updater_worker():
    return send_from_directory('.', 'OneSignalSDKUpdaterWorker.js')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')


@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


