# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HtmlPage(Item):
    title = Field()
    description = Field()
    keywords = Field()
    url = Field()
    contents = Field()
