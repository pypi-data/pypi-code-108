from django.db import connection


def get_current_database_id():
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        database_name = cursor.fetchone()[0]

        cursor.execute("SELECT oid FROM pg_database WHERE datname = %s", [database_name])
        database_id = cursor.fetchone()[0]

        return database_id
