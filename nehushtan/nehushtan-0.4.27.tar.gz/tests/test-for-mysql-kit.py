from pymysql import MySQLError, InterfaceError

from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLKitConfig import MySQLKitConfig
from tests.config import MYSQL_CONFIG

db = MySQLKit(MySQLKitConfig(MYSQL_CONFIG))

cursor = db.get_raw_connection().cursor()
cursor.execute("select id,data from a limit 2")
all = cursor.fetchall()
print('first', all)

db.get_raw_connection().close()
try:
    cursor.execute("select id,data from a limit 2")
    all = cursor.fetchall()
    print('second', all)
except InterfaceError as ie:
    print(ie, ie.__cause__)
except MySQLError as e:
    print(e)
    print(e.__class__, e.__class__.__doc__)
