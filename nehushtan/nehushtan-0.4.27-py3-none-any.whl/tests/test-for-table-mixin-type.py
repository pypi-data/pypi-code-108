from nehushtan.mysql.MySQLAnyTable import MySQLAnyTable
from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLKitConfig import MySQLKitConfig
from tests.config import MYSQL_CONFIG

table = MySQLAnyTable(
    MySQLKit(MySQLKitConfig(MYSQL_CONFIG)),
    'a'
)

fields = ['id', 'data']
matrix = [[1, 'e'], (3, '3'), [4, '5']]

result = table.replace_many_rows_with_matrix(fields, matrix)
print(result.get_status(), result.get_error(), result.get_sql())

dicts = [{'id': 2, 'data': '55'}, {'id': 4, 'data': 3.3}]

result = table.insert_many_rows_with_dicts(dicts, on_duplicate_key_update_rows={'data': 'data+1'})
print(result.get_status(), result.get_error(), result.get_sql())

# result = table.update_rows(conditions=[MySQLCondition.make_equal('id', 3), 3], modifications={"data": 4})
# print(result.get_status(), result.get_error(), result.get_sql())
#
# result = table.update_rows(conditions=MySQLCondition.make_equal('id', 3), modifications={"data": 4})
# print(result.get_status(), result.get_error(), result.get_sql())
