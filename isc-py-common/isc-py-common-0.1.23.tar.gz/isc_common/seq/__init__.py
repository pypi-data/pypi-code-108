from django.db import connection


def get_deq_next_value(seq_name):
    cursor = connection.cursor()
    cursor.execute(f"select nextval('{seq_name}')")
    result, = cursor.fetchone()
    return result
