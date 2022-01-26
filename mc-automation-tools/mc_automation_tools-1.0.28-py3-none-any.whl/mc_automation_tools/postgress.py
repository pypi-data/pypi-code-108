"""
This module adapt and provide useful access to postgressSQL DB
"""
import logging
import psycopg2
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
