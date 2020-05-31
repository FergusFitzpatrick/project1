import os
import requests, json
import bcrypt

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

@app.route("/signup")
def signup():
    title = "Sign Up"
    return render_template("signup.html", title=title)

@app.route("/logIn", methods=['GET','POST'])
def signingUp():
    title = "Log In"
    if request.method == 'GET':
        return render_template("login.html", title=title)

    #get the request form variable
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = bcrypt.hashpw(request.form.get('password'), bcrypt.gensalt())

    if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("signup.html", message="Username already exists!")

    db.execute("INSERT INTO users (firstname, lastname, username, email, password) VALUES (:firstname, :lastname, :username, :email, :password)",{"firstname": firstname, "lastname": lastname, "username": username, "email": email, "password": password})
    db.commit()
    if db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).rowcount == 0:
        return render_template("login.html", message="Successfully signed up!")
    else:
        return render_template("error.html", message="error signing up.")

@app.route("/searchPage", methods=['POST','GET'])
def loggingin():
    title = "Search"
    #get request form variables
    username = request.form.get('username')
    if db.execute("SELECT username FROM users WHERE username = :username",{"username": username}).rowcount == 0:
        return render_template("login.html", message="invalid username, please try again.")
    hashed_password = db.execute("SELECT username, password FROM users WHERE username = :username",{"username": username}).fetchone()['password']
    if bcrypt.checkpw(request.form.get('password'), hashed_password):
        return render_template("searchPage.html", title=title)
    else:
        return render_template("login.html", message="Incorrect Password.")


@app.route("/search", methods=['POST','GET'])
def search():
    title = "Search"
    searchQuery = str(request.form.get('searchquery') or 0)
    query = '%' + searchQuery + '%'
    if db.execute("SELECT title, isbn, author, year FROM books WHERE title ILIKE :query OR isbn ILIKE :query OR author ILIKE :query", {"query": query}).rowcount == 0:
        return render_template("error.html", message="Invalid serach query, no such book.")
    books = db.execute("SELECT * FROM books WHERE title ILIKE :query OR isbn ILIKE :query OR author ILIKE :query ORDER BY year ASC LIMIT 20", {"query": query}).fetchall()
    return render_template("search.html", title=title, books=books, searchQuery=searchQuery)


@app.route("/search/bookpage/<isbn>", methods=['GET'])
def book(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
    db.commit()
    KEY = "Tpre1YWnXuIint1k5r4HUAß"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    if res.status_code != 200:
        raise Exception ("Error api unsuccessful.")
    data = res.json()
    num_rating = data["books"][0]["work_ratings_count"]
    rating = data["books"][0]["average_rating"]
    return render_template("bookpage.html", num_rating=num_rating, rating=rating, book=book)

if __name__ == "__main__":
    app.run(debug=True)
