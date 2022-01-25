import scrapy
from mi import items

# cmd usage : scrapy crawl kosdaq


class KosdaqSpider(scrapy.Spider):
    name = 'kosdaq'
    allowed_domains = ['finance.naver.com']
    start_urls = ['https://finance.naver.com/sise/sise_index_day.nhn?code=KOSDAQ']

    def parse(self, response):
        print(f"Parsing ...'{self.name}' page", flush=True)
        item = items.MIitems()
        # KOSDAQ를 스크랩하는코드
        self.logger.info(response.url)
        # 최근 3개일의 데이터를 스크랩한다.
        for r in range(3, 6):
            item['title'] = self.name
            item['date'] = response.xpath(f'/html/body/div/table[1]/tr[{r}]/td[1]/text()').get()
            item['value'] = response.xpath(f'/html/body/div/table[1]/tr[{r}]/td[2]/text()').get().replace(',', '')
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item