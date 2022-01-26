import os
import pickle
import platform

import logging
import pymongo.errors

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)

DEF_MONGO_ADDR = 'mongodb://localhost:27017'
DEF_WIN_SQLITE3_PATH = 'C:\\_db'
DEF_LINUX_SQLITE3_PATH = '/home/hj3415/Stock/_db'

FILENAME = 'setting.pickle'
FULL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), FILENAME)


class DbSetting:
    """데이터베이스 설정 데이터

    데이터베이스의 경로와 활성화 여부를 저장하는 클래스로 피클에 저장되어 사용됨
    """
    def __init__(self):
        self.mongo_addr = DEF_MONGO_ADDR
        self.active_mongo = True
        if 'Windows' in platform.platform():
            self.sqlite3_path = DEF_WIN_SQLITE3_PATH
        elif 'Linux' in platform.platform():
            self.sqlite3_path = DEF_LINUX_SQLITE3_PATH
        else:
            raise
        self.active_sqlite3 = False

    def __str__(self):
        s = ''
        if self.active_mongo:
            s += f'Mongo db(active) : {self.mongo_addr}\n'
        else:
            s += f'Mongo db(inactive) : {self.mongo_addr}\n'
        if self.active_sqlite3:
            s += f'Sqlite3 db(active) : {self.sqlite3_path}'
        else:
            s += f'Sqlite3 db(inactive) : {self.sqlite3_path}'
        return s


def load() -> DbSetting:
    try:
        with open(FULL_PATH, "rb") as fr:
            s = pickle.load(fr)
            logger.info(s)
            return s
    except (EOFError, FileNotFoundError) as e:
        logger.error(e)
        set_default()
        # 새로 만든 파일을 다시 불러온다.
        with open(FULL_PATH, "rb") as fr:
            s = pickle.load(fr)
            logger.info(s)
            return s


def chg_mongo_addr(new_addr: str):
    """몽고 db의 주소 변경

    몽고 db의 주소를 변경하는 함수로 형식을 검사하여 적합하면 변경함.
    """
    if new_addr.startswith('mongodb'):
        s = load()
        before = s.mongo_addr
        s.mongo_addr = new_addr
        if before != s.mongo_addr:
            print(f'Change mongo setting : {before} -> {new_addr}')
            with open(FULL_PATH, "wb") as fw:
                pickle.dump(s, fw)
    else:
        raise ValueError(f'Invalid mongo address : {new_addr}')


def turn_off_mongo():
    s = load()
    s.active_mongo = False
    print(s)
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(s, fw)


def turn_on_mongo():
    s = load()
    s.active_mongo = True
    print(s)
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(s, fw)


def chg_sqlite3_path(path: str):
    s = load()
    before = s.sqlite3_path
    s.sqlite3_path = path
    if before != path:
        print(f'Change mongo setting : {before} -> {path}')
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(s, fw)


def turn_off_sqlite3():
    s = load()
    s.active_sqlite3 = False
    print(s)
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(s, fw)


def turn_on_sqlite3():
    s = load()
    s.active_sqlite3 = True
    print(s)
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(s, fw)


def set_default():
    s = DbSetting()
    print(s)
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(s, fw)


def is_srv_live(addr: str) -> bool:
    from pymongo import MongoClient
    try:
        client = MongoClient(addr)
        r = client.db_name.command('ping')
        return True
    except pymongo.errors.ServerSelectionTimeoutError:
        return False