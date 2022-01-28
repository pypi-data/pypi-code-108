import requests
from googlesearch import search
from bs4 import BeautifulSoup
from .error_handling import SearchNotWork, NoResultFound

class Charapedia:
  def __init__(self, char: str):
    
    try:
      mal_char_id = search('site:myanimelist.net {} character info inurl:/character/'.format(char), num_results=0)
    except SearchNotWork:
      raise SearchNotWork('Search Library Not Work')
    try:
      mal_char_id = ''.join(mal_char_id).split('/')[4]
    except:
      raise NoResultFound('Character Not Found')
    self.mal_char_id = mal_char_id
    base_api = 'https://api.jikan.moe/v3/character/{}/'.format(self.mal_char_id)
    r = requests.get(base_api)
    result = r.json()
    self.result = result
    
    #Caharcter Name
    try:
      name = result['name']
      name = f'{name} ({result["name_kanji"]})'
    except KeyError:
      raise NoResultFound(f'{char} is not Anime characters or u typo')
    self.name = name or None
#url name
    url = result['url']
    self.url = url
#image url
    image_url = result['image_url']
    self.image_url = image_url
#about
    about = result['about']
    if 'No biography written.' in about:
      self.age = about
    about = ''.join(about)
    self.about = about
    self.anu = self.about.split('\n')
#age
    try:
      age = self.anu[0].split('Age: ')[1]
    except:
      age = 'Age biography not written.'
    self.age = age
#birthday
    try:
      try:
        birthday = self.anu[1].split('Birthday: ')[1]
      except:
        birthday = self.anu[0].split('Birthday: ')[1]
    except:
      birthday = 'Birthday biography not written'
    self.birthday = birthday
#height
    
    try:
      try:
        height = self.anu[1].split('Height: ')[1]
      except:
        try:
          height = self.anu[2].split('Height: ')[1]
        except:
          height = self.anu[3].split('Height:')[1]
    except:
      height = 'Height biography not written'
    self.height = height
#weight
    try:
      try:
        weight = self.anu[1].split('Weight: ')[1]
      except:
        try:
          weight = self.anu[2].split('Weight: ')[1]
        except:
          weight = self.anu[3].split('Weight:')[1]
    except:
      weight = 'weight biography not written'
    self.weight = weight
#nickname
    nickname = result['nicknames']
    nickname = ', '.join(nickname)
    if ',' not in nickname:
      nickname = 'None'
    self.nickname = nickname
#anime reference
  @property
  def anime(self) -> list:
    anime = []
    for nama in self.result['animeography']:
      anime.append(nama['name'])
    anime = ', '.join(anime)
    return anime or None
#manga reference
  @property
  def manga(self) -> list:
    manga = []
    for nama in self.result['mangaography']:
      manga.append(nama['name'])
    manga = ', '.join(manga)
    return manga or None