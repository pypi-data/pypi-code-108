import requests
from googlesearch import search
from bs4 import BeautifulSoup
from .error_handling import SearchNotWork, NoResultFound

class Mangaography:
  def __init__(self, title: str):
    try:
      manga_id = search(f'site:myanimelist.net {title} inurl:/manga/ manga info', num_results=0)
    except:
      raise SearchNotWork('Search Library not work/connection not found')
    try:
      manga_id = ''.join(manga_id).split('/')[4]
    except:
      raise NoResultFound('No Result Found')
    self.manga_id = manga_id or None
    base_url = f'https://api.jikan.moe/v3/manga/{self.manga_id}'
    url = requests.get(base_url)
    result = url.json()
    self.result = result
#manga name
    name = result['title']
    self.name = name or None
#manga en name
    name_en = result['title_english']
    self.name_en = name_en or None
#manga jp name
    name_jp = result['title_japanese']
    self.name_jp = name_jp
#anime url
    manga_url = result['url']
    self.manga_url = manga_url or None

#image anime url
    image_url = result['image_url']
    self.image_url = image_url or None

#type anime, example = TV
    type = result['type']
    self.type = type or None

#score rating anime
    score = result['score']
    self.score = score or None

#aired
    aired = result['published']['string']
    self.aired = aired or None

#ranking
    ranking = result['rank']
    self.ranking = ranking or None

#popularity
    popularity = result['popularity']
    self.popularity = popularity or None

#synopsis
    synopsis = result['synopsis']
    self.synopsis = synopsis or None
#publishing
    is_publishing = result['publishing']
    self.is_publishing = is_publishing or None
#volumes
    volume = result['volumes']
    self.volume = volume
#chapter
    chapter = result['chapters']
    self.chapter = chapter
#member
    member = result['members']
    self.member = member
#favorites
    favorite = result['favorites']
    self.favorite = favorite or None
#status
    status = result['status']
    self.status = status

#author
  @property
  def author(self) -> list:
      author = []
      for nama in self.result['authors']:
          author.append(nama['name'])
      author = ', '.join(author)
      return author or None
#genre
  @property
  def genres(self) -> list:
      genres = []
      for nama in self.result['genres']:
          genres.append(nama['name'])
      genres = ', '.join(genres)
      return genres or None
#related
  @property
  def related(self) -> list:
      related = []
      try:
        for nama in self.result['related']['Adaptation']:
          related.append(nama['name'])
      except:
        for nama in self.result['related']['Alternative version']:
          related.append(nama['name'])
      related = ', '.join(related)
      return related or None
#serializations
  @property
  def serialization(self) -> list:
      serialization = []
      for nama in self.result['serializations']:
          serialization.append(nama['name'])
      serialization = ', '.join(serialization)
      return serialization or None
  
  
  
  