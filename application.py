from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta, datetime

app = Flask(__name__)
# To encrypt and decrypt sessions data
app.config['SECRET_KEY'] = 'sessions'
# Store session data for 1 day, then log out
app.permanent_session_lifetime = timedelta(days=1)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if session.get("user_id") is None:
            return redirect("/login")
        else:
            # Connecting to DB
            connection = sqlite3.connect('data.db')
            db = connection.cursor()

            # Getting data from tasks table, for current user (as creator and executor)
            db.execute("SELECT * FROM tasks WHERE creator_id = ? OR executor_id = ? AND status = 0 ORDER BY creation_date DESC",
               (session["user_id"], session["user_id"]))
            rows = db.fetchall()

            db.execute("SELECT * FROM users")
            users = db.fetchall()
            # Passing all values to jinja
            return render_template("index.html", rows=rows, users=users)
    else:
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        task_id = request.form.get("task_id")

        # Get current task data
        db.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id))

        row = db.fetchone()

        creator_id = row[1]
        executor_id = row[2]
        heading = row[3]
        description = row[4]
        creation_date = row[5]
        deadline = row[6]
        status = row[7]

        db.execute("SELECT name FROM users WHERE user_id = ?", (creator_id,))
        creatorList = db.fetchone()
        creator_name = creatorList[0]

        db.execute("SELECT name FROM users WHERE user_id = ?", (executor_id,))
        executorList = db.fetchone()
        executor_name = executorList[0]

        db.execute("SELECT note, user_name, creation_date FROM notes WHERE task_id = ? ORDER BY creation_date DESC", (task_id))
        notes = db.fetchall()

        # NEED TO FIX THIS
        return render_template("edit_task.html", task_id=task_id, creator_id=creator_id, executor_id=executor_id, heading=heading, description=description, creation_date=creation_date, deadline=deadline, status=status
        , creator_name=creator_name, executor_name=executor_name, notes=notes)


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

        return redirect("/")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    return redirect("/")


@app.route("/new_task", methods=["GET", "POST"])
def new_task():
    if request.method == "GET":

        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()
        user_id = session["user_id"]

        # Get current user session id
        db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_row = db.fetchone()

        # Get current user company data
        db.execute("SELECT * FROM users WHERE company = ?", (user_row[4],))
        rows = db.fetchall()

        # Get all relations data
        db.execute("SELECT * FROM relations")
        relations = db.fetchall()

        return render_template("new_task.html", relations=relations, rows=rows, user_id=user_id)
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
    # Connecting to DB
    connection = sqlite3.connect('data.db')
    db = connection.cursor()

    # Get current user tasks history
    db.execute("SELECT * FROM tasks WHERE creator_id = ? OR executor_id = ? ORDER BY creation_date DESC",
               (session["user_id"], session["user_id"]))
    rows = db.fetchall()

    db.execute("SELECT * FROM users")
    users = db.fetchall()

    return render_template("tasks.html", rows=rows, users=users)


@app.route("/edit_task", methods=["POST"])
def edit_task():
    if request.method == "POST":
        heading = request.form.get("heading")
        description = request.form.get("description")
        deadline = request.form.get("deadline")
        status = request.form.get("status")
        task_id = request.form.get("task_id")
        # Connecting to DB
        connection = sqlite3.connect('data.db')
        db = connection.cursor()

        # Updare current task
        db.execute("UPDATE tasks SET heading = (?), description = (?), deadline_date = (?), status = (?) WHERE id = ?"
        , (heading, description, deadline, status, task_id))
        connection.commit()
        connection.close()

        # Kaip grysti i ta pacia task bet jau updatinta?
        return render_template("edit_task.html")

@app.route("/add_note", methods=["POST"])
def add_note():
    note = request.form.get("note")
    task_id = request.form.get("task_id")
    # Connecting to DB
    connection = sqlite3.connect('data.db')
    db = connection.cursor()

    db.execute("SELECT name FROM users WHERE user_id = ?", (session["user_id"],))
    listName = db.fetchone()
    name = listName[0]

    # Add note to table
    db.execute("INSERT INTO notes(task_id, note, user_name) VALUES (?, ?, ?)",
    (task_id, note, name))
    connection.commit()
    connection.close()
    # Kaip grysti i ta pacia task bet jau updatinta?
    return render_template("edit_task.html")


@app.route("/unassign", methods=["POST"])
def unassign():
    supervisors_id = request.form.get("selected_supervisors_id")
    subordinates_id = request.form.get("selected_subordinates_id")

    # Connecting to DB
    connection = sqlite3.connect('data.db')
    db = connection.cursor()

    connection.execute("DELETE FROM relations WHERE user_id = ? AND subordinates_id = ?",
                       (supervisors_id, subordinates_id))

    connection.execute("DELETE FROM relations WHERE user_id = ? AND supervisors_id = ?",
                       (subordinates_id, supervisors_id))

    connection.commit()
    connection.close()

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

        # Get current user company data
        db.execute("SELECT * FROM users WHERE company = ?", (user_row[4],))
        rows = db.fetchall()

        # Get all relations data
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
