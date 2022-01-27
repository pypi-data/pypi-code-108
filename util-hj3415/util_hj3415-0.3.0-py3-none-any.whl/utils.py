import math
import re
import datetime
import requests
import socket
from bs4 import BeautifulSoup
import random

from selenium import webdriver
import selenium.webdriver.chrome.webdriver
from webdriver_manager.chrome import ChromeDriverManager


from krx_hj3415 import krx

import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


def to_float(s) -> float:
    """
    인자의 예 '1432', '1,432', '23%', 1432
    인자를 실수형으로 변환하고 불가능하면 nan을 리턴한다.
    """

    def is_digit(str):
        # reference from http://seorenn.blogspot.com/2011/04/python-isdigit.html 음수 is_digit()
        try:
            tmp = float(str)
            return True
        except (ValueError, TypeError):
            return False

    logger.debug(f'to_float : {s}')

    if is_digit(s):
        return float(s)
    elif is_digit(str(s).replace(',', '').replace('%', '')):
        return float(s.replace(',', '').replace('%', ''))
    else:
        return float('nan')


def to_int(s):
    t = to_float(s)
    if math.isnan(t):
        return t
    else:
        return int(t)


def deco_num(s):
    # 숫자형 인수를 받아서 천단위에 컴마가 붙은 문자열로 반환한다.
    t = to_int(s)
    return None if s is None or math.isnan(t) else format(t, ",")


def to_억(v) -> str:
    """
    유동형식 인자를 입력받아 float으로 바꿔 nan이면 '-'리턴 아니면 '억'을 포함한 읽기쉬운 숫자 문자열로 반환
    """
    logger.debug(f'to_억 : {v}')
    float_v = to_float(v)
    if math.isnan(float_v):
        return '-'
    else:
        return str(round(float_v / 100000000, 1)) + '억'


def to_만(v) -> str:
    """
    유동형식 인자를 입력받아 float으로 바꿔 nan이면 '-'리턴 아니면 '만'을 포함한 읽기쉬운 숫자 문자열로 반환
    """
    logger.debug(f'to_만 : {v}')
    float_v = to_float(v)
    if math.isnan(float_v):
        return '-'
    else:
        return str(int(float_v / 10000)) + '만'


def get_kor_amount(amount: int, omit: str = '', str_suffix: str = '원') -> str:
    """숫자를 자릿수 한글 단위와 함께 리턴한다

    Args:
        amount (int): 한글형을 바꾸고 싶은 정수형 숫자
        omit (str): 잔돈을 자르고 싶은 경우 단위. ['억', '천만', '만', '천', '']
        str_suffix (str): 금액 문미에 붙을 접미사

    Notes:
        https://m.blog.naver.com/wideeyed/221771836059
    """
    assert isinstance(amount, int)
    assert omit in ['억', '천만', '만', '천', '']
    assert amount >= 1, '최소 1원 이상 입력되어야 합니다'

    if omit == '억':
        ndigits_round = -8
    elif omit == '천만':
        ndigits_round = -7
    elif omit == '만':
        ndigits_round = -4
    elif omit == '천':
        ndigits_round = -3
    else:
        ndigits_round = 0

    # 일, 십, 백, 천, 만, 십, 백, 천, 억, ... 단위 리스트를 만든다.
    maj_units = ['만', '억', '조', '경', '해']  # 10000 단위
    units = [' ']  # 시작은 일의자리로 공백으로하고 이후 십, 백, 천, 만...
    for mm in maj_units:
        units.extend(['십', '백', '천'])  # 중간 십,백,천 단위
        units.append(mm)

    list_amount = list(str(round(amount, ndigits_round)))  # 라운딩한 숫자를 리스트로 바꾼다
    logger.info(list_amount)
    list_amount.reverse()  # 일, 십 순서로 읽기 위해 순서를 뒤집는다

    str_result = ''  # 결과
    num_len_list_amount = len(list_amount)

    for i in range(num_len_list_amount):
        str_num = list_amount[i]
        # 만, 억, 조 단위에 천, 백, 십, 일이 모두 0000 일때는 생략
        if num_len_list_amount >= 9 and i >= 4 and i % 4 == 0 and ''.join(list_amount[i:i + 4]) == '0000':
            continue
        if str_num == '0':  # 0일 때
            if i % 4 == 0:  # 4번째자리일 때(만, 억, 조...)
                str_result = units[i] + str_result  # 단위만 붙인다
        elif str_num == '1':  # 1일 때
            if i % 4 == 0:  # 4번째자리일 때(만, 억, 조...)
                str_result = str_num + units[i] + str_result  # 숫자와 단위를 붙인다
            else:  # 나머지자리일 때
                str_result = units[i] + str_result  # 단위만 붙인다
        else:  # 2~9일 때
            str_result = str_num + units[i] + str_result  # 숫자와 단위를 붙인다
    str_result = str_result.strip()  # 문자열 앞뒤 공백을 제거한다
    if len(str_result) == 0:
        return ''
    # if not str_result[0].isnumeric():  # 앞이 숫자가 아닌 문자인 경우
    #     str_result = '1' + str_result  # 1을 붙인다
    return str_result + str_suffix  # 접미사를 붙인다


def str_to_date(d: str) -> datetime.datetime:
    """
    다양한 형태의 날짜 문자열을 날짜형식으로 변환
    '2021년 04월 13일'
    '2021/04/13'
    '2021-04-13'
    '2021.04.13'
    '20210413'
    """
    r = re.compile('^(20[0-9][0-9])[가-힣/.\-]?([0,1][0-9])[가-힣/.\-]?([0-3][0-9])[가-힣/.\-]?$')
    try:
        Ymd = "".join(re.findall(r, d.replace(' ', ''))[0])
    except IndexError:
        # 입력문자열이 날짜형식이 아닌경우 - ex) '-'
        return d
    return datetime.datetime.strptime(Ymd, '%Y%m%d')


def date_to_str(d: datetime.datetime, sep: str = '-') -> str:
    """
    datetime 형식을 %Ysep%msep%d형식으로 반환
    """
    s = d.strftime('%Y%m%d')
    if sep is None:
        return s
    else:
        return s[0:4] + sep + s[4:6] + sep + s[6:8]


def isYmd(date: str) -> bool:
    """
    date 인자의 형식이 Ymd 인지 확인

    Args:
        date (str): 날자 형태의 문자열

    Example:
        True : 20101120
        False : 2010.11.20
    """
    # date 형식여부 확인
    p = re.compile('^20[0-9][0-9][0,1][0-9][0-3][0-9]$')
    if p.match(date) is None:
        return False
    return True


def isY_slash_m(date: str) -> bool:
    """
    date 인자의 형식이 Y/m 인지 확인

    Args:
        date (str): 날자 형태의 문자열

    Example:
        True : 2010/11
        False : 2010.11
    """
    p = re.compile('^20[0-9][0-9]/[0,1][0-9]$')
    if p.match(date) is None:
        return False
    return True


def is_6digit(word: str) -> bool:
    # 파일명이 숫자6자리로 되어있는지 검사하여 참거짓 반환
    p = re.compile('^\d\d\d\d\d\d$')
    m = p.match(word)
    if m:
        return True
    else:
        return False


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'From': 'hj3415@hanmail.net'
}


def scrape_simple_data(url, selector):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    logger.info(soup.select(selector))
    try:
        raw_data = soup.select(selector)[0]
    except IndexError:
        return ''
    data = re.sub(r'<.+?>', '', str(raw_data).replace('\t', '').replace('\n', ''))
    return data


def get_price_now(code: str) -> tuple:
    """해당 코드의 현재가 조회

    code 에 해당하는 현재 시세를 조회하여 (현재가, 전일비, updown) 튜플을 반환한다.

    Returns:
        tuple: (현재가:int, 전일비:int, 'up' or 'down':str)
    """
    # 현재 시세를 조회한다.
    url = f"https://finance.naver.com/item/sise_day.nhn?code={code}&page=1"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 현재가 추출
    raw_data = soup.select(f'body > table.type2 > tr:nth-child(3) > td:nth-child(2) > span')
    try:
        현재가 = int(re.sub(r'\<.+?\>', '', str(raw_data).strip('[]').replace('\n', '').replace(',', '')))
    except ValueError:
        logger.error(f'현재가 에러 : {code} -> return 0, 0, None')
        return 0, 0, None

    # 전일비 추출
    raw_data = soup.select(f'body > table.type2 > tr:nth-child(3) > td:nth-child(3) > span')
    try:
        전일비 = int(re.sub(r'\<.+?\>', '', str(raw_data).strip('[]').replace('\n', '').replace(',', '')))
    except ValueError:
        logger.error(f'전일비 에러 : {code} -> return {현재가}, 0, None')
        return 현재가, 0, None

    # 상승, 하락 추출
    try:
        # red02 or nv01
        raw_data = soup.select('body > table.type2 > tr:nth-child(3) > td:nth-child(3) > span')[0]['class'][2]
        if raw_data == 'red02':
            updown = 'up'
        elif raw_data == 'nv01':
            updown = 'down'
        else:
            updown = None
    except IndexError:
        # none인 경우
        updown = None

    return 현재가, 전일비, updown


def get_ip_addr() -> str:
    """
    cybos에서 소켓통신을 위해서 아이피를 알아낼때 사용
    """
    # https://www.delftstack.com/howto/python/get-ip-address-python/
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def pick_rnd_x_code(count: int) -> list:
    # 임의의 갯수의 종목코드를 뽑아서 반환한다.
    return random.sample(krx.get_codes(), count)


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