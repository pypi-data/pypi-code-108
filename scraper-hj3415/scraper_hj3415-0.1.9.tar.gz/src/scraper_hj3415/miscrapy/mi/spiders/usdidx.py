import scrapy
from mi import items

# cmd usage : scrapy crawl usdkrw


class UsdidxSpider(scrapy.Spider):
    name = 'usdidx'
    allowed_domains = ['finance.naver.com']
    start_urls = ['https://finance.naver.com/marketindex/worldExchangeDetail.nhn?marketindexCd=FX_USDX']

    def parse(self, response):
        print(f"Parsing ...'{self.name}' page", flush=True)
        item = items.MIitems()
        # Dollar Index를 스크랩하는코드
        self.logger.info(response.url)

        # 최근 데이터를 스크랩한다.
        # date - //*[@id="content"]/div[1]/div[2]/span[1]
        # value - //*[@id="content"]/div[1]/div[1]/p[1]/em
        value = []
        for span in response.xpath(f'//*[@id="content"]/div[1]/div[1]/p[1]/em/span'):
            value.append(span.xpath('text()').get())

        item['title'] = self.name
        item['date'] = response.xpath('//*[@id="content"]/div[1]/div[2]/span[1]/text()').get()
        item['value'] = ''.join(value)

        self.logger.info(f"date : {item['date']}, value : {item['value']}")
        yield item
