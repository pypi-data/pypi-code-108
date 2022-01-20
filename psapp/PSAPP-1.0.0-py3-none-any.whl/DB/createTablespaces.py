from sqlalchemy import sql, text
from sqlalchemy.engine import Engine
from PSAPP.DB.dbConnection import DBConnection
import sys
import os

class TableSpacesCreation:

    def __init__(self, dbConnection: DBConnection) -> None:
        self.__sourceFile: str = ''
        self.__tempFile: str = ''
        self.__dbConnection: DBConnection = dbConnection

    def createTableSpace(self, tablespacePath: str = None):
        self.__sourceFile = os.path.join(os.path.dirname(__file__), "resources", "tablespace.sql")
        self.__tempFile = os.path.join(os.path.dirname(__file__), "resources", "tempTablespace.sql")
        self.parseTablespaceFile(tablespacePath)
        self.__dbConnection.executeSqlFile(self.__tempFile)
        os.unlink(self.__tempFile)

    def parseTablespaceFile(self, tablespacePath: str = None):
        if (tablespacePath != None):
            if (not (tablespacePath.endswith("\\") or tablespacePath.endswith("/"))):
                if (sys.platform == "win32"):
                    tablespacePath = tablespacePath + "\\"
                else:
                    tablespacePath = tablespacePath + "/"
            file = open(self.__sourceFile, 'r')
            data = file.readlines()
            with open(self.__tempFile, "w") as fOut:
                for line in data:
                    if ("_TO_BE_CHANGED_" in line):
                        fOut.write(line.replace("_TO_BE_CHANGED_", tablespacePath))
                    else:
                        fOut.write(line + "\n")
            file.close()
        else:
            file = open(self.__sourceFile, 'r')
            data = file.readlines()
            with open(self.__tempFile, "w") as fOut:
                for line in data:
                    if ("_TO_BE_CHANGED_" in line):
                        fOut.write(line.replace("_TO_BE_CHANGED_", ""))
                    else:
                        fOut.write(line + "\n")
            file.close()