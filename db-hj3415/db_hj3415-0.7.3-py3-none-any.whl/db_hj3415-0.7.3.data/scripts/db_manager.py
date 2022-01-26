import os
import sys
import argparse

from krx_hj3415 import krx
from db_hj3415 import setting as db_setting, mongo
from util_hj3415 import noti
from scraper_hj3415.nfscrapy import scraper as scraper_nfs


import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def mongo_sync():
    print('*' * 20, 'Sync with krx and mongodb', '*' * 20)
    print(f"mongo addr : {db_setting.load().mongo_addr}")
    all_dbs = mongo.Corps.get_all_corps()
    print('*' * 20, 'Refreshing krx.db...', '*' * 20)
    krx.make_db()
    print('*' * 80)
    all_codes = krx.get_codes()
    print('\tThe number of codes in krx: ', len(all_codes))
    logger.debug(all_codes)
    try:
        print('\tThe number of dbs in mongo: ', len(all_dbs))
        logger.debug(all_dbs)
    except TypeError:
        err_msg = "Error while sync mongo data...it's possible mongo db doesn't set yet.."
        logger.error(err_msg)
        noti.telegram_to(botname='manager', text=err_msg)
        return
    del_targets = list(set(all_dbs) - set(all_codes))
    add_targets = list(set(all_codes) - set(all_dbs))
    print('\tDelete target: ', del_targets)
    print('\tAdd target: ', add_targets)

    for target in del_targets:
        mongo.Corps.drop_db(db=target)
        print(f'\tDelete {target} db in mongo..')

    if len(add_targets) == 0:
        pass
    else:
        print(f'Starting.. c10346 scraper.. items : {len(add_targets)}')
        scraper_nfs.run('c103', add_targets)
        scraper_nfs.run('c104', add_targets)
        scraper_nfs.run('c106', add_targets)


if __name__ == '__main__':
    # reference form https://docs.python.org/3.3/howto/argparse.html#id1
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', help=f"cleaning, mongo, sqlite3, print, default, sync")

    db_group = parser.add_mutually_exclusive_group()
    db_group.add_argument('-a', '--addr',  metavar='addr', help='server address')
    db_group.add_argument('-set', action='store_true', help='activate db')
    db_group.add_argument('-unset', action='store_true', help='deactivate db')
    parser.add_argument('-m', '--message', action='store_true', help='Send telegram message with result after work.')

    args = parser.parse_args()

    if args.cmd == 'cleaning':
        # corp db를 sync 하고 오래된 noti db를 정리한다.
        days_ago = 15
        print(f'>>> Delete old noti data before than {days_ago} days ago.')
        mongo.Noti().cleaning_data(days_ago=days_ago)
        print('Done.')

        if args.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {args.cmd}')
        sys.exit()
    elif args.cmd == 'sync':
        mongo_sync()

        if args.message:
            noti.telegram_to(botname='manager',
                             text=f'>>> python {os.path.basename(os.path.realpath(__file__))} {args.cmd}')
        sys.exit()
    elif args.cmd == 'mongo':
        if args.addr:
            db_setting.chg_mongo_addr(addr=args.addr)
        elif args.set:
            db_setting.turn_on_mongo()
        elif args.unset:
            db_setting.turn_off_mongo()
        sys.exit()
    elif args.cmd == 'sqlite3':
        if args.addr:
            db_setting.chg_sqlite3_path(path=args.addr)
        elif args.set:
            db_setting.turn_on_sqlite3()
        elif args.unset:
            db_setting.turn_off_sqlite3()
        sys.exit()
    elif args.cmd == 'default':
        db_setting.set_default()
        sys.exit()
    elif args.cmd == 'print':
        print(db_setting.load())
        sys.exit()
    else:
        parser.print_help()
        sys.exit()
