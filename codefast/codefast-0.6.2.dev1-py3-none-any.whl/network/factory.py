import requests
from codefast.patterns.singleton import SingletonMeta


class Spider(metaclass=SingletonMeta):
    # Create a requests session
    def __init__(self) -> None:
        pass

    def born(self) -> requests.Session:
        spider = requests.Session()
        spider.encoding = 'utf-8'
        spider.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        })
        return spider


