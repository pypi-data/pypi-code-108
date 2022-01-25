import scrapy
from mi import items

# cmd usage : scrapy crawl gold


class GoldSpider(scrapy.Spider):
    name = 'gold'
    allowed_domains = ['finance.naver.com']
    start_urls = ['https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_GC&fdtc=2']

    def parse(self, response):
        print(f"Parsing ...'{self.name}' page", flush=True)
        item = items.MIitems()
        # S&P500를 스크랩하는코드
        self.logger.info(response.url)
        # 최근 3개일의 데이터를 스크랩한다.
        for r in range(3, 0, -1):
            item['title'] = self.name
            item['date'] = (response.xpath(f'/html/body/div/table/tbody/tr[{r}]/td[1]/text()')
                            .get().replace('\t', '').replace('\n', ''))
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{r}]/td[2]/text()')
                             .get().replace(',', '').replace('\t', '').replace('\n', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item