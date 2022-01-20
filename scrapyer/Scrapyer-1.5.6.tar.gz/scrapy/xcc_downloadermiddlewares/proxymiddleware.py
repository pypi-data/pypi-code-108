from scrapy import signals
import base64
import random
import logging
from scrapy.exceptions import IgnoreRequest,NotConfigured

class ProxyMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, user, password, server):
        self.user = user
        self.password = password
        self.server = server

    @classmethod
    def from_crawler(cls, crawler):
        user=crawler.settings.get('PROXY_USER','')
        password=crawler.settings.get('PROXY_PASS','')
        server=crawler.settings.get('PROXY_SERVER','')
        s = cls(user=user,password=password,server=server)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
        
    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        proxyUser = self.user
        proxyPass = self.password
        proxyServer = self.server
        if proxyUser and proxyPass and proxyServer:
            proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")
            request.meta["proxy"] = proxyServer
            request.headers["Proxy-Authorization"] = proxyAuth
            

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
