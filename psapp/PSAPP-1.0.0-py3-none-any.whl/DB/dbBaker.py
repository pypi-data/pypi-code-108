from multiprocessing import connection
import os
import collections
import copy
from typing import Any, Optional, Tuple, List
from pandas.core.frame import DataFrame
from sqlalchemy.engine import Engine
from sqlalchemy import text
from PSAPP.Logging.loggingModule import Logging
from PSAPP.DB.dbConnection import DBConnection
from PSAPP.DB.createTablespaces import TableSpacesCreation
from PSAPP.DB.createSchemas import SchemasCreation
from PSAPP.DB.importDumps import ImportDumps
from PSAPP.DB.sshConnection import SSHConnection
from PSAPP.appsReader import AppsReader

class DBBaker:

    def __init__(self, mainLogger: Logging = None) -> None:
        self.__mainLogger: Logging = mainLogger
        self.__dbInfo: dict = {}
        self.__deployConnection: DBConnection = None
        self.__sqlplusPath: str = ''
        self.__schemaNames: list = []
        self.__dumpsToImport: list = []
        self.__remapParsing: list = []
        self.__remapKeys: list = []
        self.__remapValues: list = []
        self.__schemasPriority: dict = {}

    def deployDB(self, data: dict) -> None:
        self.__mainLogger.printDebugLog("\n**********\nStart with deploying DB!\n**********\n")
        self.__data = data
        self.__parseAppsInfo(data["DB_INFO"]["APPS_SCHEMAS_INFO"])
        if (data["DB_INFO"]["IMPORT_DUMPS_INFO"]["IMPORT_DUMPS"]):
            self.__parseDumpsRef(data["DB_INFO"]["IMPORT_DUMPS_INFO"])
        for node in data["DB_INFO"]["DB_NODES"]:
            nodeValue, nodeKey = self.__nodesParsing(node)
            self.__deployConnection = DBConnection()
            self.__deployConnection.dbConnect(dbHost=nodeValue["DB_IP"], dbPort=nodeValue["DB_PORT"], dbSID=nodeValue["DB_SID"], user="sys", password=nodeValue["SYS_PASS"])
            if (data["DB_INFO"]["IMPORT_DUMPS_INFO"]["RECREATE_TABLESPACES"] == True):
                self.__createTableSpaces(data["DB_INFO"]["IMPORT_DUMPS_INFO"]["TABLESPACES_PATH"])
            if (data["DB_INFO"]["IMPORT_DUMPS_INFO"]["RECREATE_USERS"] == True):
                self.__recreateUsers(data["DB_INFO"]["APPS_SCHEMAS_INFO"])
            if (data["DB_INFO"]["DB_DEPLOYMENT_METHODOLOGY"] == 1):
                self.releaseScriptDeployment(data)
            elif (data["DB_INFO"]["DB_DEPLOYMENT_METHODOLOGY"] == 2):
                self.dumpsImportDeployment(data, nodeValue)
        return self.__deployConnection

    def __dataParse(self, data: dict):
        self.__dbInfo = data["DB_INFO"]

    def __nodesParsing(self, node: dict) -> Tuple[dict, dict]:
        nodeValue = list(node.values())[0]
        nodeKey = list(node.keys())[0]
        return (nodeValue, nodeKey)

    def releaseScriptDeployment(self, data: dict) -> None:
        pass
    
    def __createTableSpaces(self, tableSpacePath: None):
        tablespacesCreation = TableSpacesCreation(self.__deployConnection)
        if (tableSpacePath != None):
            tablespacesCreation.createTableSpace(tableSpacePath)
        else:
            tablespacesCreation.createTableSpace()

    def __recreateUsers(self, appsSchemasInfo: dict):
        print("Start creation users!")
        createShemasObj = SchemasCreation(self.__deployConnection)
        for item in appsSchemasInfo:
            itemKey = [*item.keys()][0]
            if ((1 == itemKey or 2 == itemKey) and item[itemKey]["USERNAME"] in self.__schemaNames):
                createShemasObj.createSchema(item[itemKey]["USERNAME"], item[itemKey]["PASSWORD"], 1)
            elif (item[itemKey]["USERNAME"] in self.__schemaNames):
                createShemasObj.createSchema(item[itemKey]["USERNAME"], item[itemKey]["PASSWORD"], 10)

    def __secImport(self, item, nodeValue, data, schemaToBeImported, schemaNameAsInDB, importDumpsObj: ImportDumps, sec: bool):
        existAction = "APPEND"
        content = "METADATA_ONLY"
        firstLoop = True
        secondLoop = False
        thirdLoop = False
        if (sec):
            rangeLoop = 2
        else:
            rangeLoop = 3
        for loop in range(rangeLoop):
            print(loop)
            if (firstLoop == False and secondLoop == True and thirdLoop == False):
                content = "ALL"
                secondLoop = False
                thirdLoop = True
                if (schemaNameAsInDB != self.__schemasPriority[1]["USERNAME"]):
                    print("**********************************")
                    print(f"In disable the constraints for {schemaNameAsInDB}")
                    self.__disableConstraintsParsing(schemaNameAsInDB)
                    self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                # else:
                #     continue
            elif (firstLoop == False and secondLoop == False and thirdLoop == True):
                if (schemaNameAsInDB != self.__schemasPriority[1]["USERNAME"]):
                    self.__secGrantsToUser(self.__schemasPriority[1]["USERNAME"], schemaNameAsInDB)
                    self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql"))
                    os.unlink(os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql"))
                    if (self.__synonymsParsing(schemaNameAsInDB)):
                        self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "updatedSynonyms.sql"))
                        self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "synonymsGrants.sql"))
                else:
                    continue
            else:
                firstLoop = False
                secondLoop = True
            print("Helloooooo")
            print("*******************************************")
            importDumpsObj.importDump(
                dbIP=nodeValue["DB_IP"],
                dbPort=nodeValue["DB_PORT"],
                dbSID=nodeValue["DB_SID"],
                dataPump=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["DATA_PUMP"],
                dumpPath=os.path.split(item["DUMP_PATH"])[1],
                content=content,
                logFile=item["LOGFILE"],
                parFilePath=item["PAR_FILE_PATH"],
                remapSchemas=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["REMAP_SCHEMAS"],
                schemas=[schemaToBeImported],
                tableExistAction=existAction,
                user="system",
                directory="PSDEPLOY",
                userPass=nodeValue["SYSTEM_PASS"],
                osUsername=nodeValue["OS_USERNAME"],
                osPassword=nodeValue["OS_PASSWORD"],
                version=item["VERSION"]
            )
            existAction = "REPLACE"
            if (loop == 1 and schemaNameAsInDB == self.__schemasPriority[1]["USERNAME"]):
                print("Hellowwwrdsdsds")
                print("*******************************************")
                self.__disableConstraintsParsing(schemaNameAsInDB)
                self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                self.__createSecUsers(schemaNameAsInDB)
                self.__deployConnection.disableAllTableTriggers(schemaNameAsInDB, "SEC_USERS")
                self.__deployConnection.dropTableData(schemaNameAsInDB, "SEC_USERS")
                self.__deployConnection.executeStatement(text("ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY HH24:MI:SS'"))
                self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "adminUserTemp.sql"))
                self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "systemUserTemp.sql"))
                self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "rootUserTemp.sql"))
                self.__enableConstraintsParsing(schemaNameAsInDB)
                self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql"))
                self.__deployConnection.enableAllTableTriggers(schemaNameAsInDB, "SEC_USERS")
                os.unlink(os.path.join(os.path.dirname(__file__), "resources", "adminUserTemp.sql"))
                os.unlink(os.path.join(os.path.dirname(__file__), "resources", "systemUserTemp.sql"))
                os.unlink(os.path.join(os.path.dirname(__file__), "resources", "rootUserTemp.sql"))
                os.unlink(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                os.unlink(os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql"))
            if (firstLoop == False and secondLoop == False and thirdLoop == True and loop == 2):
                if (schemaNameAsInDB != self.__schemasPriority[1]["USERNAME"]):
                    content = "ALL"
                    self.__createSecUsers(schemaNameAsInDB)
                    self.__disableConstraintsParsing(schemaNameAsInDB)
                    self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                    self.__deployConnection.disableAllTableTriggers(schemaNameAsInDB, "SEC_USERS")
                    self.__deployConnection.dropTableData(schemaNameAsInDB, "SEC_USERS")
                    self.__deployConnection.executeStatement(text("ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY HH24:MI:SS'"))
                    self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "adminUserTemp.sql"))
                    self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "systemUserTemp.sql"))
                    self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "rootUserTemp.sql"))
                    self.__deployConnection.enableAllTableTriggers(schemaNameAsInDB, "SEC_USERS")
                    self.__enableConstraintsParsing(schemaNameAsInDB)
                    self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql"))
                    os.unlink(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                    os.unlink(os.path.join(os.path.dirname(__file__), "resources", "adminUserTemp.sql"))
                    os.unlink(os.path.join(os.path.dirname(__file__), "resources", "systemUserTemp.sql"))
                    os.unlink(os.path.join(os.path.dirname(__file__), "resources", "rootUserTemp.sql"))
                    os.unlink(os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql"))
        for i in self.__data["APP_INFO"]["MODULES"]:
            moduleType = list(i.keys())[0]
            tomcatID = list(i.values())[0]["TOMCAT_REFERENCE"]
            for tomcat in self.__data["TOMCAT_INFO"]["TOMCAT_REFERENCE"]:
                if (tomcatID == list(tomcat.keys())[0]):
                    connectorPort = list(tomcat.values())[0]["CONNECTER_PORT"]
                    if (self.__data["APP_INFO"]["LOAD_BALANCER_URL"] != None):
                        if (moduleType in list(AppsReader.secModulesMapping.keys())):
                            self.updateSecAppInstances(schemaNameAsInDB, data["APP_INFO"]["LOAD_BALANCER_URL"], connectorPort, moduleType, AppsReader.secModulesMapping[moduleType])
                        elif (moduleType in list(AppsReader.appModulesMapping.keys())):
                            self.updateSecAppInstances(schemaNameAsInDB, data["APP_INFO"]["LOAD_BALANCER_URL"], connectorPort, moduleType, AppsReader.appModulesMapping[moduleType])
                    else:
                        if (moduleType in list(AppsReader.secModulesMapping.keys())):
                            self.updateSecAppInstances(schemaNameAsInDB, list(data["APP_INFO"]["APP_NODES"][0].values())[0]["NODE_IP"], connectorPort, moduleType, AppsReader.secModulesMapping[moduleType])
                        elif (moduleType in list(AppsReader.appModulesMapping.keys())):
                            self.updateSecAppInstances(schemaNameAsInDB, list(data["APP_INFO"]["APP_NODES"][0].values())[0]["NODE_IP"], connectorPort, moduleType, AppsReader.appModulesMapping[moduleType])

    def __appImport(self, item, nodeValue, data, schemaToBeImported, schemaNameAsInDB, importDumpsObj, lastLoop: bool):
        if (not lastLoop):
            existAction = "APPEND"
            content = "METADATA_ONLY"
            firstLoop = True
            secondLoop = False
            thirdLoop = False
            rangeLoop = 2
            for loop in range(rangeLoop):
                if (firstLoop == False and secondLoop == True and thirdLoop == False):
                    content = "ALL"
                    secondLoop = False
                    thirdLoop = True
                    if (schemaNameAsInDB != self.__schemasPriority[1]["USERNAME"]):
                        self.__disableConstraintsParsing(schemaNameAsInDB)
                        self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                        if (1 in self.__schemasPriority):
                            self.__secGrantsToUser(self.__schemasPriority[1]["USERNAME"], schemaNameAsInDB)
                            self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql"))
                            os.unlink(os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql"))
                        if (2 in self.__schemasPriority):
                            self.__secGrantsToUser(self.__schemasPriority[2]["USERNAME"], schemaNameAsInDB)
                            self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql"))
                            os.unlink(os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql"))
                        os.unlink(os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql"))
                    else:
                        continue
                else:
                    firstLoop = False
                    secondLoop = True
                importStatement = importDumpsObj.importDump(
                    dbIP=nodeValue["DB_IP"],
                    dbPort=nodeValue["DB_PORT"],
                    dbSID=nodeValue["DB_SID"],
                    dataPump=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["DATA_PUMP"],
                    dumpPath=os.path.split(item["DUMP_PATH"])[1],
                    content=content,
                    logFile=item["LOGFILE"],
                    parFilePath=item["PAR_FILE_PATH"],
                    remapSchemas=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["REMAP_SCHEMAS"],
                    schemas=[schemaToBeImported],
                    tableExistAction=existAction,
                    user="system",
                    directory="PSDEPLOY",
                    userPass=nodeValue["SYSTEM_PASS"],
                    osUsername=nodeValue["OS_USERNAME"],
                    osPassword=nodeValue["OS_PASSWORD"],
                    version=item["VERSION"]
                )
                existAction = "REPLACE"
        else:
            content = "ALL"
            existAction = "REPLACE"
            # if (schemaNameAsInDB != self.__schemasPriority[2]["USERNAME"]):
            if (self.__synonymsParsing(schemaNameAsInDB)):
                self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "updatedSynonyms.sql"))
                self.__deployConnection.executeSqlFile(os.path.join(os.path.dirname(__file__), "resources", "synonymsGrants.sql"))
            importStatement = importDumpsObj.importDump(
                dbIP=nodeValue["DB_IP"],
                dbPort=nodeValue["DB_PORT"],
                dbSID=nodeValue["DB_SID"],
                dataPump=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["DATA_PUMP"],
                dumpPath=os.path.split(item["DUMP_PATH"])[1],
                content=content,
                logFile=item["LOGFILE"],
                parFilePath=item["PAR_FILE_PATH"],
                remapSchemas=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["REMAP_SCHEMAS"],
                schemas=[schemaToBeImported],
                tableExistAction=existAction,
                user="system",
                directory="PSDEPLOY",
                userPass=nodeValue["SYSTEM_PASS"],
                osUsername=nodeValue["OS_USERNAME"],
                osPassword=nodeValue["OS_PASSWORD"],
                version=item["VERSION"]
            )
            self.__enableConstraintsParsing(schemaNameAsInDB)
            self.__deployConnection.executeProcedureFile(os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql"))
            os.unlink(os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql"))
    
    def dumpsImportDeployment(self, data: dict, nodeValue: Any = None) -> None:
        if (self.__deployConnection == None):
            self.__parseAppsInfo(data["DB_INFO"]["APPS_SCHEMAS_INFO"])
            self.__parseDumpsRef(data["DB_INFO"]["IMPORT_DUMPS_INFO"])
            for node in data["DB_INFO"]["DB_NODES"]:
                nodeValue, nodeKey = self.__nodesParsing(node)
                self.__deployConnection = DBConnection()
                self.__deployConnection.dbConnect(dbHost=nodeValue["DB_IP"], dbPort=nodeValue["DB_PORT"], dbSID=nodeValue["DB_SID"], user="sys", password=nodeValue["SYS_PASS"])
                self.__createTableSpaces(data["DB_INFO"]["IMPORT_DUMPS_INFO"]["TABLESPACES_PATH"])
                self.__recreateUsers(data["DB_INFO"]["APPS_SCHEMAS_INFO"])
        importDumpsObj = ImportDumps(self.__deployConnection)
        tempSchemaNames = copy.deepcopy(self.__schemaNames)
        tempAppDumpsInfo: List[dict] = []
        for index, item in enumerate(self.__dumpsToImport):
            print("IN DUMPS TO IMPORT LOOP")
            dumpPath = item["DUMP_PATH"]
            sshConnection = SSHConnection(nodeValue["DB_IP"], nodeValue["OS_USERNAME"], nodeValue["OS_PASSWORD"])
            if (sshConnection.checkIfWindows()):
                envValue = sshConnection.getEnvVariable(True)
                dumpPath = envValue + "\\Desktop\\TOOL_DUMPS" # + os.path.split(item["DUMP_PATH"])[1]
                sshConnection.transferFile(item["DUMP_PATH"], dumpPath, True)
                if (data["DB_INFO"]["IMPORT_DUMPS_INFO"]["CREATE_DIRECTORY"]):
                    self.__deployConnection.createDirectory("PSDEPLOY", envValue + "\\Desktop\\TOOL_DUMPS\\", ["system"])
            else:
                envValue = sshConnection.getEnvVariable(False)
                dumpPath = envValue + "/TOOL_DUMPS" # + os.path.split(item["DUMP_PATH"])[1]
                sshConnection.transferFile(item["DUMP_PATH"], dumpPath, False)
                if (data["DB_INFO"]["IMPORT_DUMPS_INFO"]["CREATE_DIRECTORY"]):
                    self.__deployConnection.createDirectory("PSDEPLOY", envValue + "/TOOL_DUMPS/", ["system"])
            
            self.__remapKeys = list(data["DB_INFO"]["IMPORT_DUMPS_INFO"]["REMAP_SCHEMAS"].keys())
            self.__remapValues = list(data["DB_INFO"]["IMPORT_DUMPS_INFO"]["REMAP_SCHEMAS"].values())
            schemasInImport: list = []
            if (len(self.__remapKeys) == 0):
                schemasInImport = item["SCHEMAS"]
            else:
                for schemaName in item["SCHEMAS"]:
                    if (schemaName not in self.__remapValues):
                        schemasInImport.append(schemaName)
                    else:
                        schemasInImport.append(self.__remapKeys[self.__remapValues.index(schemaName)])
            if (item["CONTENT"] == "ALL"):
                for schemaToBeImported in schemasInImport:
                    if (1 in self.__schemasPriority.keys() and (schemaToBeImported == tempSchemaNames[0] or schemaToBeImported == self.__remapKeys[self.__remapValues.index(tempSchemaNames[0])])):
                        print("IN SEC IMPORT ")
                        if (schemaToBeImported == self.__schemasPriority[1]["USERNAME"] or schemaToBeImported == self.__remapKeys[self.__remapValues.index(self.__schemasPriority[1]["USERNAME"])]):
                            self.__secImport(item=item, nodeValue=nodeValue, data=data, schemaToBeImported=schemaToBeImported, schemaNameAsInDB=tempSchemaNames[0], importDumpsObj=importDumpsObj, sec=True)
                            tempSchemaNames.pop(0)
                            break
                    if (2 in self.__schemasPriority.keys() and (schemaToBeImported == tempSchemaNames[0] or schemaToBeImported == self.__remapKeys[self.__remapValues.index(tempSchemaNames[0])])):
                        print("IN SHDW IMPORT ")
                        if (schemaToBeImported == self.__schemasPriority[2]["USERNAME"] or schemaToBeImported == self.__remapKeys[self.__remapValues.index(self.__schemasPriority[2]["USERNAME"])]):
                            self.__secImport(item=item, nodeValue=nodeValue, data=data, schemaToBeImported=schemaToBeImported, schemaNameAsInDB=tempSchemaNames[0], importDumpsObj=importDumpsObj, sec=False)
                            tempSchemaNames.pop(0)
                            break
                    if (schemaToBeImported == tempSchemaNames[0] or schemaToBeImported == self.__remapKeys[self.__remapValues.index(tempSchemaNames[0])]):
                        self.__appImport(item=item, nodeValue=nodeValue, data=data, schemaToBeImported=schemaToBeImported, schemaNameAsInDB=tempSchemaNames[0], importDumpsObj=importDumpsObj, lastLoop=False)
                        tempAppDumpsInfo.append({"item": item, "nodeValue": nodeValue, "data": data, "schemaToBeImported": schemaToBeImported, "schemaNameAsInDB": tempSchemaNames[0], "importDumpsObj": importDumpsObj})
                        tempSchemaNames.pop(0)
                        break
            else:
                importStatement = importDumpsObj.importDump(
                    dbIP=nodeValue["DB_IP"],
                    dbPort=nodeValue["DB_PORT"],
                    dbSID=nodeValue["DB_SID"],
                    dataPump=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["DATA_PUMP"],
                    dumpPath=os.path.split(item["DUMP_PATH"])[1],
                    content=item["CONTENT"],
                    logFile=item["LOGFILE"],
                    parFilePath=item["PAR_FILE_PATH"],
                    remapSchemas=data["DB_INFO"]["IMPORT_DUMPS_INFO"]["REMAP_SCHEMAS"],
                    schemas=[schemaToBeImported],
                    tableExistAction="APPEND",
                    user="system",
                    directory="PSDEPLOY",
                    userPass=nodeValue["SYSTEM_PASS"],
                    osUsername=nodeValue["OS_USERNAME"],
                    osPassword=nodeValue["OS_PASSWORD"],
                    version=item["VERSION"]
                )
        if (len(tempAppDumpsInfo) != 0):
            for tempAppDump in tempAppDumpsInfo:
                self.__appImport(tempAppDump["item"], tempAppDump["nodeValue"], tempAppDump["data"], tempAppDump["schemaToBeImported"], tempAppDump["schemaNameAsInDB"], tempAppDump["importDumpsObj"], True)
        for schemaTemp in self.__schemaNames:
            self.__deployConnection.compileAllInvalidObjects(schemaName=schemaTemp)

    def __parseAppsInfo(self, data: list):
        self.__mainLogger.printDebugLog("Parsing applications info!")
        self.__mainLogger.printInfoLog("Applications will be sorted based on priority!")
        for item in data:
            itemKey = [*item.keys()][0]
            self.__schemasPriority.update(item)
        self.__schemasPriority = collections.OrderedDict(sorted(self.__schemasPriority.items()))
    
    def __parseDumpsRef(self, data: dict):
        for key, value in self.__schemasPriority.items():
            for item in data["DUMPS_REF"]:
                itemKey = [*item.keys()][0]
                for schemaName in item[itemKey]["SCHEMAS"]:
                    if (schemaName in value["USERNAME"]):
                        self.__schemaNames.append(schemaName)
                        self.__dumpsToImport.append(item[itemKey])
    
    def __disableConstraintsParsing(self, user: str):
        sourceFile = os.path.join(os.path.dirname(__file__), "resources", "disableConstraints.sql")
        tempFile = os.path.join(os.path.dirname(__file__), "resources", "disableConstraintsTemp.sql")
        fIn = open(sourceFile, 'r')
        lines = fIn.readlines()
        with open(tempFile, 'w') as fOut:
            for line in lines:
                if ("_USER_" in line):
                    line = line.replace("_USER_", user)
                fOut.write(line + "\n")
        fIn.close()
    
    def __enableConstraintsParsing(self, user: str):
        sourceFile = os.path.join(os.path.dirname(__file__), "resources", "enableConstraints.sql")
        tempFile = os.path.join(os.path.dirname(__file__), "resources", "enableConstraintsTemp.sql")
        fIn = open(sourceFile, 'r')
        lines = fIn.readlines()
        with open(tempFile, 'w') as fOut:
            for line in lines:
                if ("_USER_" in line):
                    line = line.replace("_USER_", user)
                fOut.write(line + "\n")
        fIn.close()
    
    def __secGrantsToUser(self, secUser: str, appUser: str):
        sourceFile = os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrants.sql")
        tempFile = os.path.join(os.path.dirname(__file__), "resources", "unifiedSecGrantsTemp.sql")
        fIn = open(sourceFile, 'r')
        lines = fIn.readlines()
        with open(tempFile, 'w') as fOut:
            for line in lines:
                if ("_SEC_USER_CHANGE_" in line):
                    line = line.replace("_SEC_USER_CHANGE_", secUser)
                if ("_APP_USER_" in line):
                    line = line.replace("_APP_USER_", appUser)
                fOut.write(line + "\n")
        fIn.close()

    def __synonymsParsing(self, schemaName: str) -> bool:
        tableName = "DBA_SYNONYMS"
        synonymsDF: DataFrame = self.__deployConnection.executeSelectStatement(tableName=f"{tableName}", whereClause=[("OWNER", "=", f"{schemaName}")])
        currentUserNames: DataFrame = self.__deployConnection.executeSelectStatement("ALL_USERS", ["username"])
        if (not synonymsDF.empty):
            synonymsGrantsPath = os.path.join(os.path.dirname(__file__), "resources", "synonymsGrants.sql")
            updatedSynonymsPath = os.path.join(os.path.dirname(__file__), "resources", "updatedSynonyms.sql")
            if (os.path.exists(synonymsGrantsPath)):
                os.unlink(synonymsGrantsPath)
            if (os.path.exists(updatedSynonymsPath)):
                os.unlink(updatedSynonymsPath)
            fInGrants = open(synonymsGrantsPath, 'w')
            fInSynonyms = open(updatedSynonymsPath, 'w')
            for index, row in synonymsDF.iterrows():
                if (len(self.__remapKeys) != 0 and row['table_owner'] not in self.__remapKeys):
                    if (row['table_owner'] != None and row['table_owner'] in currentUserNames["username"].to_list()):
                        self.__deployConnection.dropSynonym(schemaName=schemaName, synonymnName=row['synonym_name'])
                        fInSynonyms.write(f"CREATE OR REPLACE SYNONYM {schemaName}.{row['synonym_name']} FOR {row['table_owner']}.{row['table_name']};\n")
                        fInGrants.write(f"GRANT ALL ON {row['table_owner']}.{row['table_name']} TO {schemaName};\n")
                    else:
                        # fInSynonyms.write(f"CREATE OR REPLACE SYNONYM {schemaName}.{row['synonym_name']} FOR {row['table_name']};\n")
                        # fInGrants.write(f"GRANT ALL ON {row['table_name']} TO {schemaName};\n")
                        pass
                elif (len(self.__remapKeys) != 0):
                    if (row['table_owner'] != None and row['table_owner'] in currentUserNames["username"].to_list()):
                        self.__deployConnection.dropSynonym(schemaName=schemaName, synonymnName=row['synonym_name'])
                        fInSynonyms.write(f"CREATE OR REPLACE SYNONYM {schemaName}.{row['synonym_name']} FOR {self.__remapValues[self.__remapKeys.index(row['table_owner'])]}.{row['TABLE_NAME']};\n")
                        fInGrants.write(f"GRANT ALL ON {self.__remapValues[self.__remapKeys.index(row['table_owner'])]}.{row['table_name']} TO {schemaName};\n")
                    else:
                        # fInSynonyms.write(f"CREATE OR REPLACE SYNONYM {schemaName}.{row['synonym_name']} FOR {row['table_name']};\n")
                        # fInGrants.write(f"GRANT ALL ON {row['table_name']} TO {schemaName};\n")
                        pass
                else:
                    if (row['table_owner'] != None and row['table_owner'] in currentUserNames["username"].to_list()):
                        self.__deployConnection.dropSynonym(schemaName=schemaName, synonymnName=row['synonym_name'])
                        fInSynonyms.write(f"CREATE OR REPLACE SYNONYM {schemaName}.{row['synonym_name']} FOR {row['table_owner']}.{row['table_name']};\n")
                        fInGrants.write(f"GRANT ALL ON {row['table_owner']}.{row['table_name']} TO {schemaName};\n")
                    else:
                        # fInSynonyms.write(f"CREATE OR REPLACE SYNONYM {schemaName}.{row['synonym_name']} FOR {row['table_name']};\n")
                        # fInGrants.write(f"GRANT ALL ON {row['table_name']} TO {schemaName};\n")
                        pass
            return True
        else:
            return False
    
    def __createSecUsers(self, schemaName: str):
        adminFilePath = os.path.join(os.path.dirname(__file__), "resources", "adminUser.sql")
        systemFilePath = os.path.join(os.path.dirname(__file__), "resources", "systemUser.sql")
        rootFilePath = os.path.join(os.path.dirname(__file__), "resources", "rootUser.sql")
        adminFile = open(adminFilePath, 'r')
        adminFileLines = adminFile.readlines()
        with open(os.path.join(os.path.dirname(__file__), "resources", "adminUserTemp.sql"), 'w') as adminFileTemp:
            for line in adminFileLines:
                if ("__USER__TO_CHANGE__" in line):
                    line = line.replace("__USER__TO_CHANGE__", schemaName)
                adminFileTemp.write(line)
        systemFile = open(systemFilePath, 'r')
        systemFileLines = systemFile.readlines()
        with open(os.path.join(os.path.dirname(__file__), "resources", "systemUserTemp.sql"), 'w') as systemFileTemp:
            for line in systemFileLines:
                if ("__USER__TO_CHANGE__" in line):
                    line = line.replace("__USER__TO_CHANGE__", schemaName)
                systemFileTemp.write(line)
        rootFile = open(rootFilePath, 'r')
        rootFileLines = rootFile.readlines()
        with open(os.path.join(os.path.dirname(__file__), "resources", "rootUserTemp.sql"), 'w') as rootFileTemp:
            for line in rootFileLines:
                if ("__USER__TO_CHANGE__" in line):
                    line = line.replace("__USER__TO_CHANGE__", schemaName)
                rootFileTemp.write(line)
        adminFile.close()
        rootFile.close()
        systemFile.close()

    def updateSecAppInstances(self, schemaName: str, nodeIP: str, port: int, moduleType: int, appName: str):
        self.__deployConnection.executeUpdateStatement(schemaName, "SEC_APP_INSTANCES", ["APPINST_INST_URL"], [f"\'http://{nodeIP}:{port}/{appName}/\'"], [("APP_ID", "=", moduleType)])