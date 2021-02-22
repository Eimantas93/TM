from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta, datetime

app = Flask(__name__)
# To encrypt and decrypt sessions data
app.config['SECRET_KEY'] = 'sessions'
# Store session data for 1 day, then log out
app.permanent_session_lifetime = timedelta(days=1)


@app.route("/")
def index():
    if session.get("user_id") is None:
        return redirect("/login")
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        # Getting data from tasks table, for current user (as creator and executor)
        db.execute("SELECT * FROM tasks WHERE executor_id = ? OR creator_id = ?",
                   (session["user_id"], session["user_id"],))
        rows = db.fetchall()
        # Passing all values to jinja
        return render_template("index.html", rows=rows)


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
        company = request.form.get("company")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if password != password2:
            return "error"

        # Hashing password
        hashed_password = generate_password_hash(password)

        # Registering user to DB
        connection.execute("INSERT INTO users (name, hash, position, company) VALUES(?, ?, ?, ?)",
                           (username, hashed_password, position, company))

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


@app.route("/new_task", methods=["GET", "POST"])
def new_task():
    if request.method == "GET":
        return render_template("new_task.html")
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        # Getting values from user
        executor = request.form.get("task_for")
        heading = request.form.get("heading")
        description = request.form.get("description")
        deadline = request.form.get("deadline")
        status = 0

        # Storing user task into db table
        db.execute("INSERT INTO tasks(creator_id, executor_id, heading, description, deadline_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (session["user_id"], executor, heading, description, deadline, status))
        connection.commit()
        connection.close()

        # Redirecting to index, where all tasks will be shown (recent created ones first)
        return redirect("/")


@app.route("/tasks", methods=["GET"])
def tasks():
    return render_template("tasks.html")


@app.route("/edit_task", methods=["GET", "POST"])
def edit_task():
    if request.method == "GET":
        return render_template("edit_task.html")


@app.route("/unassign", methods=["GET"])
def unassign():
    selected_supervisors_id = request.form.get("new_supervisor")
    selected_subordinates_id = request.form.get("new_subordinate")

    # Connecting to DB
    connection = sqlite3.connect('data.db')
    db = connection.cursor()

    connection.execute(
        "DELETE FROM relations WHERE supervisors_id = ? AND subordinates_id = ?", (selected_supervisors_id, selected_subordinates_id))

    return redirect(url_for("relations"))


@app.route("/relations", methods=["GET", "POST"])
def relations():
    if request.method == "GET":
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        # Get current user session id
        db.execute(
            "SELECT * FROM users WHERE user_id = ?", (session["user_id"],))
        user_row = db.fetchone()

        # Get current user company
        db.execute("SELECT * FROM users WHERE company = ?", (user_row[4],))
        rows = db.fetchall()

        # Get current user company
        db.execute("SELECT * FROM relations")
        relations = db.fetchall()

        db.execute(
            "SELECT users.user_id, users.name, users.position, users.company, relations.supervisors_id, relations.subordinates_id FROM users INNER JOIN relations ON users.user_id = relations.user_id")
        joined_rows = db.fetchall()

        return render_template("relations.html", rows=rows, relations=relations, joined_rows=joined_rows)
    else:
        selected_supervisors_id = request.form.get("new_supervisor")
        selected_subordinates_id = request.form.get("new_subordinate")

        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        connection.execute("INSERT INTO relations (user_id, subordinates_id) VALUES (?, ?)",
                           (selected_supervisors_id, selected_subordinates_id))

        connection.execute("INSERT INTO relations (user_id, supervisors_id) VALUES (?, ?)",
                           (selected_subordinates_id, selected_supervisors_id))

        connection.commit()
        connection.close()

        return redirect(url_for("relations"))
