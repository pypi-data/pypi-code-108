import base64
import codefast as cf
from typing import List
import feedparser

from rss.base import AnyNews, Article
from rss.data import WECHAT_PUBLIC


class FeedEntryToArticle(object):
    def __init__(self, entry, source: str):
        self.title = entry.title.replace('&', '').replace('|', '').strip()
        self.uid = base64.b64encode(self.title.encode('utf-8')).decode('utf-8')
        self.url = entry.link
        self.source = source
        self.published_at = entry.published
        self.published_at_parsed = entry.published_parsed
        self.content = entry.summary

    def to_article(self):
        return Article(title=self.title,
                       uid=self.uid,
                       url=self.url,
                       source=self.source)


class _Feeder(object):
    AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'


class WechatRSS(AnyNews):
    ''' Fetch new articles with a paid public aggregator feed service, such as https://werss.app/
    '''

    def __init__(self, main_url, source: str = ''):
        super().__init__(main_url)
        self.source = source  # 公众号名称

    def search_articles(self) -> List[Article]:
        seen_ids = [a.uid for a in self.archives]
        entries = feedparser.parse(self.main_url, agent=_Feeder.AGENT).entries
        articles = [
            FeedEntryToArticle(entry, self.source) for entry in entries
        ]
        articles = [a.to_article() for a in articles if not (
            a.uid in seen_ids or self.redis.get(cf.b64encode(a.url)))]
        return articles

    def pipeline(self) -> List[Article]:
        articles = self.search_articles()
        archives = self.archives
        latest, all_ = self.latest(archives, articles)
        for a in latest:
            self.redis.set(cf.b64encode(a.url), '1', ex=3600 * 720)
        return latest, all_


def worker_factory(main_url: str, source, redis_subkey: str) -> WechatRSS:
    wp = WechatRSS(main_url, source)
    wp.type += ':%s' % redis_subkey
    return wp


def create_rss_worker(key: str) -> WechatRSS:
    map_ = WECHAT_PUBLIC[key]
    return worker_factory(map_['main_url'], map_['source'],
                          map_['redis_subkey'])
