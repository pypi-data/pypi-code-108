import cx_Oracle
import sys
import pandas as pd
from sqlalchemy import create_engine, Table, text
from sqlalchemy.orm.session import sessionmaker, Session
from sqlalchemy.schema import DropSchema
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.engine import Engine
from PSAPP.Logging.loggingModule import Logging
from typing import Any, Dict, List, Optional, Tuple
import os
import subprocess

class DBConnection:

    DIALECT = 'oracle'
    DRIVER = 'cx_oracle'

    def __init__(self, mainLogger: Logging =  None) -> None:
        self.__username: str = ''
        self.__password: str = ''
        self.__host: str = ''
        self.__port: int = -1
        self.__serviceName: str = ''
        self.__sid: str = ''
        self.__connStr: str = ''
        self.__engine: Engine = None
        self.__connection: Engine = None
        self.__metadata: MetaData = None
        self.__mainLogger: Logging = mainLogger
        self.__session: Session = None

    def dbConnect(self, dbHost: str, dbPort: int, user: str, password: str, serviceName: str = '', dbSID: str = '') -> None:
        self.__host = dbHost
        self.__port = dbPort
        self.__serviceName = serviceName
        self.__sid = dbSID
        self.__username = user
        self.__password = password
        import PSAPP.test
        try:
            if (user == "sys"):
                self.__connStr = DBConnection.DIALECT + '+' + DBConnection.DRIVER + '://' + self.__username + ':' + self.__password +'@' + self.__host + ':' + str(self.__port) + '/?service_name=' + self.__sid + "&mode=2"
            else:
                self.__connStr = DBConnection.DIALECT + '+' + DBConnection.DRIVER + '://' + self.__username + ':' + self.__password +'@' + self.__host + ':' + str(self.__port) + '/?service_name=' + self.__sid
            print(self.__connStr)
            self.__engine = create_engine(self.__connStr)
            print("Heloo1")
            self.__connection = self.__engine.connect()
            print("Heloo2")
            self.__metadata = MetaData(self.__engine)
            tempSession = sessionmaker(self.__engine)
            self.__session = Session(self.__connection)
            self.__connection.execute(text("alter session set \"_ORACLE_SCRIPT\"=true"))
        except Exception as error:
            print(error)
            # self.__mainLogger.printErrorLog(f"Error while creating DB connection : {error}")
            sys.exit(1)

    def closeConnection(self):
        try:
            self.__connection.close()
        except Exception as error:
            self.__mainLogger.printErrorLog(f"Error while closing connection: {error}")
    
    def executeSelectStatement(self, tableName: str, tableColumns: List[str] = ["*"], whereClause: Optional[List[Tuple[str, str, str]]] = None, sort: Optional[Tuple[str, str]] = None, groupBy: Optional[List[str]] = None) -> pd.DataFrame:
        tableObject = Table(tableName, self.__metadata, autoload=True, autoload_with=self.__engine)
        tempTableColumns = [text(tableColumn) for tableColumn in tableColumns]
        statement = select(columns=tempTableColumns, from_obj=tableObject)
        if (whereClause != None):
            for where in whereClause:
                if (where[1].lower() == "like"):
                    statement.append_whereclause(text(f"UPPER({where[0]}) {where[1]} \'%{where[2]}\'"))
                else:
                    statement.append_whereclause(text(f"UPPER({where[0]}) {where[1]} \'{str(where[2])}\'"))
        if (sort != None):
            statement.append_order_by(text(f"UPPER({tableObject.c.get(sort[0])} {sort[1]}"))
        if (groupBy != None):
            for group in groupBy:
                statement.append_group_by(text(f"{group}"))
        executionResult = self.__connection.execute(statement)
        resultData = executionResult.fetchall()
        df = pd.DataFrame(resultData)
        if (not df.empty):
            if (tableColumns[0] == "*"):
                df.set_axis([*tableObject.c.keys()], axis=1, inplace=True)
            else:
                df.set_axis([*tableColumns], axis=1, inplace=True)
        return df

    def createDirectory(self, directoryName: str, directoryPath: str, usersToGrant: Optional[List[str]] = None):
        createDirStatement = f"CREATE OR REPLACE DIRECTORY {directoryName} AS \'{directoryPath}\'"
        grantDirectoryStatement = f"GRANT READ,WRITE ON DIRECTORY {directoryName} TO "
        for user in usersToGrant:
            grantDirectoryStatement = grantDirectoryStatement + user + " "
        self.__connection.execute(text(createDirStatement))
        self.__connection.execute(text(grantDirectoryStatement))
        self.__session.commit()

    def executeStatement(self, statement: Any):
        print("Inside execution statement!")
        self.__connection.execute(statement)
        print("Finished executing statement!")
        print("Start with commit!")
        self.__session.commit()
        print("Finish Commit!")


    def executeSqlFile(self, filePath: str):
        with open(filePath, 'r') as file:
            sqlFileLines = file.readlines()
            sql_command = ''
            for line in sqlFileLines:
                if not line.startswith('--') and line.strip('\n'):
                    sql_command += " " + line.strip('\n')
                    if (sql_command.endswith(';')):
                        sql_command = sql_command.replace(";", "\n")
                        try:
                            self.__connection.execute(text(sql_command))
                            self.__session.commit()
                        except Exception as error:
                            print(f'An error while executing sql file {error}')
                        finally:
                            sql_command = ''
                    elif (sql_command.endswith("/")):
                        sql_command = sql_command.replace("/", "\n")
                        try:
                            self.__connection.execute(text(sql_command))
                            self.__session.commit()
                        except Exception as error:
                            print(f'An error while executing sql file {error}')
                        finally:
                            sql_command = ''

    def dropSchema(self, schemaName: str):
        self.executeStatement(text("ALTER SYSTEM ENABLE RESTRICTED SESSION"))
        print("**************************************\n\n")
        print(schemaName)
        self.executeStatement(text(f"begin for x in (select Sid, Serial# from v$session where lower(username) = lower('{schemaName}')) loop execute immediate 'Alter System Kill Session '''|| x.Sid || ',' || x.Serial# || ''' IMMEDIATE'; end loop; end;"))
        statement: Any = text(f"DROP USER {schemaName} CASCADE")
        self.executeStatement(statement)
        self.executeStatement(text("ALTER SYSTEM DISABLE RESTRICTED SESSION"))

    def compileAllInvalidObjects(self, schemaName: str):
        self.executeStatement(text(f"BEGIN DBMS_UTILITY.compile_schema(schema => '{schemaName}'); END;"))

    def executeProcedureFile(self, filePath: str):
        print(f"In execute procedure file for: {filePath}")
        toExecute: str = ''
        with open(filePath, 'r') as file:
            fileData = file.readlines()
            for line in fileData:
                toExecute += f" {line}"
        print(toExecute)
        self.__connection.execute(toExecute)
    
    def dropTableData(self, schemaName: str, tableName: str):
        self.__connection.execute(text(f"DELETE FROM {schemaName}.{tableName}"))
    
    def disableAllTableTriggers(self, schemaName: str, tableName: str):
        self.__connection.execute(text(f"ALTER TABLE {schemaName}.{tableName} DISABLE ALL TRIGGERS"))
    
    def enableAllTableTriggers(self, schemaName: str, tableName: str):
        self.__connection.execute(text(f"ALTER TABLE {schemaName}.{tableName} ENABLE ALL TRIGGERS"))
    
    def dropSynonym(self, schemaName: str, synonymnName: str):
        self.__connection.execute(text(f"DROP SYNONYM {schemaName}.{synonymnName} FORCE"))
    
    def executeUpdateStatement(self, schemaName: str, tableName: str, columnsToUpdate: List[str], newValues: List[Any], whereClause: Optional[List[Tuple[str, str, str]]] = None):
        updateSatement = f"UPDATE {schemaName}.{tableName}"
        for index, column in enumerate(columnsToUpdate):
            updateSatement += f" SET {column}={newValues[index]}"
        for where in whereClause:
            updateSatement += f" WHERE UPPER({where[0]}) {where[1]} {where[2]}"
        # updateSatement += ";"
        self.__connection.execute(text(updateSatement))