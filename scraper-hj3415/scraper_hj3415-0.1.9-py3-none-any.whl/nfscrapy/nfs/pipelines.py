# reference from https://livedata.tistory.com/27?category=1026425 (scrapy pipeline usage)
from . import items
from db_hj3415 import mongo, setting, sqlite


import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


class C101Pipeline:
    # c101에서 eps, bps, per, pbr을 수동으로 계산하여 입력하는 파이프라인
    def process_item(self, item, spider):
        if isinstance(item, items.C101items):
            print(f"\tIn the C101 pipeline...custom calculating EPS, BPS, PER, PBR")
            logger.info('*** Start c101 pipeline ***')
            logger.info(f"Raw data - EPS:{item['EPS']} BPS:{item['BPS']} PER:{item['PER']} PBR:{item['PBR']}")
            # eps, bps, per, pbr을 직접 계산해서 바꾸기 위해 c104 page를 찾는다.
            try:
                logger.info('Try to get c104 page for calculate values..')
                mongo_c104 = mongo.C104(code=item['코드'], page='c104q')
                cal_eps = mongo_c104.sum_recent_4q('EPS')[1]    # 최근 4분기 eps값을 더한다.
                cal_bps = mongo_c104.latest_value('BPS')[1]     # 마지막 분기 bps값을 찾는다.

                # per, pbr을 구하는 람다함수
                cal_ratio = (lambda eps_bps, pprice:
                             None if eps_bps is None or eps_bps == 0 else round(int(pprice) / int(eps_bps), 2))
                cal_per = cal_ratio(cal_eps, item['주가'])
                cal_pbr = cal_ratio(cal_bps, item['주가'])
                logger.info(f"After calc data - EPS:{cal_eps} BPS:{cal_bps} PER:{cal_per} PBR:{cal_pbr}")
                logger.info(f"*** End c101 calculation pipeline {item['코드']} ***")
            except:
                logger.warning("Error on calculating custom EPS, BPS, PER, PBR, maybe DB hasn't c104q collection.")
                logger.warning(
                    f"We will use default scraped values -  EPS:{item['EPS']} BPS:{item['BPS']} PER:{item['PER']} PBR:{item['PBR']}")
                return item
            item['EPS'], item['BPS'], item['PER'], item['PBR'] = cal_eps, cal_bps, cal_per, cal_pbr
        return item


class MongoPipeline:
    # 몽고 데이터 베이스에 저장하는 파이프라인
    def __init__(self):
        self.db_setting = setting.load()
        logger.info(f"mongodb addr : {self.db_setting.mongo_addr}")

    def process_item(self, item, spider):
        if self.db_setting.active_mongo:
            if isinstance(item, items.C101items):
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {spider.name}")
                mongo.C101(code=item['코드']).save(c101_dict={
                    "date": item['date'],
                    "코드": item['코드'],
                    "종목명": item['종목명'],
                    "업종": item['업종'],
                    "주가": item['주가'],
                    "거래량": item['거래량'],
                    "EPS": item['EPS'],
                    "BPS": item['BPS'],
                    "PER": item['PER'],
                    "업종PER": item['업종PER'],
                    "PBR": item['PBR'],
                    "배당수익률": item['배당수익률'],
                    "최고52주": item['최고52주'],
                    "최저52주": item['최저52주'],
                    "거래대금": item['거래대금'],
                    "시가총액": item['시가총액'],
                    "베타52주": item['베타52주'],
                    "발행주식": item['발행주식'],
                    "유통비율": item['유통비율'],
                    "intro": item['intro1'] + item['intro2'] + item['intro3']
                })
            elif isinstance(item, items.C103items):
                page = ''.join(['c103', item['title']])
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {page}")
                mongo.C103(code=item['코드'], page=page).save(c103_list=item['df'].to_dict('records'))
            elif isinstance(item, items.C104items):
                if item['title'].endswith('y'):
                    c104_page = 'c104y'
                elif item['title'].endswith('q'):
                    c104_page = 'c104q'
                else:
                    raise ValueError
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {c104_page}")
                mongo.C104(code=item['코드'], page=c104_page).save(c104_list=item['df'].to_dict('records'))
            elif isinstance(item, items.C106items):
                page = ''.join(['c106', item['title']])
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {page}")
                item['df'].set_index('항목', inplace=True)
                logger.debug(item['df'].to_dict('index'))
                mongo.C106(code=item['코드'], page=''.join(['c106', item['title']])).save(c106_dict=item['df'].to_dict('index'))
            elif isinstance(item, items.C108items):
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {spider.name}")
                mongo.C108(code=item['코드']).save(c108_list=item['df'].to_dict('records'))
            return item
        else:
            print(f"\tIn the {self.__class__.__name__}...skipping save to db ")
            return item


class SqlitePipeline:
    # Sqlite3 데이터 베이스에 저장하는 파이프라인
    def __init__(self):
        self.db_setting = setting.load()
        logger.info(f"sqlite3db addr : {self.db_setting.sqlite3_path}")

    def process_item(self, item, spider):
        if self.db_setting.active_sqlite3:
            if isinstance(item, items.C101items):
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {spider.name}")
                sqlite.C101(code=item['코드']).save(c101_dict={
                    "date": item['date'],
                    "코드": item['코드'],
                    "종목명": item['종목명'],
                    "업종": item['업종'],
                    "주가": item['주가'],
                    "거래량": item['거래량'],
                    "EPS": item['EPS'],
                    "BPS": item['BPS'],
                    "PER": item['PER'],
                    "업종PER": item['업종PER'],
                    "PBR": item['PBR'],
                    "배당수익률": item['배당수익률'],
                    "최고52주": item['최고52주'],
                    "최저52주": item['최저52주'],
                    "거래대금": item['거래대금'],
                    "시가총액": item['시가총액'],
                    "베타52주": item['베타52주'],
                    "발행주식": item['발행주식'],
                    "유통비율": item['유통비율'],
                    "intro": item['intro1'] + item['intro2'] + item['intro3']
                })
            elif isinstance(item, items.C103items):
                page = ''.join(['c103', item['title']])
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {page}")
                sqlite.C103(code=item['코드'], page=page).save(c103_df=item['df'])
            elif isinstance(item, items.C104items):
                page = ''.join(['c104', item['title']])
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {page}")
                sqlite.C104(code=item['코드'], page=page).save(c104_df=item['df'])
            elif isinstance(item, items.C106items):
                page = ''.join(['c106', item['title']])
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {page}")
                sqlite.C106(code=item['코드'], page=page).save(c106_df=item['df'])
            elif isinstance(item, items.C108items):
                print(f"\tIn the {self.__class__.__name__}...code : {item['코드']} / page : {spider.name}")
                sqlite.C108(code=item['코드']).save(c108_df=item['df'])
            return item
        else:
            print(f"\tIn the {self.__class__.__name__}...skipping save to db ")
            return item
