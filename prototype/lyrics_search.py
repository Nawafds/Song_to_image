from flask import Flask, request, render_template
import json
import requests

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

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST']
)
def home():
    if request.method == 'POST':
        name = request.form.get('name')

        return render_template("lyrics_search.html",variable= f"{Lyrics(name)}")
    return render_template("lyrics_search.html")

if __name__ == "__main__":
    app.run(debug=True)





