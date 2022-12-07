from flask import Flask, request, render_template, redirect, session, url_for
import json
import requests
import getpass, os
import io
import base64
import warnings
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import mysql.connector
from mysql.connector import Error
import pathlib
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests as g
import lyricsgenius

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="SongToImgDB"
)

mycursor = mydb.cursor()

app = Flask(__name__)

# app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)
app.secret_key = "12345"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "940761290205-s8u2blg6v6vfhp7ipv2lv7qqu2n7eth6.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def Lyrics(song):
    token = '6hIJ54nrVtypqwWkecZ2di-rpa2bMBMhVMbgTpJn6XFL0pqbuRlMw8knuT6_iZXs'
    genius = lyricsgenius.Genius(token)

    try:
        song = genius.search_song(song)
        result = song.lyrics
        index = result.index('Lyrics')

        if song == None:
            return "No lyrics found"
        return song.lyrics[index + 6:1000]
    except:
        return "An error occured trying again"


def getImg(keyWords):
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_KEY'] = 'sk-D5RHAieHRtzjQoDP2eVY2RPLf3heqHJa85lQg66PxZyMSWCE'
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
                return "Error"
            if artifact.type == generation.ARTIFACT_IMAGE:
                return Image.open(io.BytesIO(artifact.binary))


@app.route('/img', methods=['GET', 'POST'])
def find_img():
    msg = ""
    if request.method == 'POST':

        name = request.form.get('name')
        song_lyrics = Lyrics(name)

        if song_lyrics == "No lyrics found" or song_lyrics == "An error occured trying again":
            return render_template("home.html", msg=f"{song_lyrics}", nolyrics="none")
        else:

            im = getImg(song_lyrics)
            if im == "Error":
                song_lyrics = "Explicit content filter activated try another song"
                return render_template("home.html", msg=f"{song_lyrics}", nolyrics="none")
            else:
                data = io.BytesIO()
                im.save(data, "JPEG")
                encoded_img_data = base64.b64encode(data.getvalue())
                mycursor.execute("INSERT INTO images (name,username,img) VALUES (%s,%s,%s)",
                                 (name, session['username'], encoded_img_data))
                mydb.commit()

                return render_template("home.html", msg=f"{song_lyrics}", img_data=encoded_img_data.decode('utf-8'),
                                       name=name, display="block")

    return render_template("home.html", display="none")


@app.route('/', methods=['GET', 'POST'])
def login():
    # return redirect(url_for("google.login"))
    msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        username = username.strip()
        password = request.form.get("password")

        mycursor.execute("SELECT * FROM Users WHERE Username = %s AND password = %s", (username, password))
        account = mycursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = username

            msg = 'Logged in successfully!'
            return redirect('/home')
        else:

            msg = 'Incorrect username/password!'
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
        mycursor.execute("SELECT * FROM Users WHERE Username = %s", (session["username"],))
        account = mycursor.fetchone()

        return render_template('profile.html', username=account[0], email=account[2])
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        mycursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        check_username = mycursor.fetchone()

        mycursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        check_email = mycursor.fetchone()

        if check_username:
            msg = 'Username already taken!'

        elif check_email:
            msg = 'Email already registered'
        else:
            mycursor.execute("INSERT INTO Users (Username, password, email) VALUES (%s,%s,%s)",
                             (username, password, email))
            mydb.commit()
            msg = 'Sign up successfully proceed to login'

    return render_template("signup.html", msg=msg)


@app.route('/library')
def library():
    mycursor.execute("SELECT img, name, id FROM images WHERE username = %s;", (session['username'],))
    records = mycursor.fetchall()
    result = []
    for i in range(len(records)):
        result.append([records[i], i])
    return render_template("library.html", data=result)


@app.route('/google')
def google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = g.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    email = id_info.get("email")
    username = email.split("@")[0]

    mycursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
    check_username = mycursor.fetchone()

    if check_username:
        session['loggedin'] = True
        session['username'] = username

        msg = 'Logged in successfully!'
        return redirect('/home')
    else:
        mycursor.execute("INSERT INTO Users (Username, password, email) VALUES (%s,%s,%s)",
                         (username, "signed in using google", email))
        mydb.commit()
        session['loggedin'] = True
        session['username'] = username

        msg = 'Logged in successfully!'
        return redirect('/home')


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        id = request.form.get('delete')
        mycursor.execute("DELETE FROM images WHERE id = %s;", (id,))
        mydb.commit()

    return redirect('/library')


def addUserImg(name, user_id, img):
    try:
        mycursor.execute("INSERT INTO images (name,username,img) VALUES (%s,%s,%s)", (id, name, user_id, img))
        mydb.commit()
        return "Insertion successfull"
    except mysql.connector.Error as err:
        return "Something went wrong: {}".format(err)


if __name__ == "__main__":
    app.run(debug=True)
