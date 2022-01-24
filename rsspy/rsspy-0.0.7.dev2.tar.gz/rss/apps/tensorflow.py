#!/usr/bin/env python
import urllib
from typing import Dict, List, Optional, Set, Tuple, Union

from bs4 import BeautifulSoup

from rss.base.urlparser import TextBody, UrlParser


class TensorFlowBlog(UrlParser):
    """ A parser for fetching blog links from the TensorFlow website: https://blog.tensorflow.org/
    """
    def __init__(self, url: str, host: str) -> None:
        super().__init__(url, host, 'tensorflow')

    def parse(self, soup: BeautifulSoup):
        """Return dictioanry of blog links, titles and date.
        """
        for link in soup.find_all('div', class_='tensorsite-card'):
            blog = {
                'url':
                link.find('a').get('href'),
                'title':
                link.find('div',
                          class_='tensorsite-content__title').text.strip(),
                'date':
                link.find('span',
                          class_='tensorsite-content__info').text.strip()
            }
            blog = TextBody(**blog)
            self.results[blog.url] = blog
        return self.results
