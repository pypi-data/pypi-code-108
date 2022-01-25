import re
import time
import pandas as pd
import requests
from util_hj3415 import noti, utils
from db_hj3415 import mongo
from . import data


import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


URL = 'https://opendart.fss.or.kr/api/list.json'
# crtfc_key - 발급받은 인증키(40자리)
KEY = '?crtfc_key=f93473130995a146c3e9e7b250b0f4d4c4dc1513'


def islive_opendart() -> bool:
    """Check opendart alive

    https://opendart.fss.or.kr/ 의 연결여부 확인

    Returns:
        bool: 연결 여부에 따라 True, False 반환

    Note:
        연결오류시 텔레그램으로 오류 메시지 전송함.
    """
    try:
        m = requests.get(''.join([URL, KEY]), timeout=3).json()
        if m['status'] != '000':
            noti.telegram_to(botname='dart', text=m['message'])
            logger.error(m)
            return False
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        err_str = "Connection Error on opendart.fss.or.kr.."
        logger.error(err_str)
        noti.telegram_to(botname='dart', text=err_str)
        return False
    return True


def make_full_url(sdate: str, edate: str, code: str, title: str, page_no: int = 1) -> str:
    """

    인자에 해당하는 조건의 최종 url을 반환한다.

    Args:
        sdate (str): 검색시작날자 %Y%m%d
        edate (str): 검색종료날자 %Y%m%d
        code (str): 종목코드 6자리 숫자형 문자열
        title (str): dart 타이틀
        page_no (str): 페이지번호

    Returns:
        str: 최종 생성된 url 문자열열

    Note:
        &last_reprt_at : 최종보고서만 검색여부(Y or N) 기본값 : N
        &pblntf_ty : 공시유형
    """
    def find_title_type(title: str) -> str:
        """공시유형결정

        타이틀을 기반으로 공시유형을 결정해서 반환한다.

        Args:
            title (str): 공시 타이틀

        Returns:
            str: 결정된 공시유형

        Note:
            공시유형 - A : 정기공시\n
            B : 주요사항보고\n
            C : 발행공시\n
            D : 지분공시\n
            E : 기타공시\n
            F : 외부감사관련\n
            G : 펀드공시\n
            H : 자산유동화\n
            I : 거래소공시\n
            J : 공정위공시\n
        """
        logger.debug('<<<  _match_title_with_title_code() >>>')
        if title == '':
            title_type = ''
        elif title in ['분기보고서', '반기보고서', '사업보고서']:
            title_type = 'A'  # 정기공시
        elif title in ['무상증자결정', '자기주식취득결정', '자기주식처분결정', '유상증자결정', '전환사채권발행결정',
                       '신주인수권부사채권발행결정', '교환사채권발행결정', '회사합병결정', '회사분할결정']:
            title_type = 'B'  # 주요사항보고
        elif title in ['공급계약체결', '주식분할결정', '주식병합결정', '주식소각결정', '만기전사채취득', '신주인수권행사',
                       '소송등의', '자산재평가실시결정', '현물배당결정', '주식배당결정', '매출액또는손익', '주주총회소집결의']:
            title_type = 'I'  # 거래소공시
        elif title in ['공개매수신고서', '특정증권등소유상황보고서', '주식등의대량보유상황보고서']:
            title_type = 'D'  # 지분공시
        else:
            raise
        return title_type

    # 모든 인자를 생략할 경우 오늘 날짜의 공시 url를 반환한다.
    logger.info('<<<  make_full_url() >>>')
    logger.info(f'corp_code : {code}\ttitle_code : {title}\tstart_date : {sdate}\tend_date : {edate}')

    title_type = find_title_type(title)

    # 최종 url을 만들기 위한 문장 요소들
    is_last = f'&last_reprt_at=Y'
    page_no = f'&page_no={page_no}'
    page_count = f'&page_count=100'
    start_date = f'&bgn_de={sdate}' if utils.isYmd(sdate) else ''
    end_date = f'&end_de={edate}' if utils.isYmd(edate) else ''
    corp_code = f'&corp_code={code}' if utils.is_6digit(code) else ''

    pblntf_ty = f'&pblntf_ty={title_type}' if title_type != '' else ''

    final_url = URL + KEY + is_last + page_no + page_count + start_date + end_date + corp_code + pblntf_ty
    print(f'final url : {final_url}')

    return final_url


def make_dart_list(full_url: str) -> list:
    """full_url에 해당하는 딕셔너리를 포함하는 리스트를 반환함.

    첫번째 페이지 final url로 반환된 딕셔너리의 status 값을 체크하는 함수

    Args:
        full_url (str): make_full_url()로 만들어진 첫번째 페이지 url

    Returns:
        list: 각 페이지의 r_dict['list'] 의 값을 모아서 반환하는 리스트

    Note:
        << status: message 값 >>
        - 000 : 	정상\n
        - 010 : 	등록되지 않은 키입니다.\n
        - 011 : 	사용할 수 없는 키입니다. 오픈API에 등록되었으나, 일시적으로 사용 중지된 키를 통하여 검색하는 경우 발생합니다.\n
        - 013 :     조회된 데이타가 없습니다.\n
        - 020 : 	요청 제한을 초과하였습니다.\n
                    일반적으로는 10,000건 이상의 요청에 대하여 이 에러 메시지가 발생되나, 요청 제한이 다르게 설정된 경우에는 이에 준하여 발생됩니다.\n
        - 100 : 	필드의 부적절한 값입니다. 필드 설명에 없는 값을 사용한 경우에 발생하는 메시지입니다.\n
        - 800 : 	원활한 공시서비스를 위하여 오픈API 서비스가 중지 중입니다.\n
        - 900 : 	정의되지 않은 오류가 발생하였습니다.\n

        << r_dict 값 >>
        {'status': '000',\n
        'message': '정상',\n
        'page_no': 1,\n
        'page_count': 100,\n
        'total_count': 134,\n
        'total_page': 2,\n
        'list': [\n
            {'corp_code': '01550070',\n
            'corp_name': '동백철강',\n
            'stock_code': '',\n
            'corp_cls': 'E',\n
            'report_nm': '최대주주등의주식보유변동',\n
            'rcept_no': '20210802000085',\n
            'flr_nm': '동백철강',\n
            'rcept_dt': '20210802', 'rm': '공'},... ]}\n

    """
    r_dict = requests.get(full_url).json()
    status = r_dict['status']
    message = r_dict['message']
    total_page = r_dict['total_page']

    if status != '000':
        err_str = f"Error message on dart - {message}"
        logger.error(err_str)
        noti.telegram_to(botname='dart', text=err_str)
        return []

    return_list = []
    print(f'Extracting all pages({total_page}) ', end='')
    p = re.compile('&page_no=[0-9]+')
    for i in range(total_page):
        each_page_url = p.sub(f'&page_no={i + 1}', full_url)
        print(f'{i + 1}..', end='')
        return_list += requests.get(each_page_url).json()['list']
        time.sleep(1)
    print(f'\nMaking the list involving the dart dictionaries : total {len(return_list)} items')
    return return_list


def convert_dart_list_to_df(items_list: list) -> pd.DataFrame:
    """dart 딕셔너리를 포함하는 리스트를 데이터프레임으로 변환.

    corp_cls는 법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타)의 값을 가질수 있다.
    우리는 Y와 K만 필요하기 때문에 데이터프레임을 만들기전 필터링한다.

    Args:
        items_list (list): dart 딕셔너리를 포함하는 리스트

    Returns:
        pd.Dataframe: 변환된 데이터프레임

    Note:
        << item_list 구조 >>\n
        [{'corp_cls': 'K',\n
        'corp_code': '00261887',\n
        'corp_name': '티엘아이',\n
        'flr_nm': '코스닥시장본부',\n
        'rcept_dt': '20210802',\n
        'rcept_no': '20210802900146',\n
        'report_nm': '조회공시요구(풍문또는보도)',\n
        'rm': '코',\n
        'stock_code': '062860'},....]\n
    """
    # 전체데이터에서 Y(유가증권),K(코스닥)만 고른다.
    # reference by https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#selection-by-callable
    yk_df = pd.DataFrame(items_list).loc[lambda df: df['corp_cls'].isin(['Y', 'K']), :]
    print(f'Making the dataframe removing unnessasary corp_cls value - N(코넥스), E(기타) : total {len(yk_df)} items')
    return yk_df


def filtering_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """ dart 데이터프레임에서 특정한 단어가 포함된 타이틀을 필터링함.

    """
    filter_words = ['기재정정', '첨부정정', '자회사의', '종속회사의', '기타경영사항']
    for word in filter_words:
        df = df[~df['report_nm'].str.contains(word)]
    print(f'Filtering the dataframe removing unnessasary titles - {filter_words} : total {len(df)} items')
    return df


def get_df(sdate: str = '', edate: str = '', code: str = '', title: str = '', filtering: bool = True) -> pd.DataFrame:
    """인자로 입력된 조건에 맞는 dart 데이터프레임을 생성하여 반환한다.

    모든 인자를 생략하면 오늘 날짜의 dart를 검색하여 데이터프레임을 반환한다.

    Args:
        sdate (str): 검색시작날자 %Y%m%d
        edate (str): 검색종료날자 %Y%m%d
        code (str): 종목코드 6자리 숫자형 문자열
        title (str): dart 타이틀
        filtering (bool): ['기재정정', '첨부정정', '자회사의', '종속회사의', '기타경영사항'] 를 뺄지 말지

    """
    if not islive_opendart():
        # opendart 서버가 다운된 경우
        return pd.DataFrame()
    else:
        try:
            full_url = make_full_url(sdate, edate, code, title)
            item_list = make_dart_list(full_url)
            df = convert_dart_list_to_df(item_list)
        except:
            return pd.DataFrame()

        if filtering:
            df = filtering_dataframe(df)

        if title != '':
            # 타이틀을 인자로 넣은 경우
            df = df[df['report_nm'].str.contains(title)]
            print(f'Filtering the dataframe involving the word {title} : total {len(df)} items')
        return df


def get_dartinfo_list(sdate: str = '', edate: str = '', code: str = '', title: str = '', filtering: bool = True) -> list:
    """
    analysis에서 사용하는 data.DartInfo 클래스의 리스트를 반환한다.
    내부적으로 get_df()를 이용해 데이터프레임을 생성하고 c101의 데이터를 추가하여 합하여 만든다.
    """
    df = get_df(sdate=sdate, edate=edate, code=code, title=title, filtering=filtering)
    logger.info(df)
    dartinfo_list = []
    for namedtuple in df.itertuples():
        dartinfo = data.DartInfo()

        # dart 로부터 데이터를 채운다.
        dartinfo.code = namedtuple.stock_code
        dartinfo.name = namedtuple.corp_name
        dartinfo.rtitle = namedtuple.report_nm
        dartinfo.rno = namedtuple.rcept_no
        dartinfo.rdt = namedtuple.rcept_dt
        dartinfo.url = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + str(namedtuple.rcept_no)

        # c101 로부터 데이터를 채운다.
        try:
            c101 = mongo.C101(code=namedtuple.stock_code).get_recent()
            dartinfo.price = utils.to_int(c101['주가'])
            dartinfo.per = c101['PER'] if c101['PER'] is not None else None
            dartinfo.pbr = c101['PBR'] if c101['PBR'] is not None else None
            dartinfo.high_52w = utils.to_int(c101['최고52주'])
            dartinfo.low_52w = utils.to_int(c101['최저52주'])
        except StopIteration:
            # 해당코드의 c101이 없는 경우
            dartinfo.price = None
            dartinfo.per = None
            dartinfo.pbr = None
            dartinfo.high_52w = None
            dartinfo.low_52w = None

        dartinfo_list.append(dartinfo)
    logger.info(dartinfo_list)
    return dartinfo_list
