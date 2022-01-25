import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from django.core.management.base import BaseCommand
from ...searchbot import GammaSpider

class Command(BaseCommand):
    help = 'Triggers the searchbot crawler to crawl this site'

    def handle(self, *args, **kwargs):
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'generic_search.searchbot.searchbot.settings')
        print(get_project_settings())
        c = CrawlerProcess(get_project_settings())
        c.crawl(GammaSpider)
        c.start()