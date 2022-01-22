import requests


class WrongCookies(Exception):
    def __init__(self, message="Wrong RR cookies"):
        self.message = message
        super().__init__(self.message)


class RRSession(requests.Session):
    def __init__(self, c):
        super().__init__()
        self.c = {'c': c}

    def upPerk(self, perk, speed):
        self.post(f"https://rivalregions.com/perks/up/{perk}/{speed}", data=self.c)


def auth_by_cookie(_cookies, c, proxies=None):
    session = RRSession(c)
    if proxies is not None:
        session.proxies.update(proxies)
    session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
    session.cookies.update(_cookies)
    return session




