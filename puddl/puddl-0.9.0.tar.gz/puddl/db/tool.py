from puddl.typing import URL


def connect_to_db(url: URL):
    """
    throws psycopg2.OperationalError on failure
    """
    import psycopg2
    connection = psycopg2.connect(url)
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
