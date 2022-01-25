from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from django.conf import settings
from ..items import HtmlPage

class GammaSpider(CrawlSpider):
    name = 'gammaspider'
    allowed_domains = settings.ALLOWED_HOSTS
    start_urls = settings.SPYDER_START_URLS[name]

    rules = (
        Rule(LinkExtractor(), callback='parse'),
    )

    def parse(self, response, **kwargs):
        page = HtmlPage()
        page['title'] = ' '.join(response.xpath('//title/text()').get().replace("\n", " ").split()) if response.xpath('//title/text()').get() else None
        page['description'] = ' '.join(response.xpath('//meta[@name="description"]/@content').get().replace("\n", " ").split()) if response.xpath('//meta[@name="description"]/@content').get() else None
        page['keywords'] = ' '.join(response.xpath('//meta[@name="keywords"]/@content').get().replace("\n", " ").split()) if response.xpath('//meta[@name="keywords"]/@content').get() else None
        page['url'] = response.url
        page['contents'] = ' '.join(BeautifulSoup(response.text, 'html.parser').get_text().replace("\n", " ").split())
        yield page

    #def closed(self, reason):
    #    super(GammaSpider, self).closed(reason)
