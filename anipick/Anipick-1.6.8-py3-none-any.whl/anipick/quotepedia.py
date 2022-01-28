
from random import choice
import os
import requests



#uhh
class Quotenime:
    base_url = ['https://animechan.vercel.app/api/random', 'https://some-random-api.ml/animu/quote']
    base_url = choice(base_url)
    if 'some-random' in base_url:
      r = requests.get(base_url)
      result = r.json()
      quote = result['sentence']
      char = result['character']
      anime = result['anime']
    else:
      re = requests.get(base_url)
      resu = re.json()
      quote = resu['quote']
      char = resu['character']
      anime = resu['anime']

    quote = quote or None
    char = char or None
    anime = anime or None
