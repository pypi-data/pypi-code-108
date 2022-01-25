import time
import scrapy
from scrapy.selector import Selector
from selenium.common.exceptions import NoSuchElementException
from mi import items

# cmd usage : scrapy crawl mihistory -a year=1


from selenium import webdriver
import selenium.webdriver.chrome.webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_driver() -> selenium.webdriver.chrome.webdriver.WebDriver:
    """ 크롬 드라이버를 생성 및 반환

    원래는 util_hj3415에서 만들었으나 메모리 누수 문제로 각 모듈별로 따로 만들기로함.
    """
    # 크롬드라이버 옵션세팅
    options = webdriver.ChromeOptions()
    # reference from https://gmyankee.tistory.com/240
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-gpu')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-extensions")

    # 크롬드라이버 준비
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    print('Get chrome driver successfully...')

    return driver


WAIT = 1


class MIHistory(scrapy.Spider):
    name = 'mihistory'
    allowed_domains = ['finance.naver.com']

    def __init__(self, year=1):
        self.year = int(year)
        self.driver = get_driver()
        if self.driver is None:
            raise
        # 대략1년전 kospi, kosdaq -> 42, gbond3y -> 38, s&p -> 27, usdkrw -> 26, wti -> 38, gold -> 38, audchf -> 46
        self.last_page_kospi_kosdaq = 42 * self.year
        self.last_page_3bond3y = 38 * self.year
        self.last_page_sp500 = 27 * self.year
        self.last_page_usdkrw = 26 * self.year
        self.last_page_wti = 38 * self.year
        self.last_page_gold = 38 * self.year
        self.last_page_silver = 38 * self.year
        self.last_page_audchf = 46 * self.year
        self.item_list = []
        self.aud_dict = {}
        self.audchf_dict = {}

    def start_requests(self):
        # reference from https://docs.scrapy.org/en/latest/topics/request-response.html
        print(f'Parsing Market Index history...{self.year} year..')
        yield scrapy.Request(
            url=f'https://finance.naver.com/sise/sise_index_day.nhn?code=KOSPI&page={self.last_page_kospi_kosdaq}',
            callback=self.parse_kospi,
            cb_kwargs=dict(page=self.last_page_kospi_kosdaq),
        )

    def parse_kospi(self, response, page):
        print(f"Parsing ...kospi {page} page", flush=True)
        item = items.MIitems()
        # KOSPI를 스크랩하는코드
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in [12, 11, 10, 5, 4, 3]:
            item['title'] = 'kospi'
            item['date'] = response.xpath(f'/html/body/div/table[1]/tr[{i}]/td[1]/text()').get()
            item['value'] = response.xpath(f'/html/body/div/table[1]/tr[{i}]/td[2]/text()').get().replace(',', '')
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/sise/sise_index_day.nhn?code=KOSPI&page={page - 1}',
                callback=self.parse_kospi,
                cb_kwargs=dict(page=page - 1),
            )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/sise/sise_index_day.nhn?code=KOSDAQ&page={self.last_page_kospi_kosdaq}',
                callback=self.parse_kosdaq,
                cb_kwargs=dict(page=self.last_page_kospi_kosdaq),
            )

    def parse_kosdaq(self, response, page):
        print(f"Parsing ...kosdaq {page} page", flush=True)
        item = items.MIitems()
        # KOSDAQ를 스크랩하는코드
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in [12, 11, 10, 5, 4, 3]:
            item['title'] = 'kosdaq'
            item['date'] = response.xpath(f'/html/body/div/table[1]/tr[{i}]/td[1]/text()').get()
            item['value'] = response.xpath(f'/html/body/div/table[1]/tr[{i}]/td[2]/text()').get().replace(',', '')
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/sise/sise_index_day.nhn?code=KOSDAQ&page={page - 1}',
                callback=self.parse_kosdaq,
                cb_kwargs=dict(page=page - 1),
            )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y&page={self.last_page_3bond3y}',
                callback=self.parse_gbond3y,
                cb_kwargs=dict(page=self.last_page_3bond3y),
            )

    def parse_gbond3y(self, response, page):
        print(f"Parsing ...gbond3y {page} page", flush=True)
        item = items.MIitems()
        # 국고채 3년금리를 스크랩하는코드
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(7, 0, -1):
            item['title'] = 'gbond3y'
            item['date'] = (response.css(f'body > div > table > tbody > tr:nth-child({i}) > td.date::text')
                            .extract()[0].replace('\n', '').replace('\t', ''))
            item['value'] = (response.css(f'body > div > table > tbody > tr:nth-child({i}) > td:nth-child(2)::text')
                .extract()[0])
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y&page={page - 1}',
                callback=self.parse_gbond3y,
                cb_kwargs=dict(page=page - 1),
                )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?fdtc=4&marketindexCd=FX_USDAUD',
                callback=self.parse_aud,
                cb_kwargs=dict(page=self.last_page_audchf),
            )

    def parse_aud(self, response, page):
        print(f"Parsing ...aud {page} page", flush=True)
        item = items.MIitems()
        # AUD를 스크랩하는코드
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(7, 0, -1):
            item['title'] = 'aud'
            item['date'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[1]/text()')
                            .get().replace('\t', '').replace('\n', ''))
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[2]/text()')
                             .get().replace(',', '').replace('\t', '').replace('\n', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?fdtc=4&marketindexCd=FX_USDAUD&page={page - 1}',
                callback=self.parse_aud,
                cb_kwargs=dict(page=page - 1),
                )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?fdtc=4&marketindexCd=FX_USDCHF',
                callback=self.parse_chf,
                cb_kwargs=dict(page=self.last_page_audchf),
            )

    def parse_chf(self, response, page):
        print(f"Parsing ...chf {page} page", flush=True)
        item = items.MIitems()
        # CHF를 스크랩하는코드
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(7, 0, -1):
            item['title'] = 'chf'
            item['date'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[1]/text()')
                            .get().replace('\t', '').replace('\n', ''))
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[2]/text()')
                             .get().replace(',', '').replace('\t', '').replace('\n', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?fdtc=4&marketindexCd=FX_USDCHF&page={page - 1}',
                callback=self.parse_chf,
                cb_kwargs=dict(page=page - 1),
                )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW&page={self.last_page_usdkrw}',
                callback=self.parse_usdkrw,
                cb_kwargs=dict(page=self.last_page_usdkrw),
            )

    def parse_usdkrw(self, response, page):
        print(f"Parsing ...usdkrw {page} page", flush=True)
        item = items.MIitems()
        # 달러 원화 환율 스크랩
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(10, 0, -1):
            item['title'] = 'usdkrw'
            item['date'] = response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[1]/text()').get()
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[2]/text()')
                             .get().replace(',', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW&page={page - 1}',
                callback=self.parse_usdkrw,
                cb_kwargs=dict(page=page - 1),
            )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_CL&fdtc=2&page={self.last_page_wti}',
                callback=self.parse_wti,
                cb_kwargs=dict(page=self.last_page_wti),
            )

    def parse_wti(self, response, page):
        print(f"Parsing ...wti {page} page", flush=True)
        item = items.MIitems()
        # 원유 스크랩
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(7, 0, -1):
            item['title'] = 'wti'
            item['date'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[1]/text()')
                            .get().replace('\t', '').replace('\n', ''))
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[2]/text()')
                             .get().replace(',', '').replace('\t', '').replace('\n', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=OIL_CL&fdtc=2&page={page - 1}',
                callback=self.parse_wti,
                cb_kwargs=dict(page=page - 1),
            )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_GC&fdtc=2&page={self.last_page_gold}',
                callback=self.parse_gold,
                cb_kwargs=dict(page=self.last_page_gold),
            )

    def parse_gold(self, response, page):
        print(f"Parsing ...gold {page} page", flush=True)
        item = items.MIitems()
        # 금 스크랩
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(7, 0, -1):
            item['title'] = 'gold'
            item['date'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[1]/text()')
                            .get().replace('\t', '').replace('\n', ''))
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[2]/text()')
                             .get().replace(',', '').replace('\t', '').replace('\n', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_GC&fdtc=2&page={page - 1}',
                callback=self.parse_gold,
                cb_kwargs=dict(page=page - 1),
            )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_SI&fdtc=2&page={self.last_page_silver}',
                callback=self.parse_silver,
                cb_kwargs=dict(page=self.last_page_silver),
            )

    def parse_silver(self, response, page):
        print(f"Parsing ...silver {page} page", flush=True)
        item = items.MIitems()
        # 은 스크랩
        time.sleep(WAIT)
        self.logger.info(response.url)
        for i in range(7, 0, -1):
            item['title'] = 'silver'
            item['date'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[1]/text()')
                            .get().replace('\t', '').replace('\n', ''))
            item['value'] = (response.xpath(f'/html/body/div/table/tbody/tr[{i}]/td[2]/text()')
                             .get().replace(',', '').replace('\t', '').replace('\n', ''))
            self.logger.info(f"date : {item['date']}, value : {item['value']}")
            yield item
        if page > 1:
            yield scrapy.Request(
                url=f'https://finance.naver.com/marketindex/worldDailyQuote.nhn?marketindexCd=CMDT_SI&fdtc=2&page={page - 1}',
                callback=self.parse_silver,
                cb_kwargs=dict(page=page - 1),
            )
        else:
            yield scrapy.Request(
                url=f'https://finance.naver.com/world/sise.nhn?symbol=SPI@SPX',
                callback=self.parse_sp500,
                cb_kwargs=dict(page=self.last_page_sp500),
            )

    def parse_sp500(self, response, page):
        print(f"Parsing ...sp500 {page} page", flush=True)
        item = items.MIitems()
        # S&P500을 스크랩하는코드
        time.sleep(WAIT)
        self.logger.info(response.url)
        self.driver.get(response.url)
        time.sleep(WAIT)
        next1 = '//*[@id="dayPaging"]/a[11]'    # 첫페이지의 '다음' 버튼
        next2 = '//*[@id="dayPaging"]/a[12]'    # 첫페이지 이후의 '다음' 버튼
        self.driver.find_element_by_xpath(next1).click()
        time.sleep(WAIT)
        '''
        self.driver.find_element_by_xpath(next2).click()
        time.sleep(1)
        self.driver.find_element_by_xpath(next2).click()
        time.sleep(1)
        self.driver.find_element_by_xpath(next2).click()
        time.sleep(1)
        '''
        for j in range(page, 0, -1):
            if j % 10 == 0:
                prev = '//*[@id="dayPaging"]/a[1]'
                self.driver.find_element_by_xpath(prev).click()
                self.logger.info('click prev...')
                time.sleep(1)
            link = f'//*[@id="dayLink{j}"]'
            while True:
                try:
                    self.driver.find_element_by_xpath(link).click()
                    self.logger.info(f'click {j} button..')
                    break
                except NoSuchElementException as e:
                    self.logger.error(f'Error : {e}')
                    self.driver.find_element_by_xpath(next2).click()
                    time.sleep(1)
            time.sleep(1)
            sel = Selector(text=self.driver.page_source)

            for i in range(10, 0, -1):
                item['title'] = 'sp500'
                item['date'] = sel.xpath(f'//*[@id="dayTable"]/tbody/tr[{i}]/td[1]/text()').get()
                item['value'] = (sel.xpath(f'//*[@id="dayTable"]/tbody/tr[{i}]/td[2]/span/text()')
                                 .get().replace(',', ''))
                self.logger.info(f"date : {item['date']}, value : {item['value']}")
                yield item

    def __del__(self):
        if self.driver is not None:
            print('Retrieve chrome driver...')
            self.driver.quit()
