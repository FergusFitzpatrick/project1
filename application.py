import os

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

DATABASE_URL = "postgres://joqityswncejjo:ce560d2222c9edcc16f30e8f95c840a7d8348c8bef7ca3b351ecdb32c63e3f48@ec2-54-86-170-8.compute-1.amazonaws.com:5432/d7s7d50npqadm9"

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
