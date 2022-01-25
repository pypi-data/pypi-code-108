import scrapy
from nfs import items
from nfs.spiders import common

# cmd usage : scrapy crawl c101 -a code=005930

# 여러 잡다한 기호를 없어거나 교체하는 람다함수
cleaning = lambda s: (
    s.strip().replace('\t', '').replace('\r', '').replace('\n', '').replace(',', '').replace('원', '')
    .replace('주', '').replace('억', '00000000').replace('%', '') if s is not None and s != 'N/A' else None
)
css_path = lambda i, j: f'#pArea>div.wrapper-table>div>table>tr:nth-child({i})>td>dl>dt:nth-child({j})>'
css_path2 = lambda i: f'#cTB11>tbody>tr:nth-child({i})>'
str_or_blank = lambda  i: '' if i is None else str(i)


class C101Spider(scrapy.Spider):
    name = 'c101'
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
            yield scrapy.Request(url=f'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={one_code}',
                                 callback=self.parse_c101,
                                 cb_kwargs=dict(code=one_code),
                                 )

    def parse_c101(self, response, code):
        item = items.C101items()
        try:
            item['date'] = response.xpath('//*[ @ id = "wrapper"]/div[1]/div[1]/div[1]/dl/dd[2]/p/text()')\
                .get().replace('[기준:', '').replace(']', '')
        except AttributeError:
            self.logger.error(f'ERROR : Page not found...{code}')
            return None
        item['종목명'] = response.css(css_path(1, 1) + 'span::text').get()
        item['코드'] = cleaning(response.css(css_path(1, 1) + 'b::text').get())
        item['업종'] = response.css(css_path(1, 4).rstrip('>') + '::text').get().replace('WICS : ', '')
        item['EPS'] = cleaning(response.css(css_path(3, 1) + 'b::text').get())
        item['BPS'] = cleaning(response.css(css_path(3, 2) + 'b::text').get())
        item['PER'] = cleaning(response.css(css_path(3, 3) + 'b::text').get())
        item['업종PER'] = cleaning(response.css(css_path(3, 4) + 'b::text').get())
        item['PBR'] = cleaning(response.css(css_path(3, 5) + 'b::text').get())
        item['배당수익률'] = cleaning(response.css(css_path(3, 6) + 'b::text').get())
        item['주가'] = cleaning(response.css(css_path2(1) + 'td>strong::text').get())
        item['최고52주'], item['최저52주'] = map(cleaning, response.css(css_path2(2) + 'td::text').get().split('/'))
        item['거래량'], item['거래대금'] = map(cleaning, response.css(css_path2(4) + 'td::text').get().split('/'))
        item['시가총액'] = cleaning(response.css(css_path2(5) + 'td::text').get())
        item['베타52주'] = cleaning(response.css(css_path2(6) + 'td::text').get())
        item['발행주식'], item['유통비율'] = map(cleaning, response.css(css_path2(7) + 'td::text').get().split('/'))

        item['intro1'] = str_or_blank(response.xpath('// *[ @ id = "wrapper"] / div[5] / div[2] / ul / li[1] / text()').get())
        item['intro2'] = str_or_blank(response.xpath('// *[ @ id = "wrapper"] / div[5] / div[2] / ul / li[2] / text()').get())
        item['intro3'] = str_or_blank(response.xpath('// *[ @ id = "wrapper"] / div[5] / div[2] / ul / li[3] / text()').get())

        self.logger.info(item)
        yield item