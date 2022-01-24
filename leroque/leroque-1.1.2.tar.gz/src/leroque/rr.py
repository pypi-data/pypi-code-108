import time
import re

import requests
from bs4 import BeautifulSoup
import utils

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
            timeToReturn = re.search(r'{until: (\d+)', self.post(f'https://rivalregions.com/map/region_move/{regId}',
                                                                 data=data).text).group(0)
            return timeToReturn


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

acc = authByCookie(utils.getDictFromString('_ym_d=1642005179; _ym_uid=1642005179504794246; _iub_cs-76236742=%7B%22consent%22%3Atrue%2C%22timestamp%22%3A%222022-01-12T16%3A33%3A00.088Z%22%2C%22version%22%3A%221.2.4%22%2C%22id%22%3A76236742%7D; __atuvc=1%7C3; rr=9eaed3508aecdde8eedbe3fea9409d76; rr_id=160819338; rr_add=f96b83aca6c1c84222de35084cc8441e; rr_f=48b0c0e312f9b633c12eae17cb920f5d; _ym_isad=1; PHPSESSID=2rs6ikvs7fbk3p573nj13s8e66'),
                   '4cecd48d19dc4aa5bc5c2cf6aee45954')
acc.flyTo(48)
