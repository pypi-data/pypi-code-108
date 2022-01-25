import os
from mysql.connector import connect
from dotenv import load_dotenv

# table imports
from src.lib.tables.users import UsersTable


# load environment variables
load_dotenv()


class Initializer():

    def __init__(self):
        self.host = os.environ.get('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.connection = connect(
			host=self.host,
			user=self.user,
			password=self.password,
		)

    def get_cursor(self):
        return self.connection.cursor()

    def create_db_if_not_exists(self, db_name=None):
        ''' First SQL scripts to ensure the database actually exists and to use it '''

        if db_name is None:
            db_name = os.getenv('DB_NAME')
        else:
            os.setenv('DB_NAME', db_name)

        sql = "CREATE DATABASE IF NOT EXISTS {db_name}".format(db_name=db_name)

        cursor = self.get_cursor()
        cursor.execute(sql)

        self.connection.commit()

        sql = "USE {db_name}".format(db_name=db_name)

        cursor = self.get_cursor()
        cursor.execute(sql)

        print('Database {} successfully created/already exists and has been set.'.format(db_name))

        # finally attempt to initialize the tables in case some are missing

    def create_db_tables(self):
        ''' Waiting for tables and their individual methods '''
        pass

    def create_users_tables(self):

        users_table = UsersTable('users', if_not_exists=True)
        users_table_sql = users_table.__str__()
        
        return users_table_sql