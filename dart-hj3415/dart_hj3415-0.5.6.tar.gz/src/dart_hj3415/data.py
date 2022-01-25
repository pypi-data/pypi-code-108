import re
import datetime
import pprint
import math
import pandas as pd

from util_hj3415 import utils
from db_hj3415 import mongo

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class NotiAndAnal:
    def __init__(self):
        self.date = ''
        self.notified = []
        self.analysed = []

    def __str__(self):
        s = f'date: {self.date}\n'
        s += f'notified : {self.notified}\n'
        s += f'analysed : {self.analysed}\n'
        return s


class PointNOpinion:
    def __init__(self):
        self.point = 0
        self.__opinion_list = []

    @property
    def opinion(self):
        return ' '.join(self.__opinion_list)

    def __iadd__(self, other):
        if isinstance(other, int):
            self.point += other
        elif isinstance(other, str):
            self.__opinion_list.append(other)
        else:
            raise TypeError
        return self

    def __isub__(self, other):
        if isinstance(other, int):
            self.point -= other
        else:
            raise TypeError
        return self

    def __str__(self):
        s = f'Point : {self.point}\n'
        for i, opinion in enumerate(self.__opinion_list):
            s += f'{i+1}.{opinion}\n'
        return s


def 유통주식계산(code: str, date: str) -> float:
    """
    c101에서 date에 해당하는 날짜의 유통주식을 계산하고 만약 그날짜가 없으면 최신날짜로 유통주식을 계산한다.\n
    :param code: ex - 005930
    :param date: ex - 20211011
    :return:
    """
    if not utils.is_6digit(code) or not utils.isYmd(date):
        raise ValueError(f'Invalid values - {code}/{date}')
    # c101을 통해서 실제 유통주식의 수를 반환한다.
    c101_db = mongo.C101(code=code)
    c101_dict = c101_db.find(date=date)
    if c101_dict is None:
        c101_dict = c101_db.get_recent()

    logger.info(pprint.pformat(f'c101 : {c101_dict}', width=80))

    try:
        return round((float(c101_dict['유통비율']) / 100) * float(c101_dict['발행주식']))
    except ValueError:
        return float('nan')


class DartInfo:
    def __init__(self,
                 code: str = '',
                 name: str = '',
                 rtitle: str = '',
                 rno: str = '',
                 rdt: str = '',
                 url: str = '',
                 price: int = 0,
                 per: float = 0.0,
                 pbr: float = 0.0,
                 high_52w: int = 0,
                 low_52w: int = 0):
        self.__code = code
        self.name = name
        self.rtitle = rtitle
        self.rno = rno
        self.__rdt = rdt
        self.url = url
        self.price = price
        self.per = per
        self.pbr = pbr
        self.high_52w = high_52w
        self.low_52w = low_52w
        if self.__code != '' and self.__rdt != '':
            self.유통주식 = 유통주식계산(code=self.__code, date=self.__rdt)
        else:
            self.유통주식 = None

    @property
    def code(self) -> str:
        return self.__code

    @code.setter
    def code(self, code):
        if utils.is_6digit(code):
            self.__code = code
            if self.__code != '' and self.__rdt != '':
                self.유통주식 = 유통주식계산(code=self.__code, date=self.__rdt)
        else:
            raise ValueError(f'Invalid code - {code}')

    @property
    def rdt(self) -> str:
        return self.__rdt

    @rdt.setter
    def rdt(self, rdt):
        if utils.isYmd(rdt):
            self.__rdt = rdt
            if self.__code != '' and self.__rdt != '':
                self.유통주식 = 유통주식계산(code=self.__code, date=self.__rdt)
        else:
            raise ValueError(f'Invalid date - {rdt}')

    def __str__(self):
        s = f'코드: {self.code}\t종목명: {self.name}\n'
        s += f'rtitle: {self.rtitle}\n'
        s += f'rno: {self.rno}\n'
        s += f'rdt: {self.rdt}\n'
        s += f'url: {self.url}\n'
        s += f'price: {self.price}\thigh_52w: {self.high_52w}\tlow_52w: {self.low_52w}\n'
        s += f'per: {self.per}\tpbr: {self.pbr}\n'
        s += f'유통주식: {self.유통주식}'
        return s


class 공급계약체결:
    """
    {'계약금액': '64900000000',
    '계약상대': '(주)포스코건설',
    '공급계약내용': '신안산선 복선전철 민간투자사업 3-2공구',
    '매출액대비': '22.36',
    '시작일': '2021-02-24',
    '종료일': '2025-04-09',
    '주요계약조건': '토공 및 구조물공사',
    '최근매출액': '290210341264'}
    """
    def __init__(self):
        self.__계약금액 = float('nan')
        self.계약상대 = ''
        self.공급계약내용 = ''
        self.__매출액대비 = float('nan')
        self.__시작일 = None
        self.__종료일 = None
        self.기간 = None
        self.주요계약조건 = ''
        self.__최근매출액 = float('nan')

    @property
    def 계약금액(self) -> int:
        return utils.to_int(self.__계약금액)

    @계약금액.setter
    def 계약금액(self, 계약금액):
        self.__계약금액 = utils.to_int(계약금액)

    @property
    def 매출액대비(self) -> float:
        return self.__매출액대비

    @매출액대비.setter
    def 매출액대비(self, 매출액대비):
        self.__매출액대비 = utils.to_float(매출액대비)

    @property
    def 시작일(self) -> datetime.date:
        return self.__시작일

    @시작일.setter
    def 시작일(self, 시작일: str):
        if 시작일 == '-' or 시작일 == '':
            self.__시작일 = None
            self.기간 = None
        else:
            self.__시작일 = datetime.datetime.strptime(시작일, '%Y-%m-%d').date()
            if self.__시작일 is not None and self.__종료일 is not None:
                self.기간 = (self.__종료일 - self.__시작일).days

    @property
    def 종료일(self) -> datetime.date:
        return self.__종료일

    @종료일.setter
    def 종료일(self, 종료일: str):
        if 종료일 == '-' or 종료일 == '':
            self.__종료일 = None
            self.기간 = None
        else:
            self.__종료일 = datetime.datetime.strptime(종료일, '%Y-%m-%d').date()
            if self.__시작일 is not None and self.__종료일 is not None:
                self.기간 = (self.__종료일 - self.__시작일).days

    @property
    def 최근매출액(self) -> int:
        return utils.to_int(self.__최근매출액)

    @최근매출액.setter
    def 최근매출액(self, 최근매출액):
        self.__최근매출액 = utils.to_int(최근매출액)

    def __str__(self):
        def days_to_yd(days: int) -> str:
            # 기간을 정수로 입력받아 몇년 몇일의 문자열로 반환하는 함수
            if days is None or math.isnan(days):
                return ''
            y, d = divmod(days, 365)
            if y == 0:
                return f'{d}일'
            else:
                return f'{y}년 {d}일'

        s = f'계약금액: {self.계약금액}\n'
        s += f'계약상대: {self.계약상대}\n'
        s += f'공급계약내용: {self.공급계약내용}\n'
        s += f'매출액대비: {self.매출액대비}%\n'
        s += f'시작일: {self.시작일}\n'
        s += f'종료일: {self.종료일}\n'
        s += f'기간: {days_to_yd(self.기간)}\n'
        s += f'주요계약조건: {self.주요계약조건}\n'
        s += f'최근매출액: {self.최근매출액}\n'
        return s


class 무상증자결정:
    """
    {'1주당신주배정주식수': '0.5',
     '신주배정기준일': '2021년 04월 13일',
     '신주의종류와수': '12335217',
     '증자전발행주식총수': '24670435'}
    """
    def __init__(self, dartinfo: DartInfo):
        self.__주당신주배정주식수 = float('nan')
        self.__신주배정기준일 = None
        self.__신주의종류와수 = float('nan')
        self.__증자전발행주식총수 = float('nan')

        self.증자전유통주식 = dartinfo.유통주식
        self.비유통주식 = float('nan')
        self.증자후유통주식 = float('nan')

    @property
    def 주당신주배정주식수(self) -> float:
        return self.__주당신주배정주식수

    @주당신주배정주식수.setter
    def 주당신주배정주식수(self, 주당신주배정주식수):
        self.__주당신주배정주식수 = utils.to_float(주당신주배정주식수)

    @property
    def 신주배정기준일(self) -> datetime.date:
        return self.__신주배정기준일

    @신주배정기준일.setter
    def 신주배정기준일(self, 신주배정기준일: str):
        if 신주배정기준일 == '-' or 신주배정기준일 == '':
            self.__신주배정기준일 = None
        else:
            self.__신주배정기준일 = datetime.datetime.strptime(신주배정기준일.replace(' ', ''), '%Y년%m월%d일').date()

    @property
    def 신주의종류와수(self) -> int:
        return utils.to_int(self.__신주의종류와수)

    @신주의종류와수.setter
    def 신주의종류와수(self, 신주의종류와수):
        self.__신주의종류와수 = utils.to_int(신주의종류와수)
        if not math.isnan(self.증자전유통주식) and not math.isnan(self.__신주의종류와수):
            self.증자후유통주식 = int(self.증자전유통주식 + self.__신주의종류와수)

    @property
    def 증자전발행주식총수(self) -> int:
        return utils.to_int(self.__증자전발행주식총수)

    @증자전발행주식총수.setter
    def 증자전발행주식총수(self, 증자전발행주식총수):
        self.__증자전발행주식총수 = utils.to_int(증자전발행주식총수)
        if not math.isnan(self.__증자전발행주식총수) and not math.isnan(self.증자전유통주식):
            self.비유통주식 = int(self.__증자전발행주식총수 - self.증자전유통주식)

    def __str__(self):
        s = f'주당신주배정주식수: {self.주당신주배정주식수}\n'
        s += f'신주배정기준일: {self.신주배정기준일}\n'
        s += f'신주의종류와수: {self.신주의종류와수}\n'
        s += f'증자전발행주식총수: {self.증자전발행주식총수}\n'
        s += f'증자전유통주식: {self.증자전유통주식}\n'
        s += f'비유통주식: {self.비유통주식}\n'
        s += f'증자후유통주식: {self.증자후유통주식}\n'
        return s


class 자기주식취득결정:
    """
    {'취득목적': '주주가치 제고 및 주가안정',
     '취득방법': '코스닥시장을 통한 장내 직접 취득',
     '취득예정기타주식': '-',
     '취득예정보통주식': '400000'}
    """
    def __init__(self, dartinfo: DartInfo):
        self.dartinfo = dartinfo
        self.취득목적 = ''
        self.취득방법 = ''
        self.__취득예정보통주식 = float('nan')
        self.보고일기준취득총액 = float('nan')
        self.유통주식대비비율 = float('nan')

    @property
    def 취득예정보통주식(self) -> int:
        return utils.to_int(self.__취득예정보통주식)

    @취득예정보통주식.setter
    def 취득예정보통주식(self, 취득예정보통주식):
        self.__취득예정보통주식 = float('nan') if 취득예정보통주식 == '-' else utils.to_float(취득예정보통주식)

        # 보고일기준취득총액 계산
        if math.isnan(self.__취득예정보통주식) or math.isnan(self.dartinfo.price):
            self.보고일기준취득총액 = utils.to_int(float('nan'))
        else:
            self.보고일기준취득총액 = utils.to_int(self.__취득예정보통주식 * self.dartinfo.price)

        # 유통주식대비비율 계산
        try:
            self.유통주식대비비율 = round((self.__취득예정보통주식 / self.dartinfo.유통주식) * 100, 2)
        except ZeroDivisionError:
            self.유통주식대비비율 = float('nan')

    def __str__(self):
        s = f'취득목적: {self.취득목적}\n'
        s += f'취득방법: {self.취득방법}\n'
        s += f'취득예정보통주식: {self.취득예정보통주식}\n'
        s += f'보고일기준취득총액: {self.보고일기준취득총액}\n'
        s += f'유통주식대비비율: {self.유통주식대비비율}%\n'
        return s


class 주식등의대량보유상황보고서:
    """
    {'변경사유': '-',
     '변동방법': '코스닥시장 신규상장',
     '변동사유': '특별관계자 보유주식등 변동(특수관계자 변동 및 주식매수선택권 행사)',
     '보고구분': '변동',
     '보고사유': '특별관계자 보유주식등 변동(특수관계자 변동 및 주식매수선택권 행사)',
     '보고자구분': '개인(국내)',
     '보고자성명': '김효기',
     '보고자직업': '주식회사 셀레믹스 대표이사',
     '이번보고서': '9.84',
     '직전보고서': '11.49',
     '평균단가': 8333}
    """
    def __init__(self):
        self.변경사유 = ''
        self.변동방법 = ''
        self.변동사유 = ''
        self.보고구분 = ''
        self.보고사유 = ''
        self.보고자구분 = ''
        self.보고자성명 = ''
        self.보고자직업 = ''
        self.__이번보고서 = float('nan')
        self.__직전보고서 = float('nan')
        self.평균단가 = float('nan')

    @property
    def 이번보고서(self) -> float:
        return self.__이번보고서

    @이번보고서.setter
    def 이번보고서(self, 이번보고서):
        self.__이번보고서 = utils.to_float(이번보고서)

    @property
    def 직전보고서(self) -> float:
        return self.__직전보고서

    @직전보고서.setter
    def 직전보고서(self, 직전보고서):
        self.__직전보고서 = utils.to_float(직전보고서)

    def __str__(self):
        s = f'변경사유: {self.변경사유}\n'
        s += f'변동방법: {self.변동방법}\n'
        s += f'변동사유: {self.변동사유}\n'
        s += f'보고구분: {self.보고구분}\n'
        s += f'보고사유: {self.보고사유}\n'
        s += f'보고자구분: {self.보고자구분}\n'
        s += f'보고자성명: {self.보고자성명}\n'
        s += f'보고자직업: {self.보고자직업}\n'
        s += f'이번보고서: {self.이번보고서}\n'
        s += f'직전보고서: {self.직전보고서}\n'
        s += f'평균단가: {self.평균단가}'
        return s


class 주식소각결정:
    """
    {'발행보통주식총수': '117401592',
     '소각예정금액': '4998510065',
     '소각할보통주식': '1895607',
     '소각할주식의취득방법': '기취득 자기주식'}
    """
    def __init__(self, dartinfo: DartInfo):
        self.__발행보통주식총수 = float('nan')
        self.__소각예정금액 = float('nan')
        self.__소각할보통주식 = float('nan')
        self.소각할주식의취득방법 = ''
        self.유통주식총수 = dartinfo.유통주식
        self.유통주식대비소각비율 = float('nan')

    @property
    def 발행보통주식총수(self) -> int:
        return utils.to_int(self.__발행보통주식총수)

    @발행보통주식총수.setter
    def 발행보통주식총수(self, 발행보통주식총수):
        self.__발행보통주식총수 = utils.to_int(발행보통주식총수)

    @property
    def 소각예정금액(self) -> int:
        return utils.to_int(self.__소각예정금액)

    @소각예정금액.setter
    def 소각예정금액(self, 소각예정금액):
        self.__소각예정금액 = utils.to_int(소각예정금액)

    @property
    def 소각할보통주식(self) -> int:
        return utils.to_int(self.__소각할보통주식)

    @소각할보통주식.setter
    def 소각할보통주식(self, 소각할보통주식):
        self.__소각할보통주식 = utils.to_int(소각할보통주식)

        # 유통주식대비소각비율 계산
        try:
            self.유통주식대비소각비율 = round((self.__소각할보통주식 / self.유통주식총수) * 100, 2)
        except ZeroDivisionError:
            self.유통주식대비소각비율 = float('nan')

    def __str__(self):
        s = f'발행보통주식총수: {self.발행보통주식총수}\n'
        s += f'유통주식총수: {self.유통주식총수}\n'
        s += f'소각할보통주식: {self.소각할보통주식}\n'
        s += f'유통주식대비소각비율: {self.유통주식대비소각비율}%\n'
        s += f'소각예정금액: {self.소각예정금액}\n'
        s += f'소각할주식의취득방법: {self.소각할주식의취득방법}'
        return s


class 특정증권등소유상황보고서:
    """
    {'단가': nan,
     '보고사유': ['신규상장(+)'],
     '임원': '등기임원',
     '주요주주': '사실상지배주주',
     '증감': 871860,
     '직위명': '대표이사'}
    """
    def __init__(self):
        self.__단가 = float('nan')
        self.__증감 = float('nan')
        self.보고사유 = []
        self.임원 = ''
        self.주요주주 = ''
        self.직위명 = ''

        self.취득처분총액 = float('nan')

        # 단가를 세밀하게 처리하기 위해 <특정증권등의 소유사항 -> 세부변동내역> 표를 데이터프레임으로 저장한다.
        self.df = pd.DataFrame()

    @property
    def 단가(self) -> int:
        return utils.to_int(self.__단가)

    @단가.setter
    def 단가(self, 합계행의단가):
        """
        이상한 단가의 예들
        '4,999,998,600( 1주당 1,800'
        '34,813( 주1)'
        '754,000(75,400)'
        '13.01'
        '취득(1,147)'
        """

        # 합계행의 단가 평가 - nan의 경우 평균단가를 산출해본다.
        s = str(합계행의단가).replace(' ', '').replace(',', '').replace('1주당', '').replace('주1', '')
        r = r'\d+'
        num_list = re.findall(r, s)
        if len(num_list) == 0:
            # 숫자형식을 추출하지 못했다면...
            합계행의단가 = float('nan')
        elif len(num_list) == 2:
            if (int(num_list[0]) % int(num_list[1])) == 0:
                # '754,000(75,400)' 의 경우
                합계행의단가 = utils.to_float(num_list[1])
            else:
                # '13.01' 의 소수점의 경우
                합계행의단가 = float('.'.join(re.findall(r, s)))
        elif len(num_list) == 1:
            합계행의단가 = utils.to_float(num_list[0])
        else:
            # 기타 - 리스트 아이템 개수가 3개 이상인 경우등...
            합계행의단가 = float('nan')

        # 합계행에서 단가를 구할수 없으면 수동으로 각행의 증감과 단가를 계산하여 평균단가를 산출해본다.
        if math.isnan(합계행의단가):
            if len(self.df) == 0:
                raise ValueError('Please set 세부변동내역 dataframe first..')

            # 증감(4열)과 단가(6열)의 시리즈
            # 마지막 합계행을 빼기 위해 :-1을 사용하고 에러시 NaN을 반환하기 위해 coerce 사용
            증감_s = pd.to_numeric(self.df.iloc[:-1, 4], errors='coerce')
            단가_s = pd.to_numeric(self.df.iloc[:-1, 6], errors='coerce')
            # 각행별로 증감과 단가의 곱셈을한 각각을 전체 더한다.여기에 전체 증감합으로 나누면 평균단가가 계산된다.
            증감_mul_단가 = 증감_s * 단가_s
            logger.info(f'각 행별 증감*단가\n{증감_mul_단가.to_string()}')
            증감합 = 증감_s.sum()
            증감_mul_단가합 = 증감_mul_단가.sum()
            logger.info(f'증감열의 전체합: {증감합}')
            logger.info(f'증감*단가의 전체합: {증감_mul_단가합}')
            try:
                평균단가 = utils.to_float(증감_mul_단가합 / 증감합)
            except:
                평균단가 = float('nan')
            logger.info(f"평균단가 : {평균단가}")
            self.__단가 = 평균단가
        else:
            self.__단가 = 합계행의단가

        if not math.isnan(self.__증감) and not math.isnan(self.__단가):
            self.취득처분총액 = utils.to_int(self.__증감 * self.__단가)

        """
        - 단가 nan인 경우 임의로 현재 주가를 단가로 설정했던 코드.. 
        if math.isnan(self.data['단가']):
            # 숫자가 아닌경우 - '-','-(-)'등..
            print(f"\tTrying to set 단가... {self.dartinfo.price}원")
            self.data['취득처분총액'] = round(self.data['증감'] * self.dartinfo.price, 1)
            # 단가가 숫자가 아닌경우 최근주가를 기반으로 계산하기 때문에 **를 붙여준다.
            self.data['단가'] = str(self.dartinfo.price) + '**'
        else:
            self.data['취득처분총액'] = utils.to_int(self.data['증감'] * self.data['단가'])
        """

    @property
    def 증감(self) -> int:
        return utils.to_int(self.__증감)

    @증감.setter
    def 증감(self, 증감):
        self.__증감 = utils.to_int(증감)
        if not math.isnan(self.__증감) and not math.isnan(self.__단가):
            self.취득처분총액 = utils.to_int(self.__증감 * self.__단가)

    def __str__(self):
        s = f'단가: {self.단가}\n'
        s += f'증감: {self.증감}\n'
        s += f'보고사유: {self.보고사유}\n'
        s += f'임원: {self.임원}\n'
        s += f'주요주주: {self.주요주주}\n'
        s += f'직위명: {self.직위명}\n'
        s += f'취득처분총액: {self.취득처분총액}'
        return s


class 현물배당결정:
    """
    {'배당기준일': '2020-12-31',
     '보통주당배당금': '300',
     '우선주당배당금': '305'}
    """
    def __init__(self, dartinfo: DartInfo):
        self.dartinfo = dartinfo
        self.__배당기준일 = None
        self.__보통주당배당금 = float('nan')
        self.__우선주당배당금 = float('nan')
        # 현금배당성향이란 순이익중 배당금으로 지급된 금액을 말함
        self.배당성향 = mongo.C104(code=self.dartinfo.code, page='c104y').find(title='현금배당성향(%)')
        self.보통주배당수익률 = 0.0

    @property
    def 배당기준일(self) -> datetime.date:
        return self.__배당기준일

    @배당기준일.setter
    def 배당기준일(self, 배당기준일: str):
        if 배당기준일 == '-' or 배당기준일 == '':
            self.__배당기준일 = None
        else:
            self.__배당기준일 = datetime.datetime.strptime(배당기준일, '%Y-%m-%d').date()

    @property
    def 보통주당배당금(self) -> int:
        return utils.to_int(self.__보통주당배당금)

    @보통주당배당금.setter
    def 보통주당배당금(self, 보통주당배당금):
        self.__보통주당배당금 = utils.to_int(보통주당배당금)
        try:
            self.보통주배당수익률 = round((self.__보통주당배당금 / self.dartinfo.price) * 100, 2)
        except ZeroDivisionError:
            self.보통주배당수익률 = float('nan')

    @property
    def 우선주당배당금(self) -> int:
        return utils.to_int(self.__우선주당배당금)

    @우선주당배당금.setter
    def 우선주당배당금(self, 우선주당배당금):
        self.__우선주당배당금 = utils.to_int(우선주당배당금)

    def __str__(self):
        s = f'배당기준일: {self.배당기준일}\n'
        s += f'보통주당배당금: {self.보통주당배당금}\n'
        s += f'우선주당배당금: {self.우선주당배당금}\n'
        s += f'배당성향: {self.배당성향}\n'
        s += f'보통주배당수익률: {self.보통주배당수익률}%'
        return s


class 자산재평가실시결정:
    """
    {'재평가목적물': '토지',
    '재평가기준일': '2021-03-31',
    '장부가액': '402580148773',
    '기타': '1.자산재평가의 목적 - K-IFRS(한국채택국제회계기준)에 의거 자산의 실질가치 반영 - 자산 및 자본증대효과를 통한 재무구조 개선
            2. 상기 장부가액은 2020년 12월 31일 기준입니다.'}
    """
    def __init__(self):
        self.재평가목적물 = ''
        self.__재평가기준일 = None
        self.__장부가액 = float('nan')
        self.기타 = ''

    @property
    def 재평가기준일(self) -> datetime.date:
        return self.__재평가기준일

    @재평가기준일.setter
    def 재평가기준일(self, 재평가기준일: str):
        if 재평가기준일 == '-' or 재평가기준일 == '':
            self.__재평가기준일 = None
        else:
            self.__재평가기준일 = datetime.datetime.strptime(재평가기준일.replace(' ', ''), '%Y-%m-%d').date()

    @property
    def 장부가액(self) -> int:
        return utils.to_int(self.__장부가액)

    @장부가액.setter
    def 장부가액(self, 장부가액):
        self.__장부가액 = utils.to_int(장부가액)

    def __str__(self):
        s = f'재평가목적물: {self.재평가목적물}\n'
        s += f'재평가기준일: {self.재평가기준일}\n'
        s += f'장부가액: {self.장부가액}\n'
        s += f'기타: {self.기타}'
        return s


class 유상증자결정:
    """
    {'증자방식': '제3자배정증자',
    '신주보통주식': '-',
    '신주기타주식': '1325380',
    '증자전보통주식총수': '30385009',
    '증자전기타주식총수': '-',
    '시설자금': '-',
    '운영자금': '9999992100',
    '채무상환자금': '-',
    '타법인증권취득자금': '-',
    '신주보통주식발행가': '-',
    '신주기타주식발행가': '7545',
    '제3자배정대상자': [{'제3자배정 대상자': '(주)뉴그린',
                        '회사 또는최대주주와의 관계': '-',
                        '선정경위': '투자자의 의향 및 납입능력, 시기 등을 고려하여 배정 대상자를 선정함',
                        '증자결정 전후 6월이내 거래내역 및 계획': '-',
                        '배정주식수 (주)': 662690,
                        '비 고': '주권교부일로부터 1년간 전량 의무보유예탁할 예정임.'},
                    {'제3자배정 대상자': '김형순',
                        '회사 또는최대주주와의 관계': '-',
                        '선정경위': '〃',
                        '증자결정 전후 6월이내 거래내역 및 계획': '-',
                        '배정주식수 (주)': 662690,
                        '비 고': '〃'}]}
    """
    def __init__(self):
        self.증자방식 = ''
        self.__신주보통주식 = float('nan')
        self.증자전보통주식총수 = ''

        # 자금조달의 목적
        self.시설자금 = 0
        self.영업양수자금 = 0
        self.운영자금 = 0
        self.채무상환자금 = 0
        self.타법인증권취득자금 = 0
        self.기타자금 = 0

        self.__신주보통주식발행가 = float('nan')
        self.제3자배정대상자 = []

        self.할인율 = 0.0

    @property
    def 신주보통주식(self) -> int:
        return utils.to_int(self.__신주보통주식)

    @신주보통주식.setter
    def 신주보통주식(self, 신주보통주식):
        self.__신주보통주식 = utils.to_int(신주보통주식)

    @property
    def 신주보통주식발행가(self) -> int:
        return utils.to_int(self.__신주보통주식발행가)

    @신주보통주식발행가.setter
    def 신주보통주식발행가(self, 신주보통주식발행가):
        self.__신주보통주식발행가 = utils.to_int(신주보통주식발행가)

    def __str__(self):
        s = f'증자방식: {self.증자방식}\n'
        s += f'신주보통주식: {self.신주보통주식}\n'
        s += f'증자전보통주식총수: {self.증자전보통주식총수}\n'
        s += f'시설자금: {self.시설자금}\n'
        s += f'영업양수자금: {self.영업양수자금}\n'
        s += f'운영자금: {self.운영자금}\n'
        s += f'채무상환자금: {self.채무상환자금}\n'
        s += f'타법인증권취득자금: {self.타법인증권취득자금}\n'
        s += f'기타자금: {self.기타자금}\n'
        s += f'신주보통주식발행가: {self.신주보통주식발행가}\n'
        s += f'제3자배정대상자: {pprint.pformat(self.제3자배정대상자,width=80)}'
        return s


class 매출액또는손익:
    """
    {'당해매출액': '5785608', 
     '직전매출액': '7868321', 
     '매출액증감액': '-2082713', 
     '매출액증감비율': '-26.5', 
     '당해영업이익': '3670156',
     '직전영업이익': '4468321', 
     '영업이익증감액': '-798165', 
     '영업이익증감비율': '-17.9', 
     '당해당기순이익': '1188458', 
     '직전당기순이익': '-775358',
     '당기순이익증감액': '1963816', 
     '당기순이익증감비율': '흑자전환', 
     '당해자본총계': '95861883', 
     '직전자본총계': '97326624', 
     '당해자본금': '20100000',
     '직전자본금': '20100000', 
     '이사회결의일': '2021-07-06', 
     '단위': '2. 매출액 또는 손익구조 변동내용(단위:천원)'}
    """
    def __init__(self):
        self.__당해매출액 = float('nan')
        self.직전매출액 = 0
        self.매출액증감액 = 0
        self.__매출액증감비율 = float('nan')
        self.__당해영업이익 = float('nan')
        self.직전영업이익 = 0
        self.영업이익증감액 = 0
        self.__영업이익증감비율 = float('nan')
        self.__당해당기순이익 = float('nan')
        self.직전당기순이익 = 0
        self.당기순이익증감액 = 0
        self.__당기순이익증감비율 = float('nan')
        self.__당해자본총계 = float('nan')
        self.__직전자본총계 = float('nan')
        self.__당해자본금 = float('nan')
        self.__직전자본금 = float('nan')
        self.__이사회결의일 = None
        self.__단위 = float('nan')

        self.미발표분증감율 = float('nan')
        self.당해자본총계자본금비율 = float('nan')
        self.직전자본총계자본금비율 = float('nan')

    @property
    def 당해매출액(self) -> int:
        return utils.to_int(self.__당해매출액)

    @당해매출액.setter
    def 당해매출액(self, 당해매출액):
        self.__당해매출액 = utils.to_int(당해매출액)

    @property
    def 당해영업이익(self) -> int:
        return utils.to_int(self.__당해영업이익)

    @당해영업이익.setter
    def 당해영업이익(self, 당해영업이익):
        self.__당해영업이익 = utils.to_int(당해영업이익)

    @property
    def 당해당기순이익(self) -> int:
        return utils.to_int(self.__당해당기순이익)

    @당해당기순이익.setter
    def 당해당기순이익(self, 당해당기순이익):
        self.__당해당기순이익 = utils.to_int(당해당기순이익)

    @property
    def 당해자본총계(self) -> int:
        return utils.to_int(self.__당해자본총계)

    @당해자본총계.setter
    def 당해자본총계(self, 당해자본총계):
        self.__당해자본총계 = utils.to_int(당해자본총계)
        if not math.isnan(self.__당해자본총계) and not math.isnan(self.__당해자본금):
            self.당해자본총계자본금비율 = round(self.__당해자본총계 / self.__당해자본금 * 100, 1)

    @property
    def 직전자본총계(self) -> int:
        return utils.to_int(self.__직전자본총계)

    @직전자본총계.setter
    def 직전자본총계(self, 직전자본총계):
        self.__직전자본총계 = utils.to_int(직전자본총계)
        if not math.isnan(self.__직전자본총계) and not math.isnan(self.__직전자본금):
            self.직전자본총계자본금비율 = round(self.__직전자본총계 / self.__직전자본금 * 100, 1)

    @property
    def 당해자본금(self) -> int:
        return utils.to_int(self.__당해자본금)

    @당해자본금.setter
    def 당해자본금(self, 당해자본금):
        self.__당해자본금 = utils.to_int(당해자본금)
        if not math.isnan(self.__당해자본총계):
            self.당해자본총계자본금비율 = round(self.__당해자본총계 / self.__당해자본금 * 100, 1)

    @property
    def 직전자본금(self) -> int:
        return utils.to_int(self.__직전자본금)

    @직전자본금.setter
    def 직전자본금(self, 직전자본금):
        self.__직전자본금 = utils.to_int(직전자본금)
        if not math.isnan(self.__직전자본총계):
            self.직전자본총계자본금비율 = round(self.__직전자본총계 / self.__직전자본금 * 100, 1)

    @property
    def 매출액증감비율(self) -> float:
        return self.__매출액증감비율

    @매출액증감비율.setter
    def 매출액증감비율(self, 매출액증감비율):
        self.__매출액증감비율 = utils.to_float(매출액증감비율)

    @property
    def 영업이익증감비율(self) -> float:
        return self.__영업이익증감비율

    @영업이익증감비율.setter
    def 영업이익증감비율(self, 영업이익증감비율):
        self.__영업이익증감비율 = utils.to_float(영업이익증감비율)

    @property
    def 당기순이익증감비율(self) -> float:
        return self.__당기순이익증감비율

    @당기순이익증감비율.setter
    def 당기순이익증감비율(self, 당기순이익증감비율):
        self.__당기순이익증감비율 = utils.to_float(당기순이익증감비율)

    @property
    def 이사회결의일(self) -> datetime.date:
        return self.__이사회결의일

    @이사회결의일.setter
    def 이사회결의일(self, 이사회결의일: str):
        if 이사회결의일 == '-' or 이사회결의일 == '':
            self.__이사회결의일 = None
        else:
            self.__이사회결의일 = datetime.datetime.strptime(이사회결의일, '%Y-%m-%d').date()

    @property
    def 단위(self) -> int:
        return utils.to_int(self.__단위)

    @단위.setter
    def 단위(self, 단위: str):
        refined_단위 = re.search(r'단위:(\w?)', 단위.replace(' ', '')).group().replace('단위:', '')
        if '천' in refined_단위:
            self.__단위 = 1000
        elif '만' in refined_단위:
            self.__단위 = 10000
        elif '억' in refined_단위:
            self.__단위 = 100000000
        elif '원' == refined_단위:
            self.__단위 = 1

    def __str__(self):
        s = f'당해매출액: {self.당해매출액}\n'
        s += f'직전매출액: {self.직전매출액}\n'
        s += f'매출액증감액: {self.매출액증감액}\n'
        s += f'매출액증감비율: {self.매출액증감비율}\n'
        s += f'당해영업이익: {self.당해영업이익}\n'
        s += f'직전영업이익: {self.직전영업이익}\n'
        s += f'영업이익증감액: {self.영업이익증감액}\n'
        s += f'영업이익증감비율: {self.영업이익증감비율}\n'
        s += f'당해당기순이익: {self.당해당기순이익}\n'
        s += f'직전당기순이익: {self.직전당기순이익}\n'
        s += f'당기순이익증감액: {self.당기순이익증감액}\n'
        s += f'당기순이익증감비율: {self.당기순이익증감비율}\n'
        s += f'당해자본총계: {self.__당해자본총계}\n'
        s += f'직전자본총계: {self.__직전자본총계}\n'
        s += f'당해자본금: {self.__당해자본금}\n'
        s += f'직전자본금: {self.__직전자본금}\n'
        s += f'이사회결의일: {self.__이사회결의일}\n'
        s += f'당해자본총계/자본금비율: {self.당해자본총계자본금비율}%\n'
        s += f'직전자본총계/자본금비율: {self.직전자본총계자본금비율}%\n'
        s += f'단위: {self.__단위}'
        return s
