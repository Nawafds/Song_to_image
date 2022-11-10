import requests
import json

def Lyrics(artist, song):
    #
    url = f"http://api.musixmatch.com/ws/1.1/track.search?q_artist={artist}&page_size=1&page=1&s_track_rating=desc&apikey=b653a9863936de49ed3087828dcafe54&q_track={song}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    getTrackId = json.loads(response.text)
    getTrackId = int(getTrackId["message"]["body"]["track_list"][0]["track"]["track_id"])
    #


    #
    url = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={getTrackId}&apikey=b653a9863936de49ed3087828dcafe54"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    getLyrics = json.loads(response.text)
    getLyrics = getLyrics["message"]["body"]["lyrics"]["lyrics_body"]
    print(getLyrics)
    #



Lyrics("Harry Styles","As it was")