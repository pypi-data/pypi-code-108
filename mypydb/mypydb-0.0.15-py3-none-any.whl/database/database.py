import os
from mysql.connector import connect
from dotenv import load_dotenv


load_dotenv()


class Database():
    
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.connection = connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        
        # check if database exists and create it if it doesn't exist
        cursor = self.connection.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS {db_name}'.format(db_name=os.getenv('DB_NAME')))
        self.connection.commit()
        
        # set the connection's database to the created one
        self.connection.database = os.getenv('DB_NAME')
    
    def get_cursor(self):
        ''' Return the cursor for the database connection '''
        
        cursor = self.connection.cursor()
        return cursor
    
    def create_table(self, table_sql):
        ''' Create a table using a generated SQL statement '''
        
        cursor = self.get_cursor()
        cursor.execute(table_sql)
        
        self.connection.commit()
    
    def select_all_rows(self, table):
        ''' Select all rows in the specified table '''
        
        sql = "SELECT * FROM {table}".format(table=table)
        
        cursor = self.get_cursor()
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        
        return rows
    
    def select_by_id(self, table, row_id):
        ''' Select a single row from a table with the specified id '''
        
        sql = "SELECT * FROM {table} WHERE id = {row_id}".format(table=table, row_id=row_id)
        
        cursor = self.get_cursor()
        cursor.execute(sql)
        
        row = cursor.fetchone()
        
        return row
    
    def select_where(self, table, column, value, limit=None):
        ''' Selects all rows with a specific value from the given column with an optional limit '''
        
        sql = "SELECT * FROM {table} WHERE {column} = %s".format(table=table, column=column)
        
        if limit is not None and limit > 0:
            sql += " LIMIT {limit}".format(limit=limit)
        
        values = (value, )
        
        cursor = self.get_cursor()
        cursor.execute(sql, values)
        
        rows = cursor.fetchall()
        
        return rows