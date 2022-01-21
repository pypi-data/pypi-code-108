import traceback
from aishu.public.mysql_pool import connection

def select(sql):
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        traceback.print_exc()
        return False