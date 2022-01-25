import scrapy
import time
import pandas as pd

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


# 커맨드라인에서 스파이더를 실행할 경우 인자형식이 str 이 되기 때문에 list 로 변경해주는 함수
def make_list(code) -> list:
    if type(code) is str:
        return [code, ]
    elif type(code) is list:
        return code
    else:
        raise TypeError


class C103C104Base(scrapy.Spider):
    # C103Base, C104Base가 상속하는 기반클래스
    basename = None
    allowed_domains = ['navercomp.wisereport.co.kr']
    WAIT = 1.5

    def __init__(self, code, title):
        super().__init__()
        self.codes = make_list(code)
        self.driver = get_driver()
        if self.driver is None:
            raise
        self.title = title  # ex- 재무상태표q

    def start_requests(self):
        # reference from https://docs.scrapy.org/en/latest/topics/request-response.html
        total_count = len(self.codes)
        print(f'Start scraping {self.basename} {self.title}, {total_count} codes...', flush=True)
        self.logger.info(f'entire codes list - {self.codes}')

        # 페이지를 먼저 한번 호출하여 버튼을 눌러 세팅한다.
        self.click_buttons()

        # 실제로 페이지를 스크랩하기위해 호출
        for i, one_code in enumerate(self.codes):
            print(f'\t{i + 1}/{total_count}. Parsing {self.title}...{one_code}')
            yield scrapy.Request(
                url=f'https://navercomp.wisereport.co.kr/v2/company/{self.basename}0001.aspx?cmp_cd={one_code}',
                callback=getattr(self, f'parse_{self.basename}'),
                cb_kwargs=dict(code=one_code)
            )

    def click_buttons(self, buttons):
        url = f'https://navercomp.wisereport.co.kr/v2/company/{self.basename}0001.aspx?cmp_cd='
        # 하부 클래스에서 buttons 리스트를 입력받아 실제 버튼을 클릭하는 함수
        self.logger.info(f'*** Setting {self.title} page by clicking buttons ***')
        self.driver.get(url)
        for name, xpath in buttons:
            self.logger.debug(f'- Click the {name} button')
            self.driver.find_element_by_xpath(xpath).click()
            time.sleep(self.WAIT)
        self.logger.info('*** Buttons click done ***')

    @staticmethod
    def get_df_from_html(selector, xpath, table_num):
        # C103,C104에서 사용
        # 펼치지 않은 네이버 테이블의 항목과 내용을 pandas 데이터프레임으로 변환시킴
        # reference from http://hleecaster.com/python-pandas-selecting-data/(pandas 행열 선택)
        # reference from https://blog.naver.com/wideeyed/221603778414(pandas 문자열 처리)
        # reference from https://riptutorial.com/ko/pandas/example/5745/dataframe-%EC%97%B4-%EC%9D%B4%EB%A6%84-%EB%82%98%EC%97%B4(pandas 열이름 나열)
        # 전체 html source에서 table 부위만 추출하여 데이터프레임으로 변환
        tables_list = selector.xpath(xpath).getall()
        # print(tables_list[table_num])
        df = pd.read_html(tables_list[table_num])[0]
        # 항목열의 펼치기 스트링 제거
        df['항목'] = df['항목'].str.replace('펼치기', '').str.strip()
        # reference from https://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex(정규표현식 특수기호처리)
        # 인덱스행의 불필요한 스트링 제거
        df.columns = (df.columns.str.replace('연간컨센서스보기', '', regex=False).str.replace('연간컨센서스닫기', '', regex=False)
                      .str.replace('\(IFRS연결\)', '', regex=True).str.replace('\(IFRS별도\)', '', regex=True).str.replace(
            '\(GAAP개별\)', '', regex=True)
                      .str.replace('\(YoY\)', '', regex=True).str.replace('\(QoQ\)', '', regex=True).str.replace(
            '\(E\)', '', regex=True)
                      .str.replace('.', '', regex=False).str.strip())
        return df

    def __str__(self):
        return ''.join([f'{self.basename} Spider', self.title])

    def __del__(self):
        if self.driver is not None:
            print('Retrieve chrome driver...')
            self.driver.quit()
