import time
import random
import pprint
import requests
import math
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from db_hj3415 import mongo
from util_hj3415 import utils
from typing import List
from . import dart, data
from eval_hj3415 import eval

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

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


def 할인률계산(high: float, low: float) -> float:
    logger.info(f'high: {high}, low: {low}')
    try:
        return round((high - low) / high * 100)
    except (ZeroDivisionError, ValueError):
        return float('nan')


def random_sleep():
    # 너무 빠른속도로 스크래핑하면 dart 가 막는다.
    # 랜덤을 추가하여 기본 interval 에 0.5 - 1.5배의 무작위시간을 추가한다.
    interval = 2.5
    logger.info('Wait a moment...')
    time.sleep(interval * (random.random() + .5))


class DartSubject:
    최소유통주식기준 = 10000000  # 발행주식총수가 천만이하면 유통물량 작은편

    MAX_POINT = 10  # judge()에서 반환하는 포인트 최대점수
    NOTI_POINT = 2  # 알림을 하는 최소포인트
    MIN_POINT = 0

    # 상속 클래스에서 sub_url 을 얻기 위한 타이틀을 리스트로 만든다.
    subtitles = []

    def __init__(self, dartinfo: data.DartInfo):
        self.dartinfo = dartinfo
        self.driver = get_driver()
        self.sub_urls = self.get_sub_urls(dartinfo.url)
        self.score = data.PointNOpinion()
        self.data = None

    def get_sub_urls(self, url: str) -> dict:
        """
        dartinfo.url 을 인자로 받아 sub_urls 를 얻어낸다.

        Args:
            url (str): dartinfo.url로 해당 공시의 메인페이지 url

        Returns:
            dict: sub_url 주소를 값으로 하는 딕셔너리
        """
        print('(0) Get sub urls...')
        print(f"init_url : {url}")

        self.driver.implicitly_wait(10)
        self.driver.get(url)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # 화면 좌측의 사이드바 링크(a)를 추출함.
        list_trees = soup.find(id='listTree').find_all('a')
        logger.info(pprint.pformat(list_trees, width=80))

        sub_urls = {}
        if len(list_trees) == 0:
            # 사이드바가 없는 문서의 경우 우측 iframe 주소를 저장한다.
            sub_urls['subtitle'] = self.driver.find_element_by_css_selector('#ifrm').get_attribute('src')
        else:
            for list_tree_one in list_trees:
                logger.info(list_tree_one.text)
                for subtitle in self.subtitles:
                    # 화면의 사이드바에서 찾고자하는 subtitle 을 찾고 있는 경우 클릭한다.
                    if subtitle in str(list_tree_one.text).replace(' ', ''):
                        print(f"\tClick '{list_tree_one.text}' link on the sidebar...")
                        # 화면의 사이드바는 기본으로 접혀있는 상태이기 때문에 펼치는 버튼을 눌러준다.
                        self.driver.find_element_by_css_selector('#wideBtn').click()
                        time.sleep(1)
                        try:
                            # 사이드바를 펼치고 원하는 제목을 클릭한다.
                            self.driver.find_element_by_link_text(list_tree_one.text).click()
                            time.sleep(1)
                        except NoSuchElementException:
                            # 사이드바가 접혀있는 경우에 본에러가 발생하므로 다시 한번 펼치는 버튼을 눌러준다.
                            self.driver.find_element_by_css_selector('#wideBtn').click()
                            time.sleep(1)
                            self.driver.find_element_by_link_text(list_tree_one.text).click()
                            time.sleep(1)
                        sub_urls[subtitle] = self.driver.find_element_by_css_selector('#ifrm').get_attribute('src')
                    else:
                        continue
        pprint.pprint(sub_urls, width=80)
        return sub_urls

    def extract(self):
        print('(1) Extracting data from each sub url pages...')

    @staticmethod
    def _ext_data(html: str, title_n_position: dict, table_keyword: str = '', title_col: int = 0) -> dict:
        """공시 세부 페이지에서 원하는 정보를 얻어 딕셔너리로 반환하는 함수

        self.extract() 에서 내부적으로 사용

        Args:
            html (str): 최종페이지의 html
            title_n_position (dict):
                key (regex): 테이블 내에서 찾고자 하는 타이틀 정규표현식
                value (dict):
                    key (str): 반환할 딕셔너리의 키가 되는 타이틀
                    value(list): 해당 타이틀에서 원하는 값의 위치리스트 [행, 열]
            table_keyword : 페이지에서 테이블이 여러개인 경우 원하는 테이블을 선택하기 위한 테이블 내의 키워드
            title_col : regex 이 테이블의 맨처음에 위치 하지 않을 경우 iloc 의 위치 (0부터 시작)

        Returns:
            dict: 페이지에서 추출된 자료를 딕셔너리로 반환함.
        """
        if table_keyword == '':
            table_df = pd.read_html(html)[0]
        else:
            table_df = pd.read_html(html, match=table_keyword)[0]

        return_dict = {}
        logger.debug(table_df)
        for i, (regex, position_dict) in enumerate(title_n_position.items()):
            logger.debug(f'{i + 1}.Extracting..............{regex}')
            # 테이블에서 맨처음열의 문자열을 비교하여 필터된 데이터 프레임을 반환한다.
            filtered_df = table_df[table_df.iloc[:, title_col].str.contains(regex)]
            logger.info('\n' + filtered_df.to_string())

            # 개발을 위해 로깅하는 코드
            try:
                logger.debug(f'iloc[0,0] : {filtered_df.iloc[0, 0]}')
                logger.debug(f'iloc[0,1] : {filtered_df.iloc[0, 1]}')
                logger.debug(f'iloc[0,2] : {filtered_df.iloc[0, 2]}')
                logger.debug(f'iloc[0,3] : {filtered_df.iloc[0, 3]}')
                logger.debug(f'iloc[0,4] : {filtered_df.iloc[0, 4]}')
                logger.debug(f'iloc[0,5] : {filtered_df.iloc[0, 5]}')
            except IndexError:
                pass

            for title, [row, col] in position_dict.items():
                try:
                    return_dict[title] = filtered_df.iloc[row, col]
                except IndexError:
                    logger.warning(f'IndexError : key - {title}, row - {row}, col - {col}')
                    return_dict[title] = filtered_df.iloc[row, col - 1]
        logger.info(f'_ext_data : {return_dict}')
        return return_dict

    def scoring(self):
        print('(2) Scoring point...')

        # 유통주식이 너무 작으면...
        if self.dartinfo.유통주식 <= self.최소유통주식기준:
            self.score -= 1
            self.score += f"유통주식이 너무 작음 : {utils.to_만(self.dartinfo.유통주식)}주"

    def run(self):
        self.extract()      # sub_url 에서 데이터들을 추출함.
        self.scoring()      # 데이터를 판단해서 point 와 text 를 만든다.

    def __str__(self):
        """
        텔레그렘으로 노티할때 전달되는 형식
        """
        return str(f'<< intro >>\n'
                   f'{self.dartinfo}\n'
                   f'<< data >>\n'
                   f'{self.data}\n'
                   f'<< result >>\n'
                   f'{self.score}')

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()


class 공급계약체결(DartSubject):
    subtitles = []

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.공급계약체결()

    def extract(self):
        super().extract()
        for sub_url in self.sub_urls.values():
            html = requests.get(sub_url).text
            regex_titles = {
                '공급계약': {'공급계약내용': [0, 2]},
                '계약\\s?금액': {'계약금액': [0, 2]},
                '최근\\s?매출액': {'최근매출액': [0, 2]},
                '매출액\\s?대비': {'매출액대비': [0, 2]},
                '시작일': {'시작일': [0, 2]},
                '종료일': {'종료일': [0, 2]},
                '계약\\s?상대': {'계약상대': [0, 2]},
                '주요\\s?계약\\s?조건': {'주요계약조건': [0, 2]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles, title_col=1)
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        계약금액: 2360000000
        계약상대: (주)태민철강
        공급계약내용: 국내 해상고철 납품 계약
        매출액대비: 37.07%
        시작일: 2021-08-31
        종료일: 2021-09-06
        기간: 6일
        주요계약조건: -
        최근매출액: 6366818031
        """
        def cal_comparative_point(big: float, small: float) -> (int, float):
            ratio = ((big / small) - 1) * 100
            a = int(ratio / 10)
            return a if a <= DartSubject.MAX_POINT else DartSubject.MAX_POINT, round(ratio)

        def check_past_contract() -> List[data.공급계약체결]:
            """
            연간 반복 공급계약체결의 경우를 파악하기 위해서 1년전 동일공급계약이 있는지 확인하고 동일한 계약을 찾은 경우\n
            해당 data 딕셔너리를 반환한다.
            :return: 정기계약임이 확인된 과거의 data 딕셔너리
            """
            # 해당 기업의 1년전 주변의 보고서를 검색하여 분석함
            # 과거 동일거래를 찾을때 너무 많이 찾아지는 경우를 위해 기본 455일 - 275일 간격에서 5개 이상의 거래 내역일 경우 30일씩 간격을 줄여 다시 검색한다.
            sdate = 365 + 90
            edate = 365 - 90
            print(f'\t- Searching previous dart reports for checking repetitive contract...Day {sdate} to {edate}')
            report_date = datetime.datetime.strptime(self.dartinfo.rdt, '%Y%m%d')
            dartinfo_list = dart.get_dartinfo_list(
                sdate=(report_date - datetime.timedelta(days=sdate)).strftime('%Y%m%d'),
                edate=(report_date - datetime.timedelta(days=edate)).strftime('%Y%m%d'),
                code=self.dartinfo.code,
                title='공급계약체결'
            )
            while len(dartinfo_list) > 5 and (sdate != edate):
                # 날짜 간격을 한달씩 줄여감
                sdate = sdate - 15
                edate = edate + 15
                print(f'\t- Narrowing search range...Day {sdate} to {edate}\t len(df) : {len(dartinfo_list)}')
                dartinfo_list = dart.get_dartinfo_list(
                    sdate=(report_date - datetime.timedelta(days=sdate)).strftime('%Y%m%d'),
                    edate=(report_date - datetime.timedelta(days=edate)).strftime('%Y%m%d'),
                    code=self.dartinfo.code,
                    title='공급계약체결'
                )
            logger.info(dartinfo_list)
            return_list = []
            for i, dartinfo in enumerate(dartinfo_list):
                past_subject = 공급계약체결(dartinfo=dartinfo)
                past_subject.extract()
                print((f"\t- {i + 1}. Date : {dartinfo.rdt}\t"
                       f"계약상대: {past_subject.data.계약상대}\t"
                       f"계약내용: {past_subject.data.공급계약내용}"), end='')
                # 과거 계약이 현계약 상대방과 동일하면 past_contract 리스트에 추가한다.
                if (past_subject.data.계약상대 == self.data.계약상대
                        and past_subject.data.공급계약내용 == self.data.공급계약내용):
                    if past_subject.data.시작일.year == past_subject.data.종료일.year:
                        # 정기계약이면 해가 달라지지 않을 것이므로 년도를 비교해본다.
                        print(f"\t{past_subject.dartinfo.url}\t===> matching !!!")
                        past_subject.data.date = dartinfo.rdt
                        return_list.append(past_subject.data)
                else:
                    print()
            logger.info(f'past_contract - {return_list}')
            return return_list

        super().scoring()

        if math.isnan(self.data.매출액대비):
            self.score += f"유효하지 않은 매출액대비값 - {self.data.매출액대비}"
            return

        # 매출액 대비가 아무리 높더라도 장기계약일 경우는 의미가 없기때문에 계약기간을 고려하여 재계산해본다.
        if self.data.기간 is None:
            self.score += f"유효하지 않은 날짜(시작일: {self.data.시작일} 종료일: {self.data.종료일})"
            return
        else:
            min_percentage = round((self.data.기간 / 365) * 100)
            print(f"\t계약 시작일과 종료일 차이:{self.data.기간}\t계산된 최소 매출액대비:{min_percentage}")

        # 과거 데이터를 검색하여 유효한 정기공시인지 판단해본다.
        valid_past_contracts = check_past_contract()

        if len(valid_past_contracts) > 0:
            # 과거에 동일 계약상대방이 있었던 정기계약공시면....
            print('\t- Comparing with past contract...')
            print(f'\t{valid_past_contracts}')
            for old_data in valid_past_contracts:
                if math.isnan(old_data.매출액대비):
                    continue
                if self.data.매출액대비 > old_data.매출액대비:
                    p, how_much_big = cal_comparative_point(self.data.매출액대비, old_data.매출액대비)
                    self.score += p
                    # old_data.시작일 = utils.date_to_str(old_data.시작일)
                    # old_data.종료일 = utils.date_to_str(old_data.종료일)
                    self.score += f"과거 동일 거래처 계약보다 {how_much_big}% 큰 거래임 : {old_data}"
                else:
                    self.score += f'과거 동일 거래처 계약보다 작은 거래임 : {old_data}'
        else:
            # 스팟성 공시의 경우
            # 시작일과 종료일의 차를 계산하여 1년이상이면 매출액대비 퍼센트에 반영한다.
            print('\t- Analysing spot contract...')
            if self.data.매출액대비 >= min_percentage:
                p, how_much_big = cal_comparative_point(self.data.매출액대비, min_percentage)
                self.score += p
                self.score += f"공급계약이 기준점({min_percentage}%)보다 {how_much_big}% 큼 : {self.data.매출액대비}%"
            else:
                self.score += f"공급계약이 기준점({min_percentage}%) 미달 : {self.data.매출액대비}%"
        return


class 무상증자결정(DartSubject):
    subtitles = ['무상증자결정', ]

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.무상증자결정(dartinfo=dartinfo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '신주의\\s?종류와\\s?수': {'신주의종류와수': [0, 2]},
                '증자전\\s?발행주식총수': {'증자전발행주식총수': [0, 2]},
                '신주\\s?배정\\s?기준일': {'신주배정기준일': [0, 2]},
                '1주당\\s?신주배정\\s?주식수': {'주당신주배정주식수': [0, 2]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword='증자전\\s?발행주식총수')
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        주당신주배정주식수: 1.0
        신주배정기준일: 2021-09-14
        신주의종류와수: 16452252
        증자전발행주식총수: 16800000
        증자전유통주식: 8957760
        비유통주식: 7842240
        증자후유통주식: 25410012
        """
        # super().scoring() - 증자이기 때문에 증자전 유통주식은 포인트하지 않음.
        print('(2) Scoring point...')

        if self.data.주당신주배정주식수 >= 1:
            self.score += int(self.data.주당신주배정주식수)
            self.score += f"주당배정 신주 : {self.data.주당신주배정주식수}."
        else:
            self.score += f"신주배정부족 : {self.data.주당신주배정주식수}"

        if self.data.증자전유통주식 <= DartSubject.최소유통주식기준 <= self.data.증자후유통주식:
            self.score += 1
            self.score += (f"증자후 유통주식 {utils.to_만(DartSubject.최소유통주식기준)}주 이상임 : "
                           f"{utils.to_만(self.data.증자후유통주식)}주.")
        else:
            self.score -= 1
            self.score += f"증자후 유통주식 부족: {utils.to_만(self.data.증자후유통주식)}주."

        # 신주배정기준일 임박여부 판단
        diff_days = (self.data.신주배정기준일 - datetime.datetime.strptime(self.dartinfo.rdt, '%Y%m%d').date()).days
        try:
            # 신주배정기준일이 현재부터 1달이내인 경우..최대 4 포인트
            self.score += int(120 / diff_days) if int(120 / diff_days) <= 4 else 4
            self.score += f'신주배정일 {diff_days}일 남음.'
        except ZeroDivisionError:
            self.score += f'신주배정일이 오늘임.'
        return


class 자기주식취득결정(DartSubject):
    subtitles = ['자기주식취득결정', ]

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.자기주식취득결정(dartinfo=dartinfo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '취득\\s?예정\\s?주식\\(주\\)': {'취득예정보통주식': [0, 3]},
                '취득\\s?목적': {'취득목적': [0, 3]},
                '취득\\s?방법': {'취득방법': [0, 3]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword='취득\\s?예정\\s?주식')
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        취득목적: 대표이사 및 주요임원에대한 성과보상
        취득방법: 장내매수
        취득예정보통주식: 118489
        보고일기준취득총액: 511872480
        유통주식대비비율: 0.23%
        """
        super().scoring()

        MIN_PCT = 2     # 유통주식의 2% 정도 취득하면 의미있다고 봄

        if math.isnan(self.data.취득예정보통주식) or '상환전환우선주' in self.data.취득목적:
            # 상환전환우선주란 우선주 형태로 가지고 있다가 회사에 다시 팔수 있는 권리를 가진 주식
            self.score += '상환우선주 취득으로 의미 없음'
            return
        if self.data.유통주식대비비율 >= MIN_PCT:
            self.score += int(self.data.유통주식대비비율 - MIN_PCT)
            self.score += f"유통주식대비비율 의미있음({self.data.유통주식대비비율}%)(기준:{MIN_PCT}%)"
        else:
            self.score += f"유통주식대비 너무 적은 취득수량.({self.data.유통주식대비비율}%)(기준:{MIN_PCT}%)"
        return


class 주식등의대량보유상황보고서(DartSubject):
    subtitles = ['주식등의대량보유상황보고서', '대량보유자에관한사항', '변동[변경]사유', '변동내역총괄표', '세부변동내역', ]

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.주식등의대량보유상황보고서()

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            if '변동[변경]사유' in sidebar_title:
                regex_titles = {
                    '변동\\s?방법': {'변동방법': [0, 1]},
                    '변동\\s?사유': {'변동사유': [0, 1]},
                    '변경\\s?사유': {'변경사유': [0, 1]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles)
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)
            elif '대량보유상황보고서' in sidebar_title:
                # .* 의미 - 임의의 문자가 0번이상반복
                regex_titles = {
                    '보고\\s?구분': {'보고구분': [0, 1]},
                    '^보유\\s?주식.*보유\\s?비율$': {'직전보고서': [1, 3], '이번보고서': [2, 3]},
                    '보고\\s?사유': {'보고사유': [0, 1]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword='요약\\s?정보')
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)
            elif '대량보유자에관한사항' in sidebar_title:
                regex_titles = {
                    '보고자\\s?구분': {'보고자구분': [0, 1]},
                    '^성명.*$': {'보고자성명': [0, 2]},
                    '^직업.*$': {'보고자직업': [0, 1]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword='보고자\\s?구분')
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)
            elif '세부변동내역' in sidebar_title:
                table_df = pd.read_html(html, match='^성명.*$')[0]
                # 추출된 테이블이 하나일 경우
                logger.info(f'****** Table No.1 ******')
                logger.info(table_df)
                try:
                    # 단가가 (1,678) 같은 표시형태일 경우 숫자만 추출
                    self.data.평균단가 = round(table_df.iloc[:, 8].str.replace(',', '').str.extract('(\\d+)')
                                           .astype(float).mean(numeric_only=True).iloc[0])
                except AttributeError as e:
                    # 단가가 일반숫자 형태일 경우
                    logger.info(f'AttributeError : {e}')
                    self.data.평균단가 = round(table_df.iloc[:, 8].astype(float).mean())
                except ValueError as e:
                    # 단가가 - 로 표현된 경우
                    logger.info(f'ValueError : {e}')
                    self.data.평균단가 = float('nan')
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        변경사유: 보유주식등에 관한 계약 내용 일부 변경
        변동방법: -
        변동사유: -
        보고구분: 변경
        보고사유: 주요 계약내용의 변경
        보고자구분: 개인(국내)
        보고자성명: 이동채
        보고자직업: 경영인(㈜에코프로 대표이사)
        이번보고서: 18.28
        직전보고서: 18.28
        평균단가: nan
        """
        super().scoring()
       
        할인율 = 할인률계산(self.dartinfo.price, self.data.평균단가)
        # 할인율이 플러스 -> 주가보다 싸게 샀다. -> 주가가 비싸다

        if self.data.직전보고서 >= self.data.이번보고서:
            self.score += f"주식 보유수량 감소 : {self.data.직전보고서} -> {self.data.이번보고서}"
            return
        elif '전환' in self.data.보고사유 or '전환' in self.data.변동사유:
            self.score += f"전환사채 주식 취득"
            if 할인율 < 0:
                self.score += int(abs(할인율) / 5) + 1
                self.score += f"평균단가: {self.data.평균단가} 주가가 {-할인율}% 저렴"
            return
        elif '합병신주' in self.data.보고사유 or '합병신주' in self.data.변동사유:
            self.score += f"합병신주 취득"
            if 할인율 < 0:
                self.score += int(abs(할인율) / 5) + 1
                self.score += f"평균단가: {self.data.평균단가} 주가가 {-할인율}% 저렴"
            return
        elif '상장' in self.data.보고사유 or '상장' in self.data.변동사유:
            return
        elif '유상' in self.data.변동방법 or '유상' in self.data.변동사유:
            return
        elif '잔금지급' in self.data.변동방법 or '잔금지급' in self.data.변동사유:
            return

        if '신규' in self.data.보고구분 or (self.data.직전보고서 + 1.0) < self.data.이번보고서:
            self.score += 1
            self.score += f"의미 있는 신규 주식 취득"
            if 할인율 < 0:
                self.score += int(abs(할인율) / 5) + 1
                self.score += f", 평균단가: {self.data.평균단가} 주가가 {-할인율}% 저렴"
            if '경영' in self.data.보고사유 or '경영' in self.data.변동사유:
                self.score += DartSubject.MAX_POINT / 2
                self.score += f", 경영권 위한 주식 취득"
        return


class 주식소각결정(DartSubject):
    subtitles = []

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.주식소각결정(dartinfo=dartinfo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '소각할\\s?주식의\\s?종류와\\s?수': {'소각할보통주식': [0, 2]},
                '발행주식\\s?총수': {'발행보통주식총수': [0, 2]},
                '소각\\s?예정\\s?금액\\s?\\(원\\)': {'소각예정금액': [0, 2]},
                '소각할\\s?주식의\\s?취득방법': {'소각할주식의취득방법': [0, 2]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles)
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        발행보통주식총수: 21459249
        유통주식총수: 15579415
        소각할보통주식: 2459249
        유통주식대비소각비율: 15.79
        소각예정금액: 5821042383
        소각할주식의취득방법: 기취득 자기주식
        """
        super().scoring()

        MIN_PCT = 3  # 유통주식의 3% 정도 소각하면 의미있다고 봄

        if math.isnan(self.data.소각할보통주식):
            self.score += '주가 제고에 영향 없음'
            return
        elif self.data.소각할보통주식 > 0:
            self.score += 1

        if self.data.유통주식대비소각비율 >= MIN_PCT:
            self.score += int(self.data.유통주식대비소각비율) - MIN_PCT
            self.score += f"유통주식대비 소각비율 의미 있음({self.data.유통주식대비소각비율}%)."
        else:
            self.score += '소각양 미미함'
        return


class 특정증권등소유상황보고서(DartSubject):
    subtitles = ['보고자에관한사항', '특정증권등의소유상황', ]

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.특정증권등소유상황보고서()

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            if '보고자에관한사항' in sidebar_title:
                regex_titles = {
                    '임원\\s?\\(등기여부\\)': {'임원': [0, 2]},
                    '주요주주': {'주요주주': [0, 2]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, title_col=1)
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)
                regex_titles = {
                    '직위명': {'직위명': [0, 4]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, title_col=3)
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)
            elif '특정증권등의소유상황' in sidebar_title:
                # 보고사유는 일반적인 방법으로 추출할 수 없어 따로 추출한다.
                # data 클래스에서 단가를 세밀하게 처리하기 위해서 데이터프레임을 보내준다.
                table_df = pd.read_html(html, match='^보고사유$')[0]
                setattr(self.data, '보고사유', list(set(table_df.iloc[:-1, 0].unique())))
                setattr(self.data, 'df', table_df)

                regex_titles = {
                    '합\\s?계': {'증감': [0, 4], '단가': [0, 6]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword='^보고사유$')
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        단가: 2490
        증감: 5000
        보고사유: ['주식매수청구권 행사(+)']
        임원: 비등기임원
        주요주주: -
        직위명: 이사
        취득처분총액: 12450000
         """

        def check_past_특정증권등소유상황보고서() -> List[data.특정증권등소유상황보고서]:
            report_date = datetime.datetime.strptime(self.dartinfo.rdt, '%Y%m%d')
            old_dartinfo_list = dart.get_dartinfo_list(
                sdate=(report_date - datetime.timedelta(days=DAYS_AGO)).strftime('%Y%m%d'),
                edate=(report_date - datetime.timedelta(days=1)).strftime('%Y%m%d'),
                code=self.dartinfo.code,
                title='특정증권등소유상황보고서'
            )
            print('\tSearching previous dart reports...')
            print(f'\t최근 {DAYS_AGO}일내 임원공시 수: {len(old_dartinfo_list)}')
            logger.info(old_dartinfo_list)
            return_list = []
            for i, old_dartinfo in enumerate(old_dartinfo_list):
                past_subject = 특정증권등소유상황보고서(dartinfo=old_dartinfo)
                past_subject.extract()
                print((f"\t- {i + 1}. Date : {old_dartinfo.rdt}\t"
                       f"계약상대: {past_subject.data.임원}\t"
                       f"계약내용: {past_subject.data.취득처분총액}"), end='')
                if past_subject.data.취득처분총액 >= MIN_BUYING_COST and past_subject.data.임원 == '등기임원':
                    return_list.append(past_subject.data)
                    print(f"\t{past_subject.dartinfo.url}\t===> matching !!!", flush=True)
                else:
                    print()
            logger.info(f'past_contract - {return_list}')
            return return_list

        super().scoring()

        DAYS_AGO = 60  # 등기임원이 1억이상 취득한 케이스 검색 범위 날수
        MIN_BUYING_COST = 100000000  # 등기임원의 최소 주식취득금액 1억

        for reason in self.data.보고사유:
            if ('신규상장' in reason) or ('주식배당' in reason):
                self.score += f"보고사유가 {reason}임."
                return

        if self.data.취득처분총액 >= MIN_BUYING_COST and self.data.임원 == '등기임원':
            # 과거 데이터를 검색하여 유효한 공시인지 판단해본다.
            valid_past_data = check_past_특정증권등소유상황보고서()
            number_of_data = len(valid_past_data)

            if number_of_data > 0:
                self.score += number_of_data
                self.score += f'{DAYS_AGO}일내 {number_of_data}건 등기임원이 {int(MIN_BUYING_COST / 100000000)}억 이상 취득함'
                for past_one in valid_past_data:
                    self.score += str(past_one)
            else:
                self.score += 1
                self.score += f'등기임원이 {utils.to_억(MIN_BUYING_COST)}이상 취득했으나 최근 {DAYS_AGO}일내 유사 케이스 없음.'
        else:
            self.score += f"등기임원이 {utils.to_억(MIN_BUYING_COST)} 이상 구매하지 않음."


class 현물배당결정(DartSubject):
    subtitles = []

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.현물배당결정(dartinfo=dartinfo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '1주당\\s?배당금': {'보통주당배당금': [0, 2], '우선주당배당금': [1, 2]},
                '배당기준일': {'배당기준일': [0, 2]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword='1주당\\s?배당금')
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        배당기준일: 2021-06-30
        보통주당배당금: 1000
        우선주당배당금: nan
        배당성향(2021/12): 77.45%
        보통주배당수익률: 3.42%
         """
        super().scoring()

        MIN_DIV_RATE = 2  # 최하 배당수익률, 금리에 연동
        MEAN_DIV = 20  # 연평균배당성향
        STD_DIV = 15  # 배당성향표준편차

        # 배당기준일 임박여부 판단
        time_delta = self.data.배당기준일 - utils.str_to_date(self.dartinfo.rdt).date()
        if int(time_delta.days) < 0:
            self.score.point = 0
            self.score += f'신주배정일 {abs(int(time_delta.days))}일 지남.\n'
        elif 0 < int(time_delta.days) <= 30:
            self.score += 1
            self.score += f'신주배정일 {int(time_delta.days)}일 남음.\n'

            logger.info(self.data.배당성향)
            if self.data.보통주배당수익률 >= MIN_DIV_RATE:
                self.score += math.ceil(self.data.보통주배당수익률)
                self.score += f'배당수익률 기준({MIN_DIV_RATE}%) 이상.'

            배당성향_s = pd.Series(self.data.배당성향)
            if 배당성향_s.mean() >= MEAN_DIV and 배당성향_s.std() <= STD_DIV:
                self.score += 1
                self.score += f'과거 일관된 배당성향(평균:{round(배당성향_s.mean())}, 표준편차:{round(배당성향_s.std())})\n'


class 자산재평가실시결정(DartSubject):
    subtitles = []

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.자산재평가실시결정()

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '재평가\\s?목적물': {'재평가목적물': [0, 1]},
                '재평가\\s?기준일': {'재평가기준일': [0, 1]},
                '장부가액': {'장부가액': [0, 1]},
                '기타\\s?투자판단': {'기타': [0, 1]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles)
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        super().scoring()

        # 자산재평가는 일단 노티는 해준다.
        self.score += self.NOTI_POINT


class 유상증자결정(DartSubject):
    subtitles = ['유상증자결정', ]

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.유상증자결정()

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            if sidebar_title is None or '유상증자결정' in sidebar_title:
                regex_titles = {
                    r'증자\s?방식': {'증자방식': [0, 2]},
                    r'신주의\s?종류와\s?수': {'신주보통주식': [0, 3]},
                    r'증자전\s?발행주식\s?총수\s?\(주\)': {'증자전보통주식총수': [0, 2]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword=r'신주의\s?종류와\s?수')
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)

                regex_titles = {
                    r'시설\s?자금': {'시설자금': [0, 2]},
                    r'영업\s?양수\s?자금 ': {'영업양수자금': [0, 2]},
                    r'운영\s?자금': {'운영자금': [0, 2]},
                    r'채무\s?상환\s?자금': {'채무상환자금': [0, 2]},
                    r'타법인\s?증권\s?취득\s?자금': {'타법인증권취득자금': [0, 2]},
                    r'기타\s?자금': {'기타자금': [0, 2]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword=r'신주의\s?종류와\s?수', title_col=1)
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)

                regex_titles = {
                    r'신주\s?발행가액': {'신주보통주식발행가': [0, 3]},
                }
                ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword=r'신주\s?발행가액')
                for k, v in ext_dict.items():
                    setattr(self.data, k, v)

                if '3자' in self.data.증자방식:
                    table_df = pd.read_html(html, match=r'최대주주\s?와의\s?관계')[0]
                    logger.info(f'****** Table No.1 ******')
                    logger.info(table_df)
                    logger.info(table_df.to_dict('records'))
                    self.data.제3자배정대상자 = table_df.to_dict('records')
                else:
                    self.data.제3자배정대상자 = []
            random_sleep()
        print(self.data)

    def scoring(self):
        super().scoring()

        if not math.isnan(self.data.신주보통주식발행가):
            보통주할인율 = 할인률계산(self.dartinfo.price, self.data.신주보통주식발행가)
            if 보통주할인율 < 0:
                self.score += int(abs(보통주할인율) / 5) + 1
                self.score += f"신주보통주식발행가: {self.data.신주보통주식발행가} 주가가 {-보통주할인율}% 저렴\n"

        if '3자' in self.data.증자방식:
            for target in self.data.제3자배정대상자:
                # 제3자배정대상자의 키와 밸류의 스페이스를 없애준다.
                target = {k.replace(' ', ''): v for (k, v) in target.items()}
                if '사업제휴' in target['선정경위']:
                    self.score += 2
                    self.score += '투자자와 사업제휴.\n'
                if '투자' in target['제3자배정대상자'] or '자산운용' in target['제3자배정대상자'] or '캐피탈' in target['제3자배정대상자']:
                    self.score += 1
                    self.score += '투자를 위한 증자.\n'


class 매출액또는손익(DartSubject):
    subtitles = []

    def __init__(self, dartinfo: data.DartInfo):
        super().__init__(dartinfo)
        self.data = data.매출액또는손익()

    def extract(self):
        print('(1) Extracting data from each sub url pages...')
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                r'매출액\s?\(': {'당해매출액': [0, 2], '직전매출액': [0, 3], '매출액증감액': [0, 4], '매출액증감비율': [0, 5]},
                '영업이익': {'당해영업이익': [0, 2], '직전영업이익': [0, 3], '영업이익증감액': [0, 4], '영업이익증감비율': [0, 5]},
                '당기순이익': {'당해당기순이익': [0, 2], '직전당기순이익': [0, 3], '당기순이익증감액': [0, 4], '당기순이익증감비율': [0, 5]},
                '자본총계': {'당해자본총계': [0, 2], '직전자본총계': [0, 5]},
                '자본금': {'당해자본금': [0, 2], '직전자본금': [0, 5]},
                r'이사회\s?\결': {'이사회결의일': [0, 2]},
                r'(단위:\s?\w+\s?)': {'단위': [0, 1]},
            }
            ext_dict = DartSubject._ext_data(html, regex_titles, table_keyword=r'변동\s?주요원인')
            for k, v in ext_dict.items():
                setattr(self.data, k, v)
            random_sleep()
        print(self.data)

    def scoring(self):
        """
        당해매출액: 5785608
        직전매출액: 7868321
        매출액증감액: -2082713
        매출액증감비율: -26.5
        당해영업이익: 3670156
        직전영업이익: 4468321
        영업이익증감액: -798165
        영업이익증감비율: -17.9
        당해당기순이익: 1188458
        직전당기순이익: -775358
        당기순이익증감액: 1963816
        당기순이익증감비율: 흑자전환
        당해자본총계: 95861883
        직전자본총계: 97326624
        당해자본금: 20100000
        직전자본금: 20100000
        이사회결의일: 2021-07-06
        당해자본총계/자본금비율: 476.9%
        직전자본총계/자본금비율: 484.2%
        단위: 1000
        """

        def 미결정분계산(c103q: dict, this_y_total: float):
            # 보고서 날짜를 기준으로 당해와 직전해의 연도를 찾아낸다.
            c103q = pd.Series(c103q)
            기준일 = datetime.datetime.strptime(self.dartinfo.rdt, '%Y%m%d')
            올해 = str(기준일.year)
            작년 = str((기준일 - datetime.timedelta(days=365)).year)

            # 올해 결정된 분기만 추려서 합을 낸다.
            올해결정분기_series = c103q[c103q.index.str.contains(str(올해))]
            올해결정치합 = round(올해결정분기_series.sum(), 1)
            # 올해 총합에서 결정된 분기합을 빼서 추정치를 계산한다.
            올해4분기총합 = round(this_y_total * self.data.단위 / 100000000, 1)
            올해추정치합 = round(올해4분기총합 - 올해결정치합, 1)
            logger.info(f'올해: {올해}, 작년: {작년}, 올해4분기총합: {올해4분기총합}')
            logger.info(c103q.to_dict())
            logger.info(f"올해추정치합({올해추정치합}) = 올해4분기총합({올해4분기총합}) - 올해결정치합({올해결정치합})")

            미결정분기수 = 4 - len(올해결정분기_series)
            작년결정분기_series = c103q[c103q.index.str.contains(str(작년))]
            작년추정치합 = round(작년결정분기_series[-미결정분기수:].sum(), 1)
            logger.info(f"작년추정치합({작년추정치합})")
            try:
                ratio = round(((올해추정치합 - 작년추정치합) / abs(작년추정치합)) * 100, 1)
                logger.info(f"{round(ratio, 1)} = 올해추정치합({올해추정치합}) - 작년추정치합({작년추정치합}) / 작년추정치합({작년추정치합}) * 100")
            except ZeroDivisionError:
                ratio = float('nan')
            return 작년추정치합, 올해추정치합, ratio

        super().scoring()

        # 직전에 자본총계/자본금비율이 50% 이하이었다가 이번에 50% 이상이 되었다면 관리종목탈피
        if self.data.직전자본총계자본금비율 < 50 <= self.data.당해자본총계자본금비율:
            self.score += 2
            self.score += '관리종목탈피 요건성립(자본총계/자본금 비율 50%이상).'

        # 전체 순이익을 판단하기 보다 직전 분기 또는 미발표 분기를 분석하기 위한 코드

        c103손익계산서q = mongo.C103(code=self.dartinfo.code, page='c103손익계산서q')

        c103_매출액q = c103손익계산서q.find(title='매출액(수익)')
        c103_영업이익q = c103손익계산서q.find(title='영업이익')
        c103_당기순이익q = c103손익계산서q.find(title='당기순이익')

        매출액작년추정치합, 매출액올해추정치합, 매출액ratio = 미결정분계산(c103_매출액q, self.data.당해매출액)
        영업이익작년추정치합, 영업이익올해추정치합, 영업이익ratio = 미결정분계산(c103_영업이익q, self.data.당해영업이익)
        당기순이익작년추정치합, 당기순이익올해추정치합, 당기순이익ratio = 미결정분계산(c103_당기순이익q, self.data.당해당기순이익)
        logger.info(f'매출액 : {매출액작년추정치합} {매출액올해추정치합} {매출액ratio}')
        logger.info(f'영업이익 : {영업이익작년추정치합} {영업이익올해추정치합} {영업이익ratio}')
        logger.info(f'당기순이익 : {당기순이익작년추정치합} {당기순이익올해추정치합} {당기순이익ratio}')

        ratios = []
        if not math.isnan(매출액ratio) and not math.isinf(매출액ratio):
            ratios.append(매출액ratio)
        if not math.isnan(영업이익ratio) and not math.isinf(영업이익ratio):
            ratios.append(영업이익ratio)
        if not math.isnan(당기순이익ratio) and not math.isinf(당기순이익ratio):
            ratios.append(당기순이익ratio)
        logger.info(ratios)
        self.data.미발표분증감율 = ratios

        if len(ratios) > 0:
            avg = round(sum(ratios) / len(ratios), 1)
            if avg >= 15:
                self.score += int(avg / 15)
                # 15%이상 변동이 의미 있어서 15로 결정
                self.score += f'미발표 분기의 평균 {avg}% 재무구조의 개선 있음.'

                tpoint = 0
                if not math.isnan(매출액ratio) and not math.isnan(self.data.매출액증감비율):
                    if 매출액ratio > self.data.매출액증감비율:
                        tpoint += 1
                if not math.isnan(영업이익ratio) and not math.isnan(self.data.영업이익증감비율):
                    if 영업이익ratio > self.data.영업이익증감비율:
                        tpoint += 1
                if not math.isnan(당기순이익ratio) and not math.isnan(self.data.당기순이익증감비율):
                    if 당기순이익ratio > self.data.당기순이익증감비율:
                        tpoint += 1
                if tpoint > 0:
                    self.score += f'미발표 분기 증가율이 발표분보다 높다.'
                self.score += tpoint
