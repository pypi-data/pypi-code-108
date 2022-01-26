# 파일명을 sqlite3.py로 하면 sqlite3 모듈과 이름이 중복되어 에러가 발생한다.
from sqlalchemy import text, Column, String, Integer, create_engine, Float, TIMESTAMP, MetaData, Boolean
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import os
from .setting import load as load_setting
from util_hj3415 import utils
import pandas as pd

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


# =============== sqlite3 테이블을 구성하는 클래스 ===================


BaseCorps = declarative_base()
BaseMI = declarative_base()
BaseNoti = declarative_base()


class C101Structure(BaseCorps):
    __tablename__ = 'c101'
    date = Column("date", String, primary_key=True, nullable=False)
    코드 = Column("코드", String)
    종목명 = Column("종목명", String)
    업종 = Column("업종", String)
    주가 = Column("주가", Integer)
    거래량 = Column("거래량", Integer)
    EPS = Column("EPS", Float)
    BPS = Column("BPS", Float)
    PER = Column("PER", Float)
    업종PER = Column("업종PER", Float)
    PBR = Column("PBR", Float)
    배당수익률 = Column("배당수익률", Float)
    최고52주 = Column("최고52주", Float)
    최저52주 = Column("최저52주", Float)
    거래대금 = Column("거래대금", Float)
    시가총액 = Column("시가총액", Float)
    베타52주 = Column("베타52주", Float)
    발행주식 = Column("발행주식", Float)
    유통비율 = Column("유통비율", Float)
    intro = Column("intro", String)

    def __str__(self):
        return '/'.join([self.date, self.코드, str(self.종목명), str(self.업종), str(self.주가)])


class StampStructure(BaseCorps):
    __tablename__ = 'stamp'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String)
    sqltime = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())


class DartStructure(BaseCorps):
    """DartByCode 의 테이블 구조 클래스
    """
    __tablename__ = 'dart'
    rcept_no = Column('rcept_no', String, nullable=False, primary_key=True)
    rcept_dt = Column('rcept_dt', String)
    report_nm = Column('report_nm', String)
    point = Column("point", Integer)
    text = Column('text', String)
    is_noti = Column('is_noti', Boolean)


# ===========================================================


class Kospi(BaseMI):
    __tablename__ = 'kospi'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Kosdaq(BaseMI):
    __tablename__ = 'kosdaq'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Gbond3y(BaseMI):
    __tablename__ = 'gbond3y'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Sp500(BaseMI):
    __tablename__ = 'sp500'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Usdkrw(BaseMI):
    __tablename__ = 'usdkrw'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Wti(BaseMI):
    __tablename__ = 'wti'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Aud(BaseMI):
    __tablename__ = 'aud'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Chf(BaseMI):
    __tablename__ = 'chf'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Gold(BaseMI):
    __tablename__ = 'gold'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Silver(BaseMI):
    __tablename__ = 'silver'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Yieldgap(BaseMI):
    __tablename__ = 'yieldgap'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Avgper(BaseMI):
    __tablename__ = 'avgper'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


class Usdidx(BaseMI):
    __tablename__ = 'usdidx'
    date = Column("date", String, primary_key=True, nullable=False)
    value = Column("value", Float)

    def __str__(self):
        return '/'.join((self.date, str(self.value)))


# ===========================================================


class NotiStructure(BaseNoti):
    __tablename__ = 'noti'
    rcept_no = Column('rcept_no', String, nullable=False, primary_key=True)
    code = Column('code', String)
    rcept_dt = Column('rcept_dt', String)
    report_nm = Column('report_nm', String)
    point = Column("point", Integer)
    text = Column('text', String)


# ===========================================================

sqlite3_path = load_setting().sqlite3_path


def chk_deactivate_sqlite3(func):
    def wrapper(*args, **kwargs):
        if not load_setting().active_sqlite3:
            print('sqlite3 db is deactivated..')
            return None
        else:
            return func(*args, **kwargs)
    return wrapper


class Base:
    def __init__(self, folder_name: str, db_name: str):
        self.sqlite3_path = load_setting().sqlite3_path

        if self.sqlite3_path != '':
            self.engine = self.make_engine(folder_name, db_name)
        else:
            print('sqlite3 db is deactivated..')
            self.engine = None

    @staticmethod
    @chk_deactivate_sqlite3
    def make_engine(folder_name: str, db_name: str):
        # make folder - /db/{folder_name}
        path = os.path.join(sqlite3_path, folder_name)
        if not os.path.isdir(path):
            os.makedirs(path)
        dsn = f"sqlite:///{os.path.join(path, ''.join([db_name, '.db']))}"
        logger.info(f"Connect to {dsn}")
        return create_engine(dsn, echo=False)

    @chk_deactivate_sqlite3
    def get_tables(self) -> tuple:
        meta = MetaData()
        meta.reflect(bind=self.engine)
        return tuple(meta.tables.keys())

    def _get_session(self, base_cla):
        if self.engine is None:
            return None
        else:
            base_cla.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            return Session()


class Corps(Base):
    # mongodb와 다른점은 stamp 테이블과 c106이 c106y,c106q로 각각의 테이블을 가진다.
    TABLE = ('c101', 'c104y', 'c104q', 'c106y', 'c106q', 'c108',
             'c103손익계산서q', 'c103재무상태표q', 'c103현금흐름표q',
             'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y', 'dart', 'stamp')

    def __init__(self, code: str, table: str = 'c101'):
        if utils.is_6digit(code) and table in self.TABLE:
            self.code = code
            self.table = table
            super().__init__(folder_name='corps', db_name=self.code)
            self.session = self._get_session(BaseCorps)
        else:
            raise ValueError(f'Invalid value : {code}(6 digit) / {table}({self.TABLE})')

    # ======================Corps 만 가지는 함수들 ===========================

    def chg_code(self, code: str):
        # code 가 6자리 숫자인지 확인 후 세팅
        if utils.is_6digit(code):
            logger.info(f'Set db : {self.code} -> {code}')
            self.code = code
            self.session = self._get_session(BaseCorps)
        else:
            raise ValueError(f'Invalid value : {code}(6 digit)')

    def drop_table(self, table: str):
        if table in self.TABLE:
            with self.engine.connect() as conn:
                before_drop = self.get_tables()
                conn.execute(text(f'DROP TABLE IF EXISTS {table}'))
                conn.execute(text('VACUUM'))
                after_drop = self.get_tables()
                if before_drop != after_drop:
                    logger.info(f'Drop table : {before_drop} -> {after_drop}')
                if table == 'c101' or table == 'stamp':
                    # c101 과 stamp 테이블은 BaseCorps.metadata.create_all(self.engine) 명령어로 재생성 될 것임..
                    logger.warning('c101 and stamp table will respawn...')
        else:
            raise ValueError(f'Invalid table : {table} / {self.TABLE}')

    def stamping(self):
        stamp = StampStructure(name=self.table)
        self.session.add(stamp)
        logger.info(f"Stamping.. name:'{self.table}'")
        self.session.commit()


class C101(Corps):
    def __init__(self, code: str):
        super().__init__(code=code, table='c101')

    def save(self, c101_dict: dict) -> bool:
        """
        c101의 구조에 맞는 딕셔너리값을 받아서 구조가 맞는지 확인하고 맞으면 저장한다.
        """
        c101_struc = ['date', '코드', '종목명', '업종', '주가', '거래량', 'EPS', 'BPS', 'PER', '업종PER', 'PBR', '배당수익률',
                      '최고52주', '최저52주', '거래대금', '시가총액', '베타52주', '발행주식', '유통비율', 'intro']
        if c101_dict['코드'] != self.code:
            raise ValueError("Code isn't equal input data and db data..")
        if sorted(c101_struc) == sorted(c101_dict.keys()):
            self.session.query(C101Structure).filter(C101Structure.date >= c101_dict['date']).delete()
            self.session.add(C101Structure(date=c101_dict['date'],
                                           코드=c101_dict['코드'],
                                           종목명=c101_dict['종목명'],
                                           업종=c101_dict['업종'],
                                           주가=c101_dict['주가'],
                                           거래량=c101_dict['거래량'],
                                           EPS=c101_dict['EPS'],
                                           BPS=c101_dict['BPS'],
                                           PER=c101_dict['PER'],
                                           업종PER=c101_dict['업종PER'],
                                           PBR=c101_dict['PBR'],
                                           배당수익률=c101_dict['배당수익률'],
                                           최고52주=c101_dict['최고52주'],
                                           최저52주=c101_dict['최저52주'],
                                           거래대금=c101_dict['거래대금'],
                                           시가총액=c101_dict['시가총액'],
                                           베타52주=c101_dict['베타52주'],
                                           발행주식=c101_dict['발행주식'],
                                           유통비율=c101_dict['유통비율'],
                                           intro=c101_dict['intro']))
            logger.info(self.session.query(C101Structure).filter_by(date=c101_dict['date']).first())
            self.session.commit()
            return True
        else:
            raise ValueError('Invalid c101 dictionary structure..')


class C103(Corps):
    def __init__(self, code: str, page: str = 'c103재무상태표y'):
        if page.startswith('c103') and page[-1] in ['q', 'y']:
            if page[4:-1] in ['손익계산서', '손', 'i', '_i']:
                super().__init__(code=code, table=''.join([page[:4], '손익계산서', page[-1]]))
            elif page[4:-1] in ['재무상태표', '재', 'b', '_b']:
                super().__init__(code=code, table=''.join([page[:4], '재무상태표', page[-1]]))
            elif page[4:-1] in ['현금흐름표', '현', 'c', '_c']:
                super().__init__(code=code, table=''.join([page[:4], '현금흐름표', page[-1]]))
            else:
                raise ValueError(f'Invalid value : {page}')
        else:
            raise ValueError(f'Invalid value : {page}')

    def save(self, c103_df: pd.DataFrame) -> bool:
        """
        데이터프레임 형식의 인자를 받아 저장한다.
        """
        self.drop_table(table=self.table)
        c103_df.to_sql(self.table, con=self.engine, index=False, if_exists='replace')
        logger.info(f"Save dataframe on {self.table} table successfully...")
        self.stamping()
        return True


class C104(Corps):
    def __init__(self, code: str, page: str = 'c104y'):
        super().__init__(code=code, table=page)

    def save(self, c104_df: pd.DataFrame) -> bool:
        """
        데이터프레임 형식의 인자를 받아 저장한다.
        """
        self.drop_table(table=self.table)
        c104_df.to_sql(self.table, con=self.engine, index=False, if_exists='replace')
        logger.info(f"Save dataframe on {self.table} table successfully...")
        self.stamping()
        return True


class C106(Corps):
    PERIOD = ['q', 'y']

    def __init__(self, code: str, page: str = 'c106y'):
        if page[:4] == 'c106' and page[4:5] in self.PERIOD:
            super().__init__(code=code, table=page)
            self.page = page
        else:
            raise ValueError(f'Invalid page : {page}(c106q or c106y)')

    def save(self, c106_df: pd.DataFrame) -> bool:
        """
        데이터프레임 형식의 인자를 받아 저장한다.
        """
        self.drop_table(table=self.table)
        c106_df.to_sql(self.table, con=self.engine, index=True, if_exists='replace')
        logger.info(f"Save dataframe on {self.table} table successfully...")
        self.stamping()
        return True


class C108(Corps):
    def __init__(self, code: str):
        super().__init__(code=code, table='c108')

    def save(self, c108_df: pd.DataFrame) -> bool:
        """
        데이터프레임 형식의 인자를 받아 저장한다.
        """
        self.drop_table(table=self.table)
        c108_df.to_sql(self.table, con=self.engine, index=False, if_exists='replace')
        logger.info(f"Save dataframe on {self.table} table successfully...")
        self.stamping()
        return True


class DartByCode(Corps):
    def __init__(self, code: str):
        self.table = DartStructure.__tablename__
        super().__init__(code=code, table='c101')
        self.session = self._get_session(BaseCorps)

    def save(self, dart_dict: dict) -> bool:
        """
        dart_dict 구조\n
            {'rcept_no': '20210514000624',\n
            'rcept_dt': '20210514',\n
            'report_nm': '임원ㆍ주요주주특정증권등소유상황보고서',\n
            'point': 2,\n
            'text': '등기임원이 1.0억 이상 구매하지 않음.',\n
            'is_noti': True}\n
        """
        self.session.add(DartStructure(rcept_no=dart_dict['rcept_no'],
                                       rcept_dt=dart_dict['rcept_dt'],
                                       report_nm=dart_dict['report_nm'],
                                       point=dart_dict['point'],
                                       text=dart_dict['text'],
                                       is_noti=dart_dict['is_noti']))
        try:
            self.session.commit()
            logger.info(f'Add {self.table} : {dart_dict}')
        except IntegrityError:
            # 같은 내용 중복저상시 경고 로그 표시하고 저장하지 않음.
            logger.warning(f"rcept_no : {dart_dict['rcept_no']}  exists already in db.")
        return True


# ===========================================================


class MI(Base):
    TABLE = ('aud', 'chf', 'gbond3y', 'gold', 'silver', 'kosdaq', 'kospi',
             'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'usdidx')

    def __init__(self, index='kospi'):
        if index in self.TABLE:
            self.table = index
            # 테이블명에 해당하는 클래스를 할당하기 위해 첫글자를 대문자로 바꿔서 능동적으로 클래스를 할당한다.
            self.tabls_cls = globals()[index.capitalize()]
            super().__init__(folder_name='mi', db_name='mi')
            self.session = self._get_session(BaseMI)
        else:
            raise ValueError(f'Invalid value : {index} / {self.TABLE}')

    # ======================MI 만 가지는 함수들 ===========================
    # MI 에서는 테이블을 삭제해도 자동으로 바로 재생성되기 때문에 drop_table 이 필요없다.

    def chg_index(self, index: str):
        if index in self.TABLE:
            logger.info(f'Set col : {self.table} -> {index}')
            self.table = index
            self.tabls_cls = globals()[index.capitalize()]
            # 인덱스가 바뀌더라도 데이터베이스가 바뀌는 것은 아니라 엔진을 새로 얻을 필요는 없다.
        else:
            raise ValueError(f'Invalid value : {index} / {self.TABLE}')

    def save(self, mi_dict: dict, index: str = '') -> bool:
        """
        mi_dict의 구조 - {'date': '2021.07.21', 'value': '1154.50'}
        index 종류 - 'aud', 'chf', 'gbond3y', 'gold', 'silver', 'kosdaq', 'kospi', 'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'usdidx'
        """
        if index != '':
            self.chg_index(index=index)
        # 해당테이블에서 날짜에 해당하는 데이터를 쿼리한다.
        old_one = self.session.query(self.tabls_cls).filter(self.tabls_cls.date == mi_dict['date']).first()

        if old_one:
            setattr(old_one, 'value', mi_dict['value'])
            logger.info(f"Update {self.table} : {old_one} -> {mi_dict['date']}/{mi_dict['value']}")
        else:
            self.session.add(self.tabls_cls(date=mi_dict['date'], value=mi_dict['value']))
            logger.info(f'Add {self.table} : {mi_dict}')
        self.session.commit()
        return True


class Noti(Base):
    def __init__(self):
        self.table = NotiStructure.__tablename__
        super().__init__(folder_name='noti', db_name='noti')
        self.session = self._get_session(BaseNoti)

    def save(self, noti_dict: dict) -> bool:
        """
        noti_dict 구조
        {'code': '005930',
        'rcept_no': '20210514000624',
        'rcept_dt': '20210514',
        'report_nm': '임원ㆍ주요주주특정증권등소유상황보고서',
        'point': 2,
        'text': '등기임원이 1.0억 이상 구매하지 않음.'}
        """
        self.session.add(NotiStructure(rcept_no=noti_dict['rcept_no'],
                                       code=noti_dict['code'],
                                       rcept_dt=noti_dict['rcept_dt'],
                                       report_nm=noti_dict['report_nm'],
                                       point=noti_dict['point'],
                                       text=noti_dict['text']))
        try:
            self.session.commit()
            logger.info(f'Add {self.table} : {noti_dict}')
        except IntegrityError:
            # 같은 내용 중복저상시 경고 로그 표시하고 저장하지 않음.
            logger.warning(f"rcept_no : {noti_dict['rcept_no']}  exists already in db.")
        return True

    def get_data(self) -> pd.DataFrame:
        df = pd.read_sql_query(text(f"SELECT * FROM {self.table}"), con=self.engine)
        return df

    def cleaning_data(self, days_ago=15):
        logger.warning("Deleting sqlite noti data is not implement yet..")


class DartByDate(Base):
    def __init__(self, date: str):
        super().__init__(folder_name='dart', db_name='dart')
        if utils.isYmd(date):
            self.date = date
            self.tablename = 't' + date
        else:
            raise ValueError(f'Invalid date : {date}(%Y%m%d)')

    def save(self, df: pd.DataFrame) -> bool:
        # 전체 공시 마감후 저녁 8시경 한번 실행함.
        if df.empty:
            print('Dataframe is empty..So we will skip saving db..')
            return False

        # 테이블을 저장한다.
        print(f"Save dataframe on {self.tablename} table ...")
        df.to_sql(self.tablename, con=self.engine, index=False, if_exists='replace')
        return True

    def get_data(self, title: str = '') -> pd.DataFrame:
        """
        analysis를 제작하는 동안 dart를 매번 받아오지 않도록 하는 개발전용 함수
        """
        df = pd.read_sql_query(text(f"SELECT * FROM t{self.date}"), con=self.engine)
        if title != '':
            df = df[df['report_nm'].str.contains(title)]
        return df


class EvalByDate(Base):
    def __init__(self, date: str):
        super().__init__(folder_name='eval', db_name='eval')
        if utils.isYmd(date):
            self.date = date
            self.tablename = 't' + date
        else:
            raise ValueError(f'Invalid date : {date}(%Y%m%d)')

    def save(self, df: pd.DataFrame) -> bool:
        if df.empty:
            print('Dataframe is empty..So we will skip saving db..')
            return False

        # 테이블을 저장한다.
        print(f"Save dataframe on {self.tablename} table ...")
        df.to_sql(self.tablename, con=self.engine, index=False, if_exists='replace')
        return True

    def get_data(self) -> pd.DataFrame:
        df = pd.read_sql_query(text(f"SELECT * FROM t{self.date}"), con=self.engine)
        return df
