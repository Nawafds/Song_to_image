from flask import Flask, request, render_template
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


def Lyrics(song):
    artist = ""
    url = f"http://api.musixmatch.com/ws/1.1/track.search?q_artist={artist}&page_size=1&page=1&s_track_rating=desc&apikey=b653a9863936de49ed3087828dcafe54&q_track={song}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    getTrackId = json.loads(response.text)

    if(int(getTrackId["message"]["header"]["available"])== 0):
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
    # NB: host url is not prepended with \"https\" nor does it have a trailing slash.
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

    # To get your API key, visit https://beta.dreamstudio.ai/membership
    os.environ['STABILITY_KEY'] = 'sk-ZW2FwVJtzNT6wlBdQEw7vAcpVLHXXzwgIeGwA3A5aaOvvUt1'

    stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,)


    # the object returned is a python generator
    answers = stability_api.generate(
    prompt= keyWords,
    seed=34567, # if provided, specifying a random seed makes results deterministic
    steps=30,) # defaults to 50 if not specified

    #iterating over the generator produces the api response
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                data = Image.open(io.BytesIO(artifact.binary))
                data = data.save("photos/" + name + ".png")


app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])

def home():
    if request.method == 'POST':
        name = request.form.get('name')

        song_lyrics = Lyrics(name)

        getImg(song_lyrics, name)


        im = Image.open("photos/" + name + ".png")
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())

        return render_template("lyrics_search.html",variable = f"{song_lyrics}", img_data=encoded_img_data.decode('utf-8'), song_name = name )
    return render_template("lyrics_search.html")

if __name__ == "__main__":
    app.run(debug=True)


