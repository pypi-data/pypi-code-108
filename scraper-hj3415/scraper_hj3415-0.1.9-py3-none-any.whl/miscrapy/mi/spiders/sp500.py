import scrapy
from mi import items

# cmd usage : scrapy crawl sp500


class Sp500Spider(scrapy.Spider):
    name = 'sp500'
    allowed_domains = ['finance.naver.com']
    start_urls = ['https://finance.naver.com/world/sise.nhn?symbol=SPI@SPX']

    def parse(self, response):
        print(f"Parsing ...'{self.name}' page", flush=True)
        item = items.MIitems()
        # S&P500를 스크랩하는코드
        self.logger.info(response.url)
        # 최근 3개일의 데이터를 스크랩한다.
        for r in range(3, 0, -1):
            item['title'] = self.name
            item['date'] = response.xpath(f'//*[@id="dayTable"]/tbody/tr[{r}]/td[1]/text()').get()
            item['value'] = (response.xpath(f'//*[@id="dayTable"]/tbody/tr[{r}]/td[2]/span/text()')
                             .get().replace(',', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
