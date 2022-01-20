import requests
from bs4 import BeautifulSoup

def crawl(url, tag='html', attr:dict=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text)
    entities = soup.find_all(tag)

    if isinstance(attr, dict):
        entities = soup.find(tag, attr)
    return entities
