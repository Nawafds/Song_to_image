from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("l")

if __name__ == "__main__":
    app.run(debug=True)
