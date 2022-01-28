import requests
from googlesearch import search
from .error_handling import NoResultFound
from requests.exceptions import HTTPError

class Animegraphy:
  def __init__(self, title: str):
    
    try:
      mal_id = search('site:myanimelist.net {} anime info inurl:anime/'.format(title), num_results=0)
    except HTTPError:
      raise HTTPError('Too many requests')
    if not mal_id:
        raise NoResultFound('Not found')
    try:
        mal_id = ''.join(mal_id).split('/')[4]
    except:
        raise KeyError('Not found')
    self.mal_id = mal_id
    url = f'https://api.jikan.moe/v3/anime/{self.mal_id}/'
    r = requests.get(url)
    resu = r.json()
    self.resu = resu or None
    #Anime Title
    title = resu['title']
    self.title = title or None

#anime url
    anime_url = resu['url']
    self.anime_url = anime_url or None

#image anime url
    image_url = resu['image_url']
    self.image_url = image_url or None

#rated anime, example = PG - 13
    rated = resu['rating']
    self.rated = rated or None

#type anime, example = TV
    type_nime = resu['type']
    self.type = type_nime or None

#score rating anime
    score = resu['score']
    self.score = score or None

#episode anime
    eps = resu['episodes']
    self.eps = eps or None


#opening song
    op_song = resu['opening_themes']
    op_song = '"'.join(op_song)
    self.op_song = op_song or None

#ending song
    ed_song = resu['ending_themes']
    ed_song = '"'.join(ed_song)
    self.ed_song = ed_song or None

#aired
    aired = resu['aired']['string']
    self.aired = aired or None

#ranking
    ranknim = resu['rank']
    self.rank = ranknim or None

#popularity
    popularity = resu['popularity']
    self.popularity = popularity or None

#synopsis
    synopsis = resu['synopsis']
    self.synopsis = synopsis or None

#trailer url(EMBED)
    trailer_url = resu['trailer_url']
    trailer_url = trailer_url.split('/')[4].split('?')[0]
    trailer_url = f'https://youtube.com/watch?v={trailer_url}'
    self.trailer_url = trailer_url or None
#status anime
    status = resu['status']
    self.status = status or None
#premiered
    premiered = resu['premiered']
    self.premiered = premiered or None
#broadcast
    broadcast = resu['broadcast']
    self.broadcast = broadcast or None
#adaptation anime type
    try:
        adaptation_type = resu['related']['Adaptation'][0]['type']
    except:
        adaptation_type = "This Anime Doesn't Have A Manga/Anime Adaptation"
    self.adaptation_type = adaptation_type or None
#adaptation anime name
    try:
        adaptation_name = resu['related']['Adaptation'][0]['name']
    except:
        adaptation_name = "This Anime Doesn't Have A Manga/Anime Adaptation"
    self.adaptation_name = adaptation_name or None
#sequel name
    try:
        sequel_name = resu['related']['Sequel'][0]['name']
    except:
        sequel_name = "This Anime Doesn't Have A Anime Sequel"
    self.sequel = sequel_name or None
#sequel url
    try:
        sequel_url = resu['related']['Sequel'][0]['url']
    except:
        sequel_url = "This Anime Doesn't Have A Anime Sequel"
    self.sequel_url = sequel_url or None
#adaptation
    adaptation = f' {adaptation_type}, {adaptation_name}'
    self.adaptation = adaptation or None
#favorite
    favorite = resu['favorites']
    self.favorite = favorite or None
#duration
    duration = resu['duration']
    self.duration = duration or None
#source
    source = resu['source']
    self.source = source or None
#background
    background = resu['background']
    self.background = background or None
  @property
  def studio(self):
      studio = []
      for nama in self.resu['studios']:
          studio.append(nama['name'])
      studio = ', '.join(studio)
      return studio or None
  @property
  def genre(self) -> list:
      genre = []
      for nama in self.resu['genres']:
          genre.append(nama['name'])
      genre = ', '.join(genre)
      return genre or None
  @property
  def producers(self):
      producers = []
      for nama in self.resu['producers']:
          producers.append(nama['name'])
      producers = ', '.join(producers)
      return producers or None
  @property
  def recommend(self):
      recommend = []
      url = f'https://api.jikan.moe/v3/anime/{self.mal_id}/recommendations'
      su = requests.get(url)
      sult = su.json()
      self.sult = sult
      for nama in self.sult['recommendations']:
          recommend.append(nama['title'])
      recommend = recommend[:5]
      recommend = '; '.join(recommend)
      return recommend or None
  def nsfw_scan(self) -> bool:
      return any(a in self.rated for a in ['R', '17'])