import json
import codefast as cf
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Tuple
from bs4 import BeautifulSoup
from codefast.functools import naruto
from rss.core import Initiator, Spider, shorten_url


class Article(NamedTuple):
    uid: str = None
    title: str = None
    url: str = None
    source: str = None
    author: str = None
    date: str = None
    extra_url: str = None

    def __str__(self):
        return '\n'.join(
            ['{}: {}'.format(k, v) for k, v in self._asdict().items() if v])

    def telegram_format(self) -> str:
        short_url = shorten_url(self.url)
        msg = 'Title: {}\nURL: {}'.format(self.title, short_url)
        if self.source:
            msg += '\nSource: {}'.format(self.source)
        return msg


class DummyItem(NamedTuple):
    text: str = ''
    href: str = ''


class AnyNews(ABC):
    """ check whether any new articles posted in a certain website
    """
    def __init__(self, main_url: str):
        self.main_url = main_url
        self.spider = Spider().born()
        self.type = 'anynews'
        self._redis = None
        self._archives = None

    @property
    def redis(self):
        if not self._redis:
            self._redis = Initiator.redis()
        return self._redis

    @property
    def archives(self):
        if not self._archives:
            self._archives = self.get_archives()
        cf.info('found archives {} \nfor key {}'.format(
            self._archives, self.type))
        return self._archives

    def get_soup(self) -> BeautifulSoup:
        soup = self.spider.get(self.main_url)
        return BeautifulSoup(soup.content, 'html.parser')

    @abstractmethod
    def search_articles(self, soup: BeautifulSoup) -> List[Article]:
        pass

    def latest(self, old: List[Article],
               new: List[Article]) -> Tuple[List[Article]]:
        # Return a tuple: (the latest articles, all articles)
        old_ids = set([e.uid for e in old])
        latest_ids = set([e.uid for e in new if e.uid not in old_ids])
        latest = [e for e in new if e.uid in latest_ids]
        all_ = latest + old
        return latest, all_

    def get_archives(self) -> List[Article]:
        arch = naruto.load(self.redis.get_key,
                           self.type).ensure_nontrivial_return(3, 10)
        return [Article(**e)
                for e in json.loads(arch.decode('utf-8'))] if arch else []

    def save_to_redis(self, articles: List[Article]) -> None:
        str_articles = json.dumps([a._asdict() for a in articles],
                                  ensure_ascii=True)
        cf.info('save to redis: {} with key {}'.format(str_articles,
                                                       self.type))
        _f = lambda: self.redis.set_key(
            self.type, str_articles, ex=60 * 60 * 24 * 30)
        return naruto.load(_f).ensure_nontrivial_return()

    def pipeline(self) -> List[Article]:
        soup = self.get_soup()
        articles = self.search_articles(soup)
        archives = self.get_archives()
        latest, all_ = self.latest(archives, articles)
        return latest, all_
