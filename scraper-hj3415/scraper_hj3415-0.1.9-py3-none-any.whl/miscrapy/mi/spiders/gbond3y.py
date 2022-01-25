import scrapy
from mi import items

# cmd usage : scrapy crawl gbond3y


class Gbond3ySpider(scrapy.Spider):
    name = 'gbond3y'
    allowed_domains = ['finance.naver.com']
    start_urls = ['https://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y']

    def parse(self, response):
        print(f"Parsing ...'{self.name}' page", flush=True)
        item = items.MIitems()
        # 국고채 3년금리를 스크랩하는코드
        self.logger.info(response.url)
        for r in range(3, 0, -1):
            item['title'] = self.name
            item['date'] = (response.css(f'body > div > table > tbody > tr:nth-child({r}) > td.date::text')
                            .extract()[0].replace('\n', '').replace('\t', ''))
            item['value'] = (response.css(f'body > div > table > tbody > tr:nth-child({r}) > td:nth-child(2)::text')
                .extract()[0])
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item