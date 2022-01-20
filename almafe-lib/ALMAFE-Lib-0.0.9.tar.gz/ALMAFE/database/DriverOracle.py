'''
Driver wrapper for cx_Oracle
'''
import cx_Oracle

class DriverOracle():
    '''
    Driver wrapper for cx_Oracle
    Provides a uniform interface to SQL user code
    '''

    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, connectionInfo):
        '''
        Constructor
        :param connectionInfo: dictionary having the items needed to connect to Oracle server
                {'host', 'user', 'passwd', 'service_name', 'schema', 'port' : 1521, 'encoding' : 'UTF-8'}

        '''
        self.host = connectionInfo['host']
        self.user = connectionInfo['user']
        self.passwd = connectionInfo['passwd']
        self.service_name = connectionInfo['service_name']        
        self.port = connectionInfo.get('port', 1521)
        self.schema = connectionInfo.get('schema', None)
        encoding = connectionInfo.get('encoding', 'UTF-8')
        self.connection = None
        self.cursor = None
        self.connect(encoding = encoding)
        
    def connect(self, encoding = 'UTF-8'):
        '''
        Connect to the database.
        :param encoding: str defaults to 'UTF-8'
        :return True/False
        '''
        self.connection = None
        try:
            connString = "{}:{}/{}".format(self.host, self.port, self.service_name)
            if self.connection:
                self.connection.close()
            self.connection = cx_Oracle.connect(self.user, self.passwd, connString, encoding=encoding)
            self.cursor = self.connection.cursor()
            if self.schema:
                self.cursor.execute('ALTER SESSION SET CURRENT_SCHEMA = "{}"'.format(self.schema))
            return True
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False

    def disconnect(self):
        '''
        Disconnect from the database.
        :return True/False
        '''
        try:
            self.connection.close()
            self.connection = None
            self.cursor = None
            return True
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False
        
    def execute(self, query, params = None, commit = False):
        '''
        Execute an SQL query.
        :param query: str
        :param params: list (by position) or dict (by tag name) of values to assign to bind variables in the query. 
                Bind variables are names prefixed by a colon. E.g. :my_var        
        :param commit: If True, commit INSERT/UPDATE/DELETE queries immediately.
        :return True/False
        '''
        try:
            self.cursor.execute(query)
            if commit:
                self.connection.commit()
            return True
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            print(query)
            return False
    
    def commit(self):
        '''
        Commit any previously executed but not yet committed INSERT/UPDATE/DELETE queries.
        :return True/False
        '''
        try:
            self.connection.commit()
            return True
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False
        
    def rollback(self):
        '''
        Rollback any previously executed but not yet committed INSERT/UPDATE/DELETE queries.
        :return True/False
        '''
        try:
            self.connection.rollback()
            return True
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False

    def fetchone(self):
        '''
        Fetch one row from the last SELECT query.
        :return tuple or False
        '''
        try:
            row = self.cursor.fetchone()
            return row
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False    

    def fetchmany(self, chunkSize):
        '''
        Fetch multiple rows from the last SELECT query.
        :param chunkSize: max number of rows to fetch
        :return list of tuple or False
        '''
        try:
            result = self.cursor.fetchmany(chunkSize)
            return result
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False
        
    def fetchall(self):
        '''
        Fetch all rows from the last SELECT query.
        :return list of tuple or False
        '''
        try:
            result = self.cursor.fetchall()
            return result
        except cx_Oracle.Error as e:
            print(f"cx_Oracle error: {e}")
            return False

