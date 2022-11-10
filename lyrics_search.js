

const form = document.getElementById("form");
const artist = document.getElementById("artist");
const song = document.getElementById("song");
const result = document.getElementById("result");


const apiLink = "https://private-anon-42f26ad9a7-lyricsovh.apiary-mock.com";

form.addEventListener('submit', e =>{
    e.preventDefault();
    searchArtist = artist.value.trim();
    searchSong = song.value.trim();
    console.log(searchArtist);
    console.log(searchSong);
    
    if(!searchArtist || !searchSong){
        alert("Error empty search.")
        
    }
    else{
        query(searchArtist,searchSong);
    }


});


async function query(artist, song){
    var requestOptions = {
        method: 'GET',
        redirect: 'follow'
      };
      
      fetch("http://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id=142504979\n&apikey=b653a9863936de49ed3087828dcafe54&q_track=havana", requestOptions)
        .then(response => response.text())
        .then(result => console.log(result))
        .catch(error => console.log('error', error));
}


