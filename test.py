from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta, datetime

app = Flask(__name__)
# To encrypt and decrypt sessions data
app.config['SECRET_KEY'] = 'sessions'
# Store session data for 1 day, then log out
app.permanent_session_lifetime = timedelta(days=1)

 
connection = sqlite3.connect('data.db')
db = connection.cursor()
 
db.execute("SELECT * FROM tasks WHERE creator_id = 4 OR executor_id = 4")
rows = db.fetchall()

for row in rows:
    print(row)
print(rows)