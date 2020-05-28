import os
import requests, json

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

DATABASE_URL = """postgres://zymwknwojzdrxt:6b4a824b4c7e4f0f3e7db6f0939d4d75e206845a0ce6d1c7d87621e35635a226@ec2-35-173-94-156.compute-1.amazonaws.com:5432/d3qnplhrdgtkp0"""

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    title = "Home"
    return render_template("index.html", title=title)

@app.route("/search")
def search():
    books = db.execute("SELECT * FROM books").fetchall()
    title = "Search"
    return render_template("search.html", title=title, books=books)


@app.route("/search/bookpage/<isbn>", methods=['GET'])
def book(isbn):
    book = db.execute("SELECT title, isbn FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
    db.commit()
    KEY = "Tpre1YWnXuIint1k5r4HUAß"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    if res.status_code != 200:
        raise Exception ("Error api unsuccessful.")
    data = res.json()
    num_rating = data["books"][0]
    rating = data["books"][0]
    return render_template("bookpage.html", num_rating=num_rating, rating=rating, book=book)

if __name__ == "__main__":
    app.run(debug=True)
