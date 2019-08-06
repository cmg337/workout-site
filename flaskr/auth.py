import functools
from cs50 import SQL
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

from flask import (
Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///flaskr/workout.db")

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""

    # forget user info
    session.clear()

    # return register page if get
    if request.method == "GET":
        return render_template("register.html", error=0)

    # register user if meets requirements
    elif request.method == "POST":
        email = request.form.get("email")
        firstname = request.form.get("first-name")
        lastname = request.form.get("last-name")
        password = request.form.get("password")

        # check if username exists
        if len(db.execute("SELECT * FROM users WHERE email = :email", email=email)) != 0:
            return render_template("register.html", error=1)

        # add user to database
        db.execute("INSERT INTO users (email, firstname, lastname, password) VALUES (:email, :firstname, :lastname, :password)",
                    email=email, password=generate_password_hash(password), firstname=firstname, lastname=lastname)

        # start session after registering
        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE email = :email", email=email)[0]["id"]
        user_id = str(session["user_id"])

        return redirect("/")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Log User In"""

    # forget user info
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                            email=request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("login.html", error=1)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", error=0)


@bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")