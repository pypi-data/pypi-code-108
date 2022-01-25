import os
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process
from .mi import calc
from db_hj3415 import mongo, sqlite
import datetime

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


def chcwd(func):
    # scrapy는 항상 프로젝트 내부에서 실행해야하기때문에 일시적으로 현재 실행경로를 변경한다.
    def wrapper(*args, **kwargs):
        before_cwd = os.getcwd()
        logger.info(f'current path : {before_cwd}')
        after_cwd = os.path.dirname(os.path.realpath(__file__))
        logger.info(f'change path to {after_cwd}')
        os.chdir(after_cwd)
        func(*args, **kwargs)
        logger.info(f'restore path to {before_cwd}')
        os.chdir(before_cwd)
    return wrapper


def _use_single(spider):
    # reference from https://docs.scrapy.org/en/latest/topics/practices.html(코드로 스파이더 실행하기)
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider)
    process.start()


@chcwd
def mi():
    spider_list = ('aud', 'chf', 'gbond3y', 'gold', 'kosdaq', 'kospi', 'silver', 'sp500', 'usdidx', 'usdkrw', 'wti',)
    print('*' * 25, f"Scrape multiprocess mi", '*' * 25)
    logger.info(spider_list)

    start_time = time.time()
    ths = []
    error = False
    for spider in spider_list:
        ths.append(Process(target=_use_single, args=(spider,)))
    for i in range(len(ths)):
        ths[i].start()
    for i in range(len(ths)):
        ths[i].join()
        if ths[i].exitcode != 0:
            error = True

    # calc 모듈을 이용해서 avg_per 과 yield_gap 을 계산하여 저장한다.
    print('*' * 25, f"Calculate and save avgper and yieldgap", '*' * 25)
    mi_mongo = mongo.MI()
    mi_sqlite = sqlite.MI()
    today_str = datetime.datetime.today().strftime('%Y.%m.%d')

    avgper = calc.avg_per()
    avgper_dict = {'date': today_str, 'value': str(avgper)}
    logger.info(avgper_dict)
    mi_mongo.save(mi_dict=avgper_dict, index='avgper')
    print(f'\tSave to mongo... date : {today_str} / title : avgper / value : {avgper}')
    #mi_sqlite.save(mi_dict=avgper_dict, index='avgper')
    #print(f'\tSave to sqlite... date : {today_str} / title : avgper / value : {avgper}')

    yieldgap = calc.yield_gap(avgper)
    yieldgap_dict = {'date': today_str, 'value': str(yieldgap)}
    logger.info(yieldgap_dict)
    mi_mongo.save(mi_dict=yieldgap_dict, index='yieldgap')
    print(f'\tSave to mongo... date : {today_str} / title : yieldgap / value : {yieldgap}')
    #mi_sqlite.save(mi_dict=yieldgap_dict, index='yieldgap')
    #print(f'\tSave to sqlite... date : {today_str} / title : yieldgap / value : {yieldgap}')

    print(f'Total spent time : {round(time.time() - start_time, 2)} sec')
    print('done.')
    return error


@chcwd
def _mi_test(spider: str):
    _use_single(spider=spider)


@chcwd
def mihistory(year: int):
    process = CrawlerProcess(get_project_settings())
    process.crawl('mihistory', year=year)
    process.start()


if __name__ == '__main__':
    mi()

