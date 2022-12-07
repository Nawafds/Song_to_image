import lyricsgenius

token = '6hIJ54nrVtypqwWkecZ2di-rpa2bMBMhVMbgTpJn6XFL0pqbuRlMw8knuT6_iZXs'
genius = lyricsgenius.Genius(token)



song= genius.search_song("havasdfsdfsdfadsfna")
print(song)