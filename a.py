from BeautifulSoup import BeautifulSoup


soup = BeautifulSoup("lyrics_search.html")
for link in soup.findAll('a'):
    link['src'] = 'New src'
    html_string = str(soup)