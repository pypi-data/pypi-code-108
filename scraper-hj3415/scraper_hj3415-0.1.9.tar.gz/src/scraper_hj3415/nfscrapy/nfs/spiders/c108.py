import scrapy
import pandas as pd

from nfs import items
from nfs.spiders import common

# cmd usage : scrapy crawl c108 -a code=005930


class C108Spider(scrapy.Spider):
    name = 'c108'
    allowed_domains = ['navercomp.wisereport.co.kr']    # https 주소

    def __init__(self, code):
        super().__init__()
        self.codes = common.make_list(code)

    def start_requests(self):
        total_count = len(self.codes)
        print(f'Start scraping {self.name}, {total_count} items...')
        self.logger.info(f'entire codes list - {self.codes}')
        for i, one_code in enumerate(self.codes):
            print(f'\t{i + 1}/{total_count}. Parsing {self.name}...{one_code}')
            # reference from https://docs.scrapy.org/en/latest/topics/request-response.html
            yield scrapy.Request(url=f'https://navercomp.wisereport.co.kr/v2/company/c1080001.aspx?cmp_cd={one_code}',
                                 callback=self.parse_c108,
                                 cb_kwargs=dict(code=one_code)
                                 )

    def parse_c108(self, response, code):
        """
            C108 분석한 XPATH
            date_XPATH = f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[1]'               # 날짜
            content_XPATH = f'//*[@id="td{i}"]/@data-content'                               # 제목과내용
            author_XPATH = f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[3]/div'         # 작성자
            company_XPATH = f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[4]/div'        # 제공처
            opinion_XPATH = f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[5]/div[1]'     # 투자의견
            hprice_XPATH = f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[6]/div[1]'      # 목표가
        """
        # c108페이지가 아직 만들어진 경우 빈테이블을 만들어 저장한다.
        title = response.xpath('/html/head/title/text()').get()
        if title == '기업재무정보 접속장애':
            self.logger.warning(f'{code}: None C108 data...We will make empty table..')
            # make item to yield
            item = items.C108items()
            item['코드'] = code
            item['df'] = pd.DataFrame(columns=['날짜', '제목', '작성자', '제공처', '투자의견', '목표가', '내용'])
            yield item
            return

        # reference from http://hleecaster.com/python-pandas-creating-and-loading-dataframes/(데이터프레임 만들기)
        opinions = []
        # 표의 아이템 갯수는 최대 20개
        for i in range(20):
            one_opinion = list()
            # 1. 날짜추가
            one_opinion.append(response.xpath(f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[1]/text()').get())
            # 제목과 내용을 추출한 리스트에서 제목따로 내용따로 추출
            try:
                title_and_contents = response.xpath(f'//*[@id="td{i}"]/@data-content').get()\
                    .replace("<br/><span class='comment_text'>▶</span>", '▶').split('\n')
                self.logger.debug(title_and_contents)
            except AttributeError:
                break
            # 2. 제목을 추출하고 리스트에서 지움
            one_opinion.append(title_and_contents[0])
            del title_and_contents[0]
            # 3. 작성자, 제공처, 투자의견, 목표가를 차례로 추출하고 리스트에 추가
            for j in range(3, 7):
                one_opinion.append(response.xpath(f'//*[@id="tableCmpDetail"]/tr[{(i * 2) + 1}]/td[{j}]/div/text()')
                                   .get().replace('\t', '').replace('\r\n', ''))
            # 4. 내용을 추출하고 개행문자를 첨가함
            contents = ''
            for item in title_and_contents:
                contents += item
            one_opinion.append(contents)
            self.logger.debug(one_opinion)
            # 5. 완성된 row를 opinions리스트에 넣는다.
            opinions.append(one_opinion)
        self.logger.info(f'\ttotal {len(opinions)} opinions.. {code}')

        df = pd.DataFrame(data=opinions, columns=['날짜', '제목', '작성자', '제공처', '투자의견', '목표가', '내용'])
        df['내용'] = df['내용'].str.replace('\r', '')

        self.logger.debug(df)
        # make item to yield
        item = items.C108items()
        item['코드'] = code
        item['df'] = df
        yield item

    def __str__(self):
        return 'C108 Spider'
