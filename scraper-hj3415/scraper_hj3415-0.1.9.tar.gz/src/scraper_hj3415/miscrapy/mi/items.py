import scrapy


class MIitems(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    value = scrapy.Field()
