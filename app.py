from flask import Flask, render_template, request, redirect, url_for, session
from fetch_news import fetch_all_articles, get_article_by_id
from voice_reader import generate_voice
from translator import translate_text
import datetime
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = "indocnow-secret-key"

# Email configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='indocnow@gmail.com',
    MAIL_PASSWORD='indocnow@123'  # Use an app password from Gmail
)
mail = Mail(app)
subscribers = []

# Cached articles
articles_store = fetch_all_articles()

# Categories to list
CATEGORIES = [
    "technology", "sports", "politics", "entertainment", "health", "business", "world", "education"
]


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q")
    category = request.args.get("category")
    language = session.get("language", "en")

    filtered_articles = articles_store

    if query:
        filtered_articles = [
            a for a in articles_store if query.lower() in a["title"].lower()
        ]
    elif category:
        filtered_articles = [
            a for a in articles_store if category.lower() in a["title"].lower()
        ]

    # Translate article titles and text
    translated = []
    for article in filtered_articles:
        translated.append({
            "id": article["id"],
            "title": translate_text(article["title"], language),
            "content": translate_text(article["content"][:200], language),
            "image": article["image"]
        })

    return render_template("index.html",
                           articles=translated,
                           categories=CATEGORIES,
                           current_year=datetime.datetime.now().year)


@app.route("/article/<int:id>")
def article(id):
    language = session.get("language", "en")
    article = get_article_by_id(articles_store, id)

    if not article:
        return "Article not found", 404

    translated_text = translate_text(article["content"], language)
    audio_path = generate_voice(translated_text, id)

    return render_template("article.html",
                           article={
                               "title": translate_text(article["title"], language),
                               "content": translated_text,
                               "image": article["image"],
                               "audio_path": audio_path
                           },
                           current_year=datetime.datetime.now().year)


@app.route("/set_language", methods=["POST"])
def set_language():
    session["language"] = request.form.get("language", "en")
    return redirect(url_for("index"))


@app.route("/subscribe", methods=["POST"])
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
                  sender="your_email@gmail.com",
                  recipients=subscribers,
                  body=body)

    try:
        mail.send(msg)
        print("Headline email sent.")
    except Exception as e:
        print("Mail Error:", e)


@app.route("/about")
def about():
    return render_template("about.html", current_year=datetime.datetime.now().year)



@app.route("/live")
def live():
    matches = [
        {"team1": "Algeria", "team2": "Rwanda", "date": "June 5, 2025", "time": "19:00 (Local time)", "location": "Stade Mohamed-Hamlaoui,Constantine,  Algeria"},
        {"team1": "Germany", "team2": "Portugal", "date": "June 4, 2025", "time": "15:00 CEST", "location": "Allianz Arena, Munich, Germany"},
        {"team1": "Spain", "team2": "France", "date": "June 4, 2025", "time": "15:00 CEST", "location": "MHPArena, Stuttgart, Germany"},
        {"team1": "Bayern Munich", "team2": "Auckland City", "date": "June 15, 2025", "time": "TBA", "location": "TBA"},
        {"team1": "AI Ahly(Egypt)", "team2": "Inter Miami", "date": "June 14, 2025", "time": "15:00", "location": "Kigali Stadium"},
        {"team1": "Ulsan HD", "team2": "Mamelodi", "date": "June 17, 2025", "time": "TBA", "location": "Caming World Stadium, Orlando"},
        {"team1": "Manchester City", "team2": "Wydad AC", "date": "June 18, 2025", "time": "TBA", "location": "Lincoln Financial Field, Philadelphia, Pennsylvania"},
        {"team1": "SL Benfica", "team2": "Auckland City FC", "date": "June 20, 2025", "time": "TBA", "location": "Caming World Stadium, Orlando, Florida"},

        # ... add more
    ]
    return render_template("live.html", matches=matches)

@app.route("/events")
def events():
    return render_template("events.html", current_year=datetime.datetime.now().year)


if __name__ == "__main__":
    app.run(debug=True)