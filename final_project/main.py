from flask import Flask, request, render_template, redirect, session
import json
import requests
import getpass, os
import io
import base64
import io
import os
import warnings
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import mysql.connector
from mysql.connector import Error

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="SongToImgDB"
)

mycursor = mydb.cursor()


def Lyrics(song):
    artist = ""
    url = f"http://api.musixmatch.com/ws/1.1/track.search?q_artist={artist}&page_size=1&page=1&s_track_rating=desc&apikey=b653a9863936de49ed3087828dcafe54&q_track={song}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    getTrackId = json.loads(response.text)

    if (int(getTrackId["message"]["header"]["available"]) == 0):
        return "No lyrics found"

    getTrackId = int(getTrackId["message"]["body"]["track_list"][0]["track"]["track_id"])
    url = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={getTrackId}&apikey=b653a9863936de49ed3087828dcafe54"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    getLyrics = json.loads(response.text)

    if int(getLyrics["message"]["header"]["status_code"]) != 200:
        return "No lyrics found"

    getLyrics = getLyrics["message"]["body"]["lyrics"]["lyrics_body"]

    result = ""
    for i in getLyrics:
        if i == ".":
            result = result[0:len(result) - 1]
            result += "."
            break
        else:
            result += i
    return result


def getImg(keyWords, name):
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

    os.environ['STABILITY_KEY'] = 'sk-ZW2FwVJtzNT6wlBdQEw7vAcpVLHXXzwgIeGwA3A5aaOvvUt1'

    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'],
        verbose=True, )

    answers = stability_api.generate(
        prompt=keyWords,
        seed=34567,
        steps=30, )


    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                return Image.open(io.BytesIO(artifact.binary))


app = Flask(__name__)

app.secret_key = "12345678"


@app.route('/img', methods=['GET', 'POST'])
def find_img():
    if request.method == 'POST':

        name = request.form.get('name')

        song_lyrics = Lyrics(name)
        if song_lyrics == "No lyrics found":
            return render_template("lyrics_search.html", msg=f"{song_lyrics}")
        else:
            im = getImg(song_lyrics, name)
            data = io.BytesIO()
            im.save(data, "JPEG")
            encoded_img_data = base64.b64encode(data.getvalue())

            return render_template("home.html", msg=f"{song_lyrics}", img_data=encoded_img_data.decode('utf-8'))
    return render_template("home.html")


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        mycursor.execute("SELECT * FROM Users WHERE Username = %s AND password = %s", (username, password))
        account = mycursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = username
            session['password'] = password
            msg = 'Logged in successfully!'
            return redirect('/home')
        else:

            msg = 'Incorrect username/password!'

        print(username, password)
    return render_template('login.html', msg=msg)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect('/')


@app.route('/home')
def home():
    if 'loggedin' in session:
        return redirect('/img')
    return redirect("/login")


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        mycursor.execute("SELECT * FROM Users WHERE Username = %s AND password = %s", (session["username"], session['password']))
        account = mycursor.fetchone()
        print(account[0])

        return render_template('profile.html', username=account[0], password = account[1], email = account[2])
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        mycursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        account = mycursor.fetchone()
        if account:
            msg = 'Username already taken!'
        else:
            mycursor.execute("INSERT INTO Users (Username, password, email) VALUES (%s,%s,%s)", (username,password, email))
            mydb.commit()
            msg = 'Sign up successfully proceed to login'

    return render_template("signup.html",msg= msg)


if __name__ == "__main__":
    app.run(debug=True)
