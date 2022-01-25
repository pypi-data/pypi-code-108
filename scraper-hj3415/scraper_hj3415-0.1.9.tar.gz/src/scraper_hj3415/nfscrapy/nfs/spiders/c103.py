import time
from scrapy.selector import Selector

from nfs import items
from nfs.spiders import common


# cmd usage : scrapy crawl c103_bq -a code=005930
# 총 6페이지를 스크랩하는 각각의 클래스 존재함.


class C103Base(common.C103C104Base):
    # 개별 C103클래스가 상속하는 기반클래스
    basename = 'c103'

    def parse_c103(self, response, code):
        # html에서 table을 추출하여 dataframe생성
        self.driver.get(response.url)
        time.sleep(self.WAIT)
        html = Selector(text=self.driver.page_source)
        table_xpath = '//table[2]'
        df = common.C103C104Base.get_df_from_html(html, table_xpath, 1)
        self.logger.debug(df)

        # make item to yield
        item = items.C103items()
        item['코드'] = code
        item['title'] = self.title
        item['df'] = df
        yield item


'''
# XPATH 상수
손익계산서 = '//*[@id="rpt_tab1"]'
재무상태표 = '//*[@id="rpt_tab2"]'
현금흐름표 = '//*[@id="rpt_tab3"]'
연간 = '//*[@id="frqTyp0"]'
분기 = '//*[@id="frqTyp1"]'
검색 = '//*[@id="hfinGubun"]'
'''


class C103BQ(C103Base):
    name = 'c103_bq'

    def __init__(self, code):
        super().__init__(code, title='재무상태표q')

    def click_buttons(self):
        buttons = [
            ('재무상태표', '//*[@id="rpt_tab2"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C103CQ(C103Base):
    name = 'c103_cq'

    def __init__(self, code):
        super().__init__(code, title='현금흐름표q')

    def click_buttons(self):
        buttons = [
            ('현금흐름표', '//*[@id="rpt_tab3"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C103IQ(C103Base):
    name = 'c103_iq'

    def __init__(self, code):
        super().__init__(code, title='손익계산서q')

    def click_buttons(self):
        buttons = [
            ('손익계산서', '//*[@id="rpt_tab1"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C103BY(C103Base):
    name = 'c103_by'

    def __init__(self, code):
        super().__init__(code, title='재무상태표y')

    def click_buttons(self):
        buttons = [
            ('재무상태표', '//*[@id="rpt_tab2"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C103CY(C103Base):
    name = 'c103_cy'

    def __init__(self, code):
        super().__init__(code, title='현금흐름표y')

    def click_buttons(self):
        buttons = [
            ('현금흐름표', '//*[@id="rpt_tab3"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C103IY(C103Base):
    name = 'c103_iy'

    def __init__(self, code):
        super().__init__(code, title='손익계산서y')

    def click_buttons(self):
        buttons = [
            ('손익계산서', '//*[@id="rpt_tab1"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


