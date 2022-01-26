import base64
import time
import codefast as cf
from typing import List

from rss.base import AnyNews, Article
from rss.data import WECHAT_PUBLIC


class WechatPublic(AnyNews):
    # wechat public articles base class
    def __init__(self, main_url, source: str = ''):
        super().__init__(main_url)
        self.source = source  # 公众号名称

    def get_wechat_url(self, url: str, retry: int = 10) -> str:
        retry = retry
        while retry >= 0 and 'mp.weixin.qq.com' not in url:
            retry -= 1
            url = self.spider.get(url).url
            time.sleep(1)
        return url

    def search_articles(self, soup) -> List[Article]:
        articles = []
        archives = self.get_archives()
        old_ids = [a.uid for a in archives]

        for div in soup.find_all('div', class_='title'):
            href = div.find('a') or {}
            href = href.get('href')
            if not href: continue

            title = div.text.replace('原创', '').strip()
            uid = base64.b64encode(title.encode('utf-8')).decode('utf-8')
            if uid in old_ids:
                cf.info('articles old than {} already exists'.format(title))
                return articles

            url = self.get_wechat_url(href)
            article = Article(title=title,
                              uid=uid,
                              url=url,
                              source=self.source)
            articles.append(article)
        return articles


def worker_factory(main_url: str, source, redis_subkey: str) -> WechatPublic:
    wp = WechatPublic(main_url, source)
    wp.type += ':%s' % redis_subkey
    return wp


def create_rss_worker(key: str) -> WechatPublic:
    map_ = WECHAT_PUBLIC[key]
    return worker_factory(map_['main_url'], map_['source'],
                          map_['redis_subkey'])
