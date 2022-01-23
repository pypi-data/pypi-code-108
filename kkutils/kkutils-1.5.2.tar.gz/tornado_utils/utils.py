#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-07-30 21:41:46
'''
import functools
import math
import urllib.parse
from urllib.parse import urlencode

from tornado.template import Template
from tornado.web import HTTPError, UIModule
from utils import awaitable


def authorized(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        if not await awaitable(self.current_user):
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urllib.parse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        assert self.request.uri is not None
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return None
            raise HTTPError(403)
        return await awaitable(method(self, *args, **kwargs))
    return wrapper


def cache(method=None, cache_time=86400):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.app.cache_enabled and not self.settings['debug']:
                html = self.app.rd.get(self.cache_key)
                if html:
                    self.finish(html)
                else:
                    self.cache_time = cache_time
                    method(self, *args, **kwargs)
            else:
                method(self, *args, **kwargs)
        return wrapper

    return decorator if method is None else decorator(method)


class PageModule(UIModule):

    def get_url(self, page):
        ret = urllib.parse.urlparse(self.handler.request.uri)
        query = urllib.parse.parse_qs(ret.query)
        query.update({'page': page})
        url = urllib.parse.urlunparse((ret.scheme, ret.netloc, ret.path, ret.params,
                                       urllib.parse.urlencode(query, doseq=True), ret.fragment))
        return url

    def render(self, total, **kwargs):
        ''' Args:
        size: how many items each page shows
        total: the total items number
        '''
        t = Template('''<nav>
<ul class="pagination">
  <li class="page-item {% if page == 1 %}active{% end %}"><a class="page-link" href="{{ get_url(1) }}">1</a></li>
    {% if page > 2 and pages > 4 %}
    <li class="page-item disabled"><span class="page-link">«</span></li>
    {% end %}
    {% for i in range(max(2,pages-2) if page >= pages-1 else max(2,page-1), min(4,page+3,pages) if page<=2 else min(pages,page+2))  %}
    <li class="page-item {% if page == i %}active{% end %}"><a class="page-link" href="{{ get_url(i) }}">{{i}}</a></li>
    {% end %}
    {% if page + 1 < pages and pages > 4 %}
    <li class="page-item disabled"><span class="page-link">»</span></li>
    {% end %}
    {% if pages > 1 %}
    <li class="page-item {% if page == pages %}active{% end %}"><a class="page-link" href="{{ get_url(pages) }}">{{pages}}</a></li>
    {% end %}
    <li class="page-item disabled"><span class="page-link">{{ total }}项</span></li>
  </ul>
</nav>''')
        size = self.handler.get_argument('size', None)
        page = self.handler.get_argument('page', None)
        kwargs.setdefault('size', int(size) if size else 20)
        kwargs.setdefault('page', int(page) if page else 1)
        pages = int(math.ceil(total / kwargs['size']))
        return t.generate(pages=pages, total=total, get_url=self.get_url, **kwargs)

    def css_files(self):
        pass
        # return '//cdn.bootcss.com/bootstrap/4.1.1/css/bootstrap.min.css'
