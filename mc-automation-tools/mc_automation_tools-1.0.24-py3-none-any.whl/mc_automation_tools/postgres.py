"""
This module adapt and provide useful access to postgressSQL DB
"""
import logging
import psycopg2
import json
_log = logging.getLogger('automation_tools.postgress')


class PGClass:
    """
    This class create and provide connection to postgress db host
    """

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password)
        except Exception as e:
            raise ConnectionError(f'Error on connection to DB with error: {str(e)}')

    def command_execute(self, commands):
        try:
            cur = self.conn.cursor()

            for command in commands:
                cur.execute(command)
            cur.close()
            self.conn.commit()

        except (Exception, psycopg2.DatabaseError) as e:
            _log.error(str(e))
            raise e

    # def create_table(self, table_name, primary_key, columns):
    #     """
    #     This method add new table according to provided table_name and
    #     :param table_name: name of new table to create - <str>
    #     :param primary_key: name of PRIMARY_KEY - list of tuples - [(primary_key_str, data_type)]
    #     :param columns: name of other columns + foreign - list of tuples tuple - [(column name_str, data_type str, NULL - True\False, is foreign)]
    #     """
    #     prefix = f"CREATE TABLE {table_name}"
    #
    #     primary_keys_list = []
    #     for key in primary_key:
    #         primary_keys_content = ""
    #         for var in key:
    #             primary_keys_content + " " + var
    #         primary_keys_content + 'PRIMARY KEY'
    #
    #     for key in columns:
    #
    #     pass

    def get_column_by_name(self, table_name, column_name):
        """
        This method return list of column data by providing column name
        """
        command = f"SELECT {column_name} FROM {table_name}"
        try:
            cur = self.conn.cursor()
            cur.execute(command)
            res = cur.fetchall()
            cur.close()
        except Exception as e:
            _log.error(str(e))
            raise e
        return [var[0] for var in res]

    def update_value_by_pk(self, pk, pk_value, table_name, column, value):
        """This method will update column by provided primary key and table name """
        command = f"""UPDATE {table_name} SET "{column}"='{value}' WHERE {pk} = '{pk_value}'"""
        try:
            cur = self.conn.cursor()
            cur.execute(command)

            self.conn.commit()
            cur.close()

        except Exception as e:
            _log.error(str(e))
            raise e

    def polygon_to_geojson(self, column, table_name, pk, pk_value):
        """
        This method query for geometry object and return as geojson format readable
        """
        command = f"""select st_AsGeoJSON({column}) from {table_name} where {pk}='{pk_value}'"""
        try:
            cur = self.conn.cursor()
            cur.execute(command)
            res = cur.fetchall()
            cur.close()
        except Exception as e:
            _log.error(str(e))
            raise e

        return res

    def delete_row_by_id(self, table_name, pk, pk_value):
        """
        Delete entire row by providing key and value [primary key]
        """
        command = f"""delete from "{table_name}" where "{pk}"='{pk_value}'"""
        try:
            cur = self.conn.cursor()
            cur.execute(command)

            self.conn.commit()
            cur.close()

        except Exception as e:
            _log.error(str(e))
            raise e

    def drop_table(self, table_name):
        """
        This method will drop table by providing name of table to drop
        """
        command = f"""DROP TABLE {table_name} CASCADE"""
        cur = self.conn.cursor()
        cur.execute(command)
        self.conn.commit()
        cur.close()

    def truncate_table(self, table_name):
        """
        This method will empty and remove all rows on table by providing name of table to drop
        """
        command = f"""TRUNCATE TABLE {table_name} """
        cur = self.conn.cursor()
        cur.execute(command)
        self.conn.commit()
        cur.close()

    def get_by_n_argument(self, table_name, pk, pk_values, column):
        """
        This method send query with multiple number of pk arguments
        :param table_name: table name
        :param pk: primary key
        :param pk_values: list of arguments
        :param column: column name to get
        """
        for idx, i in enumerate(pk_values):
            pk_values[idx] = f"'{i}'"
        args_str = ','.join(pk_values)
        command = f"""select {column} from {table_name} where {pk} in ({args_str})"""
        try:
            cur = self.conn.cursor()
            cur.execute(command)
            res = cur.fetchall()
            cur.close()
        except Exception as e:
            _log.error(str(e))
            raise e
        res = [r[0] for r in res]
        return res

    def update_multi_with_multi(self, table_name, pk, column, values, type_pk, type_col):
        """
         Insert multiple rows with one query
        """
        update_query = f"""with vals (i,j) as (values"""
        for v in values:
            update_query = update_query + f""" (cast('{v[0]}' as {type_pk}),cast('{v[1]}' as {type_col})),"""
            # update_query = update_query + f""" ('{v[0]}' ,'{v[1]}'),"""
        update_query = update_query[:-1]+")"
        update_query = update_query + f""" update {table_name} set {column} = vals.j from vals where {table_name}.{pk} = vals.i;"""
        # update = f"""update {table_name} set {column} = vals.j from vals where {table_name}.{pk} = vals.i;"""

        # insert_query = f"""insert into {table_name} ({pk}, {column}) values {records_list_template}"""
        cur = self.conn.cursor()
        cur.execute(update_query)
        # cur.execute(update)

        self.conn.commit()
        cur.close()


    def get_rows_by_order(self, table_name, order_key=None, order_desc=False, return_as_dict=False):
        """
        This method will query for entire table rows order by spesific parameter
        """

        asc_desc = 'asc' if not order_desc else 'desc'
        command = f"""select * from "{table_name}" order by "{order_key}" {asc_desc}"""

        try:
            cur = self.conn.cursor()
            cur.execute(command)
            if return_as_dict:
                columns = list(cur.description)
                res = cur.fetchall()

                results = []
                for row in res:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col.name] = row[i]
                    results.append(row_dict)

                return results

            else:
                res = cur.fetchall()
                cur.close()
                return res
        except Exception as e:
            _log.error(str(e))
            raise e


    def get_rows_by_keys(self, table_name, keys_values,order_key=None,order_desc=False,return_as_dict=False):
        """
        This method returns rows that suitable on several keys-values
        :param table_name: table name
        :param keys_values: list of dict with columns keys values
        :param order_key: str of key for ordering query - not mendatory
        :param order_desc: order method - not mendatory as default ASC
        """

        key_value_stat = []
        for key, val in keys_values.items():
            key_value_stat.append(f""""{key}" = '{val}'""")

        key_value_stat = """ and """.join(key_value_stat)

        if not order_key:
            command = f"""select * from "{table_name}" where ({key_value_stat})"""
        else:
            asc_desc = 'asc' if not order_desc else 'desc'
            command = f"""select * from "{table_name}" where ({key_value_stat}) order by "{order_key}" {asc_desc}"""
        try:
            cur = self.conn.cursor()
            cur.execute(command)
            if return_as_dict:
                columns = list(cur.description)
                res = cur.fetchall()

                results = []
                for row in res:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col.name] = row[i]
                    results.append(row_dict)

                return results

            else:
                res = cur.fetchall()
                cur.close()
                return res
        except Exception as e:
            _log.error(str(e))
            raise e
        # res = [r[0] for r in res]
        # return res


