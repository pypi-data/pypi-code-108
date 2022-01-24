import random

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.mysql.MySQLAnyTable import MySQLAnyTable
from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLKitConfig import MySQLKitConfig
from tests.config import MYSQL_CONFIG

logger = NehushtanFileLogger('default')

config = MySQLKitConfig(MYSQL_CONFIG)
db = MySQLKit(config)

logger.info('prepare data set')

data_set = []
for i in range(100000):
    x1 = random.randint(100, 200)
    x2 = random.randint(400, 500)
    data_set.append([
        random.randint(1000, 2000),
        '2021-01-11',
        f'{x1}-{x2}',
        MySQLAnyTable.now()
    ])

logger.info('[raw] start with commit_immediately')

insert_sql = """
    INSERT IGNORE INTO sinri.dt_chat_spider_task(
        shop_id, rece_date, buyer_wang_id, ct_merits_create_time
    ) VALUES (%s, %s, %s, %s)
    """
last_row_id = db.raw_query_to_insert_many(insert_sql, data_set)

logger.info('[raw] end', {'last_row_id': last_row_id})

logger.info('prepare data set')

data_set = []
for i in range(100000):
    x1 = random.randint(100, 200)
    x2 = random.randint(400, 500)
    data_set.append([
        random.randint(1000, 2000),
        '2021-01-11',
        f'{x1}-{x2}',
        MySQLAnyTable.now()
    ])

logger.info('[model] start with commit_immediately')

afx = MySQLAnyTable(db, 'dt_chat_spider_task', 'sinri').insert_many_rows_with_matrix(
    ['shop_id', 'rece_date', 'buyer_wang_id', 'ct_merits_create_time'],
    data_set, with_ignore=True
).get_affected_rows()

logger.info('[model] end', {'afx': afx})

replace_sql = """
    REPLACE INTO sinri.dt_chat_spider_task(
        shop_id, rece_date, buyer_wang_id, ct_merits_create_time
    ) VALUES (%s, %s, %s, %s)
    """
last_row_id = db.raw_query_to_insert_many(replace_sql, data_set)

logger.info('--> [raw] end', {'last_row_id': last_row_id})

logger.info('fin')
