import pandas as pd
import psycopg2 as p


def overwrite_pg_tbl(df:pd.DataFrame, tbl_nm:str, conn:p.extensions.connection):
    sql_columns = ",".join(df.columns)
    sql_values = "VALUES({})".format(",".join(["%s" for _ in sql_columns]))
    drop_tbl_sql = "DROP TABLE IF EXISTS {};".format(tbl_nm)
    insert_stmt = "INSERT INTO {} ({}) {}".format(
        tbl_nm, sql_columns, sql_values)
    cur = conn.cursor()
    cur.execute(drop_tbl_sql)
    conn.commit()
    p.extras.execute_batch(cur, insert_stmt, df.values)
    conn.commit()
    cur.close()
    return True