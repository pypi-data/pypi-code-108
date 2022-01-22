from typing import Any

import connection_pool
from utils.enums import QueryMode


def query(sql: str, kwargs: dict, data_type: Any, model: QueryMode):
    conn: Any
    cur: Any
    try:
        conn = connection_pool.connection()
        cur = conn.cursor(connection_pool.cursor_type())
        cur.execute(sql, kwargs)

        first_data = cur.fetchone()
        if first_data is None:
            return None

        if model == QueryMode.One:
            return data_type(**first_data)
        elif model == QueryMode.Many:
            return [data_type(**first_data), *[data_type(**i) for i in cur.fetchall()]]
    finally:
        conn.close()
        cur.close()
