import random


class PROXY:
    proxy_type = {'http': 'http', 'https': 'http'}

    @classmethod
    def build(cls, proxy, proxy_type: dict = None):
        """
        build http and https proxy dict.
        :param proxy_type: set proxy type
        :param proxy: str -> proxy user:password@ip:port  e.g: user:password@0.0.0.0:11111
        """
        return {f'{p_type}': f'{prefix}://{proxy}' for p_type, prefix in (proxy_type or cls.proxy_type).items()}

    
class Clist(list):
    def random(self, default=None, func=random.choice):
        """
        :param default: if not self return default
        :param func: default: random.choice
        """
        try:
            return func(self)
        except IndexError:
            return default

    def reset(self, args: iter = None):
        if self:
            self.clear()
        self.extend(args or [])


class RequestsConf:
    proxies, cookies = Clist(), Clist()
    headers = Clist([{'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                    'Chrome/50.0.2661.102 Safari/537.36'}])

    @classmethod
    def random_headers(cls, headers: dict = None, set_new=False):
        headers = headers or {}
        return headers if set_new else {**cls.headers.random({}), **headers}

    @classmethod
    def random_cookies(cls, cookies: dict = None, set_new=False):
        cookies = cookies or {}
        return cookies if set_new else {**cls.cookies.random({}), **cookies}

    @classmethod
    def random_proxy(cls, proxy: str = None, proxy_generator=None, proxy_type: dict = None):
        g_proxy = proxy_generator() if proxy_generator else None
        proxy = proxy or (g_proxy or cls.proxies.random())
        return PROXY.build(proxy, proxy_type) if proxy else {}
