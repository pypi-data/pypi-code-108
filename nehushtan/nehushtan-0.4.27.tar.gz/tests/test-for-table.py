from nehushtan.logger.NehushtanLogger import NehushtanLogger
from nehushtan.mysql.MySQLAnyTable import MySQLAnyTable
from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLKitConfig import MySQLKitConfig
from tests.config import MYSQL_CONFIG

logger = NehushtanLogger('test', [NehushtanLogger.make_stdout_handler()])

table = MySQLAnyTable(
    MySQLKit(MySQLKitConfig(MYSQL_CONFIG)),
    'b'
)

table.truncate()

result = table.insert_one_row(
    {
        'name': 'one',
        'value': 1,
        'price': 1.1,
        'meta': None,
        'update_time': table.now(),
    }
)

logger.info(
    'insert one row',
    {
        'status': result.get_status(),
        'last_insert_id': result.get_last_inserted_id(),
        'afx': result.get_affected_rows(),
    }
)

dict_rows = []
for i in range(10000):
    dict_rows.append({
        'name': f'batch-name-{i}',
        'value': i,
        'price': i * 0.3,
        'meta': None,
        'update_time': table.now(),
    })

logger.info('insert_many_rows_with_dicts for 10000 rows start')
result = table.insert_many_rows_with_dicts(dict_rows)
logger.info(
    'insert_many_rows_with_dicts for 10000 rows end',
    {
        'status': result.get_status(),
        'last_insert_id': result.get_last_inserted_id(),
        'afx': result.get_affected_rows(),
        'error': result.get_error(),
    }
)

dict_rows = []
for i in range(10000):
    dict_rows.append({
        'name': f'replace-name-{i}',
        'value': i,
        'price': i * 0.4,
        'meta': 'fuck',
        'update_time': table.now(),
    })

logger.info('replace_many_rows_with_dicts for 10000 rows start')
result = table.replace_many_rows_with_dicts(dict_rows)
logger.info(
    'replace_many_rows_with_dicts for 10000 rows end',
    {
        'status': result.get_status(),
        'last_insert_id': result.get_last_inserted_id(),
        'afx': result.get_affected_rows(),
        'error': result.get_error(),
    }
)
