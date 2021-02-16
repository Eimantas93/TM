from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

connection = sqlite3.connect('data.db')
con = connection.cursor()


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    con.execute("INSERT INTO users (name, hash) VALUES(?, ?)",
                (username, password))

    connection.commit()
    connection.close()
    return render_template("test.html", username=username, password=password)
