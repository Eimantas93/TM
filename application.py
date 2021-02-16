from flask import Flask, render_template, request
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET, POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        # Getting username and password from registration form
        username = request.form.get("username")
        position = request.form.get("position")
        supervisor = request.form.get("supervisor")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if password != password2:
            return "error"

        # Hashing password
        hashed_password = generate_password_hash(password)

        # Registering user to DB
        connection.execute("INSERT INTO users (name, hash, position) VALUES(?, ?, ?)",
                           (username, hashed_password, position))
        connection.commit()
        connection.close()
        # return render_template("index.html" ???session???)


@app.route("/login", methods=["GET, POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        # Getting username and password from login form
        username = request.form.get("username")
        password = request.form.get("password")

        # Searching for username in DB
        rows = connection.execute(
            "SELECT * FROM users WHERE name=(?)", username)
        # Checking password
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Error"
        # Here should be set session user ID
        # session["user_id"] = rows[0]["user_id"]
        return render_template("index.html")
