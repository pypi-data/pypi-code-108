import time

import requests
from bs4 import BeautifulSoup


class WrongCookies(Exception):
    def __init__(self, message="Wrong RR cookies"):
        self.message = message
        super().__init__(self.message)


class RRSession(requests.Session):
    def __init__(self, c):
        super().__init__()
        self.c = {'c': c}

    def checkValid(self):
        if "$('.vkvk').attr('url', 'https://oauth.vk.com/authorize" in self.get('https://rivalregions.com/').text:
            raise WrongCookies
        return 1

    def upPerk(self, perk, speed):
        if self.checkValid():
            self.post(f"https://rivalregions.com/perks/up/{perk}/{speed}", data=self.c)

    def upPerkUntil(self, perk, speed, border, delay=60):
        while self.getPerk(perk) < border:
            self.upPerk(perk, speed)
            time.sleep(delay)
        return True

    def getPerk(self, perk):
        if self.checkValid():
            def is_stat(tag):
                if tag.has_attr('action'):
                    return 'perk' in tag['action']
                return False

            if self.checkValid():
                soup = BeautifulSoup(self.post('https://rivalregions.com/slide/profile').text, 'html.parser')
                return int(soup.find_all(is_stat)[perk - 1].text)

    def flyTo(self, regId, typeOf=2):
        if self.checkValid():
            data = {}
            data.update(self.c)
            data.update({'type': typeOf})
            data.update({'b': 1})
            self.post(f'https://rivalregions.com/map/region_move/{regId}', data=data)


def authByCookie(_cookies, c, proxies=None):
    session = RRSession(c)
    if proxies is not None:
        session.proxies.update(proxies)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
    session.get('https://rivalregions.com/')
    session.cookies.update(_cookies)
    return session

