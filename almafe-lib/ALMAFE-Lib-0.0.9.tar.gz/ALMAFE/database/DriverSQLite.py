'''
Driver wrapper for sqlite3
'''
import sqlite3

class DriverSQLite():
    '''
    Driver wrapper for sqlite3
    Provides a uniform interface to SQL user code
    '''
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, connectionInfo):
        '''
        Constructor
        :param connectionInfo: dictionary having the items needed to connect to SQLite server
        '''
        self.localDatabaseFile = connectionInfo['localDatabaseFile']
        self.connect()
        
    def connect(self):
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.localDatabaseFile)
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def disconnect(self):
        try:
            self.connection.close()
            self.connection = None
            self.cursor = None
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
        
    def execute(self, query, params = None, commit = False):
        self.cursor = self.connection.cursor()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if commit:
                self.connection.commit()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            print(query)
            return False
    
    def commit(self):
        try:
            self.connection.commit()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
        
    def rollback(self):
        try:
            self.connection.rollback()
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def fetchone(self):
        try:
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def fetchmany(self, chunkSize):
        try:
            result = self.cursor.fetchmany(chunkSize)
            return result
        except Exception as e:
            print(f"SQLite error: {e}")
            return False

    def fetchall(self):
        try:
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
