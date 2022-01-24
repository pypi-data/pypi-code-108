from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.mysql import constant
from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLKitConfig import MySQLKitConfig
from tests.config import MYSQL_CONFIG

if __name__ == '__main__':
    logger = NehushtanFileLogger('default')

    config = MySQLKitConfig(MYSQL_CONFIG)
    db = MySQLKit(config)

    # print(db.get_raw_connection().cursor().lastrowid)
    # exit(0)

    replace_sql = 'replace into c(id,value,name) values(%s,%s,%s)'

    x = db.raw_query_to_insert_one(replace_sql, (1, 1, 'a'))
    logger.info('Round 1', x)

    x = db.raw_query_to_insert_one(replace_sql, (2, 2, 'a'))
    logger.info('Round 2', x)

    x = db.raw_query_to_insert_one(replace_sql, (2, 2, 'a'))
    logger.info('Round 3', x)

    x = db.raw_query_to_insert_one(replace_sql, [])
    logger.info('Round 4', x)

    cursor = db.get_raw_connection().cursor()

    cursor.executemany(replace_sql, [[]])

    print(constant.MYSQL_QUERY_STATUS_EXECUTED)
    print(cursor.lastrowid)
    print(cursor.rowcount)
