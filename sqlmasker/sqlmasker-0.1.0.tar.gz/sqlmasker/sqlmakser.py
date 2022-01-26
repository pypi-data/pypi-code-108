import sqlite3, typing

class Sql():
    def __init__(self, db: typing.Union[str] = 'db.db'):
        self.db = sqlite3.connect(db)
        self.sql = self.db.cursor()

    def execute(self, value=None,
                data_: typing.Union[list, dict, str] = None):
        db = self.db
        sql = self.sql
        try:
            if data_ == None or not data_:
                sql.execute(value)
            else:
                sql.execute(value, data_)
            db.commit()
            return True
        except Exception as ex:
            return ex

    def fetch(self, method: typing.Union[str] = None,
              value: typing.Union[str] = None,
              whofetch: typing.Union[list, dict, str, None] = None,
              *args, **kwargs):
        if method == 'one' or method == 'all':
            try:
                sql = self.sql
                if method == 'one':
                    m = sql.execute(value, whofetch).fetchone()
                    return m
                else:
                    m = sql.execute(value, whofetch).fetchall()
                    return m
            except:
                return False

    def chooseBread(self, what=None, from_=None, where=None, values=None):
        try:
            sql = self.sql
            if not where is None or not where:
                if not values is None or not values:
                    a = sql.execute(f'SELECT {what} FROM {from_} WHERE {where} = ?', values).fetchone()
                    return a
        except:
            return False
    def createTable(self, tableName: str, values: str, ifnotexists: bool):
        try:
            sql = self.sql
            db = self.db
            if ifnotexists == True:
                sql.execute(f'CREATE TABLE IF NOT EXISTS {tableName} {values}')
                db.commit()
            else:
                sql.execute(f'CREATE TABLE {tableName} {values}')
                db.commit()
            return {
                'created': True,
                'ifNotExist': ifnotexists
            }

        except:
            return {
                'created': False
            }
    def insertBlue(self, table=None, values=None, count_=None):
        sql = self.sql
        db = self.db
        ques = ''
        for x in range((count_)):
            if ques.count('?') == count_-1:
                ques += '?'
            else:
                ques += '?,'


        sql.execute(f'INSERT INTO {table} VALUES ({ques})', values)
        db.commit()
        return True

#from sqlmasker import Sql
#
#sql = Sql(db="my_database.db")
#

#coded by nikprotect