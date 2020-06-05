from functools import wraps
from flask import redirect,session, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            flash("You must be logged in to use this feature")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
