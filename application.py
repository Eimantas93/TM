from flask import Flask, render_template, request
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("test.html")


@app.route("/register", methods=["POST"])
def register():

    connection = sqlite3.connect('data.db')
    username = request.form.get("username")
    password = request.form.get("password")

    hashed_password = generate_password_hash(password)

    connection.execute("INSERT INTO users (name, hash) VALUES(?, ?)",
                       (username, hashed_password))
    connection.commit()
    connection.close()

    return render_template("layout.html")
