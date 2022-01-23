from execrequests import RequestsConf
from requests import Session, adapters
from urllib3.util.retry import Retry
from lxml import etree
import re


class RequestsHandler(Session):
    def __init__(self, puser=None, set_proxy=True, proxy_generator=None, retry=3,
                 pool_maxsize=10000, proxy_type: dict = None, **kwargs):
        super(RequestsHandler, self).__init__()
        retry_strategy = Retry(total=retry, **kwargs)
        adapter = adapters.HTTPAdapter(max_retries=retry_strategy, pool_maxsize=pool_maxsize)
        self.__p = puser or {}
        if set_proxy:
            self.proxies.update(RequestsConf.random_proxy(self.__p.get('proxy'), proxy_generator=proxy_generator, proxy_type=proxy_type))  # noqa
        if puser:
            self.headers.update(RequestsConf.random_headers(self.__p.get('headers')))
            self.cookies.update(RequestsConf.random_cookies(self.__p.get('cookies')))
        else:
            self.headers.update(RequestsConf.random_headers(self.__p.get('headers')))
        self.mount("https://", adapter)
        self.mount("http://", adapter)

    def puser_update(self, puser: dict, proxy_type: dict = None):
        self.proxies.update(RequestsConf.random_proxy(puser.get('proxy'), proxy_type=proxy_type))
        self.headers.update(RequestsConf.random_headers(puser.get('headers')))
        self.cookies.update(RequestsConf.random_cookies(puser.get('cookies')))

    def puser_reset(self, puser: dict, proxy_type: tuple = None):
        [i.clear() for i in (self.proxies, self.headers, self.cookies)]
        self.puser_update(puser, proxy_type=proxy_type)

    @staticmethod
    def xpath(content: bytes, xpath: str):
        return etree.HTML(content).xpath(xpath)


class ShowRequest:

    @classmethod
    def url(cls, url: str, modify=True):
        url = url.replace('+', '%20')
        return cls.modify(url, "URL") if modify else url

    @classmethod
    def cookies(cls, cookie: dict, modify=True, pattern=r'["{}]{2}'):
        c = f'{cookie}'.replace('\'', '"').replace('", "', '; ').replace('": "', '=')
        c = 'cookie: ' + re.sub(pattern, "", c)
        return cls.modify(c, "COOKIES") if modify else c

    @classmethod
    def headers(cls, headers, modify=True, pattern=r'^["{}]{1,2}'):
        h = f'{headers}'.replace("'", '"').replace('", "', '\n').replace('": "', ': ').replace('"}', '')
        h = re.sub(pattern, "", h)
        return cls.modify(h, 'HEADERS') if modify else h

    @classmethod
    def modify(cls, item, title: str, sign=("=",), f_long=150):
        lt = (f_long - len(title)) // 2
        title = title.upper()
        mf = '\n{0}{1}{0}\n'
        return f'{mf.format(sign[0]*lt, title)}{item}{mf.format(sign[-1]*lt, title)}'
