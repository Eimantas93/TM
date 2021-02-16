from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('example.db')


@app.route("/")
def hello():
    return "Hello, World!"
