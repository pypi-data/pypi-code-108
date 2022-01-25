import os
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, cpu_count

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


def _mp_c10168(page: str, codes: list):
    # reference from https://monkey3199.github.io/develop/python/2018/12/04/python-pararrel.html
    # 전체 코드를 코어수대로 나눠서 멀티프로세싱 시행
    def _code_divider(entire_codes):
        # 전체 종목코드를 리스트로 넣으면 cpu 코어에 맞춰 나눠준다.
        # reference from https://stackoverflow.com/questions/19086106/how-to-utilize-all-cores-with-python-multiprocessing
        def _split_list(alist, wanted_parts=1):
            # 멀티프로세싱할 갯수로 리스트를 나눈다.
            # reference from https://www.it-swarm.dev/ko/python/%EB%8D%94-%EC%9E%91%EC%9D%80-%EB%AA%A9%EB%A1%9D%EC%9C%BC%EB%A1%9C-%EB%B6%84%ED%95%A0-%EB%B0%98%EC%9C%BC%EB%A1%9C-%EB%B6%84%ED%95%A0/957910776/
            length = len(alist)
            return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                    for i in range(wanted_parts)]

        core = cpu_count()
        print(f'Get number of core for multiprocessing : {core}')
        n = core - 1
        if len(entire_codes) < n:
            n = len(entire_codes)
        print(f'Split total {len(entire_codes)} codes by {n} parts ...')
        divided_list = _split_list(entire_codes, wanted_parts=n)
        return n, divided_list

    if page not in ('c101', 'c106', 'c108'):
        raise NameError
    print('*' * 25, f"Scrape multiprocess {page.capitalize()}", '*' * 25)
    print(f'Total {len(codes)} items..')
    logger.info(codes)
    n, divided_list = _code_divider(codes)

    start_time = time.time()
    ths = []
    error = False
    for i in range(n):
        ths.append(Process(target=_run_scrapy, args=(page, divided_list[i])))
    for i in range(n):
        ths[i].start()
    for i in range(n):
        ths[i].join()
    print(f'Total spent time : {round(time.time() - start_time, 2)} sec.')


def _mp_c1034(page: str, codes: list):
    if page == 'c103':
        spiders = ('c103_iy', 'c103_by', 'c103_cy', 'c103_iq', 'c103_bq', 'c103_cq')
    elif page == 'c104':
        spiders = ('c104_aq', 'c104_bq', 'c104_cq', 'c104_dq', 'c104_ay', 'c104_by', 'c104_cy', 'c104_dy')
    else:
        raise NameError
    # c103 6개, c104 8개 페이지수대로 멀티프로세싱 시행
    title = spiders[0].split('_')[0]
    print('*' * 25, f"Scrape multiprocess {title}", '*' * 25)
    print(f'Total {len(codes)} items..')
    logger.info(codes)

    start_time = time.time()
    ths = []
    error = False
    for spider in spiders:
        ths.append(Process(target=_run_scrapy, args=(spider, codes)))
    for i in range(len(ths)):
        ths[i].start()
    for i in range(len(ths)):
        ths[i].join()
    print(f'Total spent time : {round(time.time() - start_time, 2)} sec.')


def _run_scrapy(spider: str, codes: list):
    # 본 코드를 직접 실행하지 않고 멀티프로세싱 함수에서 실행하도록 한다.
    # reference from https://docs.scrapy.org/en/latest/topics/practices.html(코드로 스파이더 실행하기)
    settings = get_project_settings()
    logger.info(f"bot name: {settings.get('BOT_NAME')}")
    process = CrawlerProcess(settings)
    process.crawl(spider, code=codes)
    process.start()


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


@chcwd
def run(cxxx: str, codes: list):
    """
    cxxx:str in ['c101', 'c106', 'c108', 'c103', 'c104']
    codes:list
    """
    if cxxx in ['c101', 'c106', 'c108']:
        _mp_c10168(cxxx, codes)
    elif cxxx in ['c103', 'c104']:
        _mp_c1034(cxxx, codes)
    else:
        raise NameError
