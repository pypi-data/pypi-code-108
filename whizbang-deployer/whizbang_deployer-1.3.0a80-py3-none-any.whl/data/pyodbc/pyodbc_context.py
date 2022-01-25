import pyodbc
import logging

_log = logging.getLogger(__name__) 

class PyodbcContext:
    def __init__(self, server, database, username, password):
        self._connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD={' + password + '}',
            autocommit=True)

    def execute_statements(self, statements: 'list[str]'):
        cursor = self._connection.cursor()
        results = []
        for statement in statements:

            try:
                result = cursor.execute(statement)
                _log.info(results)
                results.append(result)
            except Exception as ex:
                _log.exception(f'sql_server statement error: {ex}')
                raise ex
        return results
