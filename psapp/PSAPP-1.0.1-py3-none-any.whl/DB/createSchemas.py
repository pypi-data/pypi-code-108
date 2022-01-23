import os
from pandas import DataFrame
from sqlalchemy import text
from PSAPP.DB.dbConnection import DBConnection

class SchemasCreation:

    def __init__(self, dbConnection: DBConnection) -> None:
        self.__dbConnection: DBConnection = dbConnection
        self.__sourceFile: str = ''
        self.__tempFile: str = ''
        self.__currentUserNames: DataFrame = self.__dbConnection.executeSelectStatement("ALL_USERS", ["username"])

    def createSchema(self, schemaName: str, schemaPass: str, schemaType: int):
        if (schemaName in self.__currentUserNames["username"].to_list()):
            print(f"Inisde drop user {schemaName}!")
            self.__dbConnection.dropSchema(schemaName)
            print("Finish drop user!")
        self.schemaFileParsing(schemaName=schemaName, schemaPass=schemaPass, schemaType=schemaType)
        self.__dbConnection.executeSqlFile(self.__tempFile)
        os.unlink(self.__tempFile)

    def schemaFileParsing(self, schemaName: str, schemaPass: str, schemaType: int):
        if (schemaType == 1):
            self.__sourceFile = os.path.join(os.path.dirname(__file__), "resources", "secUser.sql")
            self.__tempFile = os.path.join(os.path.dirname(__file__), "resources", "tempSecUser.sql")
            sFile = open(self.__sourceFile, 'r')
            data = sFile.readlines()
            with open(self.__tempFile, "w") as fOut:
                for line in data:
                    if ("_SEC_USER_" in line):
                        line = line.replace("_SEC_USER_", schemaName)
                    if ("_SEC_PASS_" in line):
                        line = line.replace("_SEC_PASS_", schemaPass)
                    fOut.write(line + "\n")
            sFile.close()
        elif (schemaType == 10):
            self.__sourceFile = os.path.join(os.path.dirname(__file__), "resources", "appUser.sql")
            self.__tempFile = os.path.join(os.path.dirname(__file__), "resources", "tempAppUser.sql")
            sFile = open(self.__sourceFile, 'r')
            data = sFile.readlines()
            with open(self.__tempFile, "w") as fOut:
                for line in data:
                    if ("_APP_USER_" in line):
                        line = line.replace("_APP_USER_", schemaName)
                    if ("_APP_PASS_" in line):
                        line = line.replace("_APP_PASS_", schemaPass)
                    fOut.write(line + "\n")
            sFile.close()