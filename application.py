from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

app = Flask(__name__)
# To encrypt and decrypt sessions data
app.config['SECRET_KEY'] = 'sessions'
# Store session data for 1 day, then log out
app.permanent_session_lifetime = timedelta(days=1)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        # Getting username and password from registration form
        username = request.form.get("username")
        position = request.form.get("position")
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
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        # Getting username and password from login form
        username = request.form.get("username")
        password = request.form.get("password")

        # Query user data
        db.execute("SELECT * FROM users WHERE name = ?", (username,))
        # fetchone() Fetches the next row of a query result set, returning a single sequence, or None when no more data is available.
        row = db.fetchone()
        # Checking for user
        if not row:
            return render_template("login.html")
        # Checking password
        if not check_password_hash(row[2], password) or not row:
            return render_template("login.html")
        # Setting session user ID
        session["user_id"] = row[0]

        return render_template("index.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    return redirect("/")


@app.route("/new_task", methods=["GET"])
def new_task():
    if request.method == "GET":
        return render_template("new_task.html")


@app.route("/edit_task", methods=["GET", "POST"])
def edit_task():
    if request.method == "GET":
        return render_template("edit_task.html")


@app.route("/relations", methods=["GET", "POST"])
def relations():
    if request.method == "GET":
        return render_template("relations.html")
    else:
        """
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        # Getting username and password from login form
        supervisor = request.form.get("supervisor")

        # Query user data
        db.execute("SELECT * FROM users WHERE name = ?", (supervisor,))

        # fetchone() Fetches the next row of a query result set, returning a single sequence, or None when no more data is available.
        row = db.fetchone()
        supervisors_id = int(row[0])

        # Update supervisor in relations table
        connection.execute("INSERT INTO relations (user_id, supervisors_id) VALUES (?, ?)",
                           (session["user_id"], supervisors_id))

        db.execute("SELECT * FROM relations WHERE user_id = ?",
                   (supervisors_id,))

        supervisors_row = db.fetchone()

        if not supervisors_row:
            connection.execute(
                "INSERT INTO relations (user_id, subordinates_id) VALUES (?, ?)", (supervisors_id, session["user_id"]))

        connection.commit()
        connection.close()
        return render_template("index.html")
        """
