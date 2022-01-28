import requests
from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup
from googlesearch import search
class Lyricspedia:
    def __init__(self, title: str):
        anu = search('site:animesonglyrics.com {}'.format(title), num_results=0)
        abu = ''.join(anu)
        try:
            url = requests.get(abu)
        except MissingSchema:
            pass
            error = 'No Results Found'
            raise MissingSchema(error)
        
        soup = BeautifulSoup(url.content, 'html.parser')
        for a in soup.findAll("br"):
            a.replace_with("\n")
        try:
            lyrics_romaji = soup.find('div', {'id': 'tab1'}).text
        except AttributeError:
            raise AttributeError('Can\' find a anime song')
        lyrics_romaji0 = lyrics_romaji.split('[')[0]
        lyrics_romaji1 = lyrics_romaji.split('[')[1]
        lyrics_romaji = '  {} [{}'.format(lyrics_romaji0, lyrics_romaji1)
        lyrics_romaji = lyrics_romaji.replace('                                                            ', '')
        self.lyrics_romaji = lyrics_romaji or None
        try:
            lyrics_en = soup.find('div', {'id': 'tab2'}).text
        except AttributeError:
            raise AttributeError('Can\' find a anime song')
        lyrics_en0 = lyrics_en.split('[')[0]
        lyrics_en1 = lyrics_en.split('[')[1]
        lyrics_en = ' {} [{}'.format(lyrics_en0, lyrics_en1)
        self.lyrics_en = lyrics_en or None
        name = soup.find('div', {'id': 'wrapper'})
        name = name.h1.text
        name = name.replace('                ','')
        self.name = name