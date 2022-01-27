#!/usr/bin/env python
import random
import urllib
from typing import Dict, List, Optional, Set, Tuple, Union

from bs4 import BeautifulSoup

from rss.core import shorten_url
from rss.base.urlparser import TextBody, UrlParser


class MeiTuan(UrlParser):
    """ A parser for fetching blog links from the: tech.meituan.com
    """
    def __init__(self, url: str, host: str) -> None:
        super().__init__(url, host, 'meituan')

    def fetch_soup(self) -> BeautifulSoup:
        """rewrite UrlParser.fetch_soup(), because blogs are presented among multiple pages 
        """
        urls = [
            'https://tech.meituan.com/page/{}.html'.format(i)
            for i in range(1, 25)
        ]
        random_url = random.choice(urls)
        response = self.spider.get(random_url)
        return BeautifulSoup(response.content, 'html.parser')

    def parse(self, soup: BeautifulSoup):
        """Return dictioanry of blog titles and link.
        div demo:
        <div class="post-content post-expect">
            美团外卖商家端基于 FlutterWeb 的技术探索已久 ...
            <a class="more-link btn btn-primary btn-xs" 
                href=https://tech.meituan.com/2021/12/16/flutterweb-practice-in-meituan-waimai.html>阅读全文
            </a>
        </div>
        """
        for link in soup.find_all('div', class_='post-content'):
            blog = {}
            blog['title'] = link.text
            blog['url'] = link.find('a').get('href')
            blog['extra_url'] = shorten_url(blog['url'])
            blog['date'] = 'N/A'
            if not blog['title']:
                continue
            blog = TextBody(**blog)
            self.results[blog.url] = blog
        return self.results
