import requests
from bs4 import BeautifulSoup
from datetime import date



class Seasonal:
    year = date.today()
    year = str(year).split('-')[0]

    doy = date.today().timetuple().tm_yday

        # "day of year" ranges for the northern hemisphere
    spring = range(80, 172)
    summer = range(172, 264)
    fall = range(264, 355)
        # winter = everything else

    if doy in spring:
            season = 'spring'
    elif doy in summer:
            season = 'summer'
    elif doy in fall:
            season = 'fall'
    else:
        season = 'winter'
        
    def __init__(self, limit='3', years=year, seasons=season): 

        url = requests.get(f'https://myanimelist.net/anime/season/{years}/{seasons}')
        soup = BeautifulSoup(url.content, 'html.parser')

        if int(limit) >= 9:
            raise KeyError('too many requests, limit max is 9')
        limit = int(limit)
        nama = soup.find_all('a', {"class": "link-title"})[:limit]
        name = []
        for namaa in nama:
            name.append(namaa.text)
        name = ', '.join(name)
        self.name = name or None
