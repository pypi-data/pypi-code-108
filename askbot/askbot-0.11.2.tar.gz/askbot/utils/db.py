from django.db import connection

def table_exists(table_name):
    cursor = connection.cursor()
    return table_name in connection.introspection.get_table_list(cursor)
