import time
from scrapy.selector import Selector

from nfs import items
from nfs.spiders import common

# cmd usage : scrapy crawl c104_aq -a code=005930
# 총 8페이지를 스크랩하는 각각의 클래스 존재함.


class C104Base(common.C103C104Base):
    # 개별 C104클래스가 상속하는 기반클래스
    basename = 'c104'

    def parse_c104(self, response, code):
        # html에서 table을 추출하여 dataframe생성
        self.driver.get(response.url)
        time.sleep(self.WAIT)
        html = Selector(text=self.driver.page_source)
        table_xpath = '//table[@class="gHead01 all-width data-list"]'

        # 테이블명을 _을 기준으로 나눠 리스트를 만든다.
        title_list = self.title.split('_')
        self.logger.debug(title_list)

        # dataframe 리스트를 만든다.
        df_list = []
        for i in range(2):
            # 상위테이블 0, 하위테이블 1
            df_list.append(common.C103C104Base.get_df_from_html(html, table_xpath, i))
        self.logger.debug(df_list)

        # 테이블명리스트와 df리스트를 매치하여 데이터베이스에 저장하기 위해 yield시킴
        for title, df in list(zip(title_list, df_list)):
            # df를 log로 출력한다.
            self.logger.info(title)
            self.logger.debug(df)
            # make item to yield
            item = items.C104items()
            item['코드'] = code
            item['title'] = title
            item['df'] = df
            yield item


'''
# XPATH 상수
수익성 = '//*[ @id="val_tab1"]'
성장성 = '//*[ @id="val_tab2"]'
안정성 = '//*[ @id="val_tab3"]'
활동성 = '//*[ @id="val_tab4"]'

연간 = '//*[@id="frqTyp0"]'
분기 = '//*[@id="frqTyp1"]'
검색 = '//*[@id="hfinGubun"]'

가치분석연간 = '//*[@id="frqTyp0_2"]'
가치분석분기 = '//*[@id="frqTyp1_2"]'
가치분석검색 = '//*[@id="hfinGubun2"]'
'''


class C104AQ(C104Base):
    name = 'c104_aq'

    def __init__(self, code):
        super().__init__(code, title='수익성q_가치분석q')

    def click_buttons(self):
        buttons = [
            ('수익성', '//*[ @id="val_tab1"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
            ('가치분석분기', '//*[@id="frqTyp1_2"]'),
            ('가치분석검색', '//*[@id="hfinGubun2"]'),
        ]
        super().click_buttons(buttons)


class C104BQ(C104Base):
    name = 'c104_bq'

    def __init__(self, code):
        super().__init__(code, title='성장성q')

    def click_buttons(self):
        buttons = [
            ('성장성', '//*[ @id="val_tab2"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C104CQ(C104Base):
    name = 'c104_cq'

    def __init__(self, code):
        super().__init__(code, title='안정성q')

    def click_buttons(self):
        buttons = [
            ('안정성', '//*[ @id="val_tab3"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C104DQ(C104Base):
    name = 'c104_dq'

    def __init__(self, code):
        super().__init__(code, title='활동성q')

    def click_buttons(self):
        buttons = [
            ('활동성', '//*[ @id="val_tab4"]'),
            ('분기', '//*[@id="frqTyp1"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C104AY(C104Base):
    name = 'c104_ay'

    def __init__(self, code):
        super().__init__(code, title='수익성y_가치분석y')

    def click_buttons(self):
        buttons = [
            ('수익성', '//*[ @id="val_tab1"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
            ('가치분석연간', '//*[@id="frqTyp0_2"]'),
            ('가치분석검색', '//*[@id="hfinGubun2"]'),
        ]
        super().click_buttons(buttons)


class C104BY(C104Base):
    name = 'c104_by'

    def __init__(self, code):
        super().__init__(code, title='성장성y')

    def click_buttons(self):
        buttons = [
            ('성장성', '//*[ @id="val_tab2"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C104CY(C104Base):
    name = 'c104_cy'

    def __init__(self, code):
        super().__init__(code, title='안정성y')

    def click_buttons(self):
        buttons = [
            ('안정성', '//*[ @id="val_tab3"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)


class C104DY(C104Base):
    name = 'c104_dy'

    def __init__(self, code):
        super().__init__(code, title='활동성y')

    def click_buttons(self):
        buttons = [
            ('활동성', '//*[ @id="val_tab4"]'),
            ('연간', '//*[@id="frqTyp0"]'),
            ('검색', '//*[@id="hfinGubun"]'),
        ]
        super().click_buttons(buttons)
