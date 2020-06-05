import os
import requests, json
import bcrypt

from flask import Flask, session, request, render_template, url_for, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import flash
from datetime import datetime
from loginRequired import *

app = Flask(__name__)

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

today = datetime.now()

#Home page
@app.route("/")
def index():
    title = "Home"
    today = datetime.now()
    return render_template("index.html", title=title, today=today)

#Sign Up page sends user to logging in page
@app.route("/signup")
def signup():
    today = datetime.now()
    title = "Sign Up"
    return render_template("signup.html", title=title, today=today)

#Signing up page where either successful signing up and sends user to log in OR unsuccessful and user must try again.
@app.route("/loggingIn", methods=['GET','POST'])
def login():
    today = datetime.now()
    title = "Log In"
    if request.method == 'GET':
        return render_template("login.html", title=title, today=today)




    if not request.form.get('username'):
        flash("Please complete all fields")
        return render_template("signup.html", today=today)

    elif not request.form.get('password'):
        flash("Please enter a password")
        return render_template("signup.html", today=today)

    elif not request.form.get('firstname'):
        flash("Please complete all fields")
        return render_template("signup.html", today=today)

    elif not request.form.get('lastname'):
        flash("Please complete all fields")
        return render_template("signup.html", today=today)

    elif not request.form.get('email'):
        flash("Please complete all fields")
        return render_template("signup.html", today=today)

    elif not request.form.get('password2'):
        flash("Please complete all fields")
        return render_template("signup.html", today=today)

    #get the request form variable
    username = request.form.get('username')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')

    #Ensures password is correct
    if not request.form.get('password') == request.form.get('password2'):
        flash("Passwords do not match")
        return render_template("signup.html", today=today)

    #hash and salt password
    password = bcrypt.hashpw(request.form.get('password'), bcrypt.gensalt())

    #Check if username exists
    if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        flash("Username already exists")
        return render_template("signup.html", today=today)

    #Insert users data into table
    db.execute("INSERT INTO users (firstname, lastname, username, email, password) VALUES (:firstname, :lastname, :username, :email, :password)",{"firstname": firstname, "lastname": lastname, "username": username, "email": email, "password": password})
    db.commit()

    #Check to make sure it has been inserted and direct to log in area
    if db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).rowcount != 0:
        flash("Account Created!")
        return render_template("login.html", today=today)
    else:
        flash("Error signing up. Please try again.")
        return render_template("signup.html", today=today)

#sends user to search page when Successfully logged in OR sends user back to log in again.
@app.route("/searchPage", methods=['POST','GET'])
def loggingin():
    title = "Search"
    today = datetime.now()

    #get request form variables
    username = request.form.get('username')
    if db.execute("SELECT username FROM users WHERE username = :username",{"username": username}).rowcount == 0:
        flash("Invalid username, please try again.")
        return render_template("login.html", today=today)

    hashed_password = db.execute("SELECT username, password FROM users WHERE username = :username",{"username": username}).fetchone()['password']
    if bcrypt.checkpw(request.form.get('password'), hashed_password):
        result = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        session['user_id'] = result[0]
        session['username'] = result[3]
        session['logged_in'] = True
        return render_template("searchPage.html", title=title, username=session['username'], today=today)
    else:
        flash("Incorrect Password.")
        return render_template("login.html", today=today)


#Search page where user can perform a search
@app.route("/search", methods=['POST','GET'])
@login_required
def search():
    title = "Search"
    today = datetime.now()
    searchQuery = str(request.form.get('searchquery') or 0)
    query = '%' + searchQuery + '%'
    if db.execute("SELECT title, isbn, author, year FROM books WHERE title ILIKE :query OR isbn ILIKE :query OR author ILIKE :query", {"query": query}).rowcount == 0:
        return render_template("error.html", message="Invalid serach query, no such book.", today=today)
    books = db.execute("SELECT * FROM books WHERE title ILIKE :query OR isbn ILIKE :query OR author ILIKE :query ORDER BY year ASC LIMIT 20", {"query": query}).fetchall()
    return render_template("search.html", title=title, books=books, searchQuery=searchQuery, today=today)

#Shows the results of the search and links to the bookpage
@app.route("/search/bookpage/<isbn>", methods=['GET'])
@login_required
def book(isbn):

    today = datetime.now()
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
    db.commit()
    session['book_id'] = book[0]

    KEY = "Tpre1YWnXuIint1k5r4HUAß"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn}, verify = False)
    if res.status_code != 200:
        raise Exception ("Error api unsuccessful.")
    data = res.json()
    num_rating = data["books"][0]["work_ratings_count"]
    rating = data["books"][0]["average_rating"]

    bookR = session['book_id']
    results = db.execute("SELECT users.username, review, rating FROM users INNER JOIN reviews ON users.id = reviews.user_id WHERE books_id = :bookR", {"bookR": bookR})
    reviews = results.fetchall()

    return render_template("bookpage.html", num_rating=num_rating, rating=rating, book=book, reviews=reviews, bookR=bookR, today=today)

@app.route("/review", methods=['POST','GET'])
@login_required
def reviewing():
    today = datetime.now()
    username = session['username']
    rating = request.form.get('rating')
    review = request.form.get('review')
    bookid = session['book_id']
    userid = session['user_id']

    isbn = db.execute("SELECT isbn FROM books WHERE id = :bookid", {"bookid": bookid}).fetchone()['isbn']

    results = db.execute("SELECT user_id, books_id FROM reviews WHERE user_id = :userid AND books_id = :bookid", {"userid": userid, "bookid": bookid})

    if results.rowcount != 0:
        return redirect(url_for('book', isbn=isbn, today=today))
    else:
        db.execute("INSERT INTO reviews (review, books_id, user_id, rating) VALUES (:review, :bookid, :userid, :rating)", {"review": review, "bookid": bookid, "userid": userid, "rating": rating})
        db.commit()
        return redirect(url_for('book', isbn=isbn, today=today))

#logs users out. clears sesssion data and sends user back to home page.
@app.route("/logout")
@login_required
def logout():
    today = datetime.now()
    session.clear()
    flash("You have logged out.")
    return render_template("login.html", today=today)

@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
    if book is None:
          return jsonify({"error": "Invalid book isbn"}), 404

    KEY = "Tpre1YWnXuIint1k5r4HUAß"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn}, verify = False)
    if res.status_code != 200:
        raise Exception ("Error api unsuccessful.")
    data = res.json()
    num_rating = data["books"][0]["work_ratings_count"]
    rating = data["books"][0]["average_rating"]

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": num_rating,
        "average_score": rating
    })


if __name__ == "__main__":
    app.run(debug=True)
