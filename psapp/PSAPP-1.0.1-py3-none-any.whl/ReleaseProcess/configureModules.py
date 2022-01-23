import os
import sys
from typing import Any
import zipfile
import re
import shutil
import socket
from lxml import etree
import xml.etree.ElementTree as ET
from PSAPP.DB.dbConnection import DBConnection
from PSAPP.Logging.loggingModule import Logging
from sqlalchemy import text
from PSAPP.appsReader import AppsReader
from PSAPP.DB.sshConnection import SSHConnection

class ModulesBaker:

    APP_MODULE: str = ''
    SEC_MODULE: str = ''
    INT_MODULE: str = ''
    APP_MODULES: dict = {}
    SEC_MODULES: dict = {}
    INT_MODULES: dict = {}
    COMM_SERVICES: dict = {}
    SEC_APP_INSTANCES: dict = {}

    def __init__(self, deployConnection: DBConnection = None, mainLogger: Logging = None, nodeIP: str = None, nodeOSUsername: str = None, nodeOSPassword: str = None) -> None:
        self.__newReleasePath: str = ''
        self.__mainLogger: Logging = mainLogger
        self.__secModulesMapping = AppsReader.secModulesMapping
        self.__appModulesMapping = AppsReader.appModulesMapping
        self.__intModulesMapping = AppsReader.intModulesMapping
        self.__DBURL: str = ''
        self.__deployConnection: DBConnection = deployConnection
        # self.__nodeIP: str = nodeIP
        # self.__osUsername = nodeOSUsername
        # self.__osPassword = nodeOSPassword
        # self.__sshConnection: SSHConnection = None

    @staticmethod
    def modulesChecker(unpackedReleasePath: str) -> None:
        for dir in os.listdir(unpackedReleasePath):
            dirPath = os.path.join(unpackedReleasePath, dir)
            if (not (zipfile.is_zipfile(dirPath) or dir == "DATABASE" or dir == "README.md")):
                for sub in os.listdir(dirPath):
                    if ("ActiveX" in sub):
                        ModulesBaker.APP_MODULE = dirPath
                    elif ("ServiceEditor.jsp" in sub):
                        ModulesBaker.INT_MODULE = dirPath
                    elif ("UsersList" in sub):
                        ModulesBaker.SEC_MODULE = dirPath
                    elif ("SVC-ECC" in sub):
                        ModulesBaker.COMM_SERVICES = dirPath
        return [ModulesBaker.APP_MODULE, ModulesBaker.INT_MODULE, ModulesBaker.SEC_MODULE, ModulesBaker.COMM_SERVICES]
    
    def __copyToLocal(self, tomcatPath: str, moduleTypeMapping: str, moduleType: int):
        appPath = os.path.join(tomcatPath, "webapps", moduleTypeMapping)
        self.__mainLogger.printDebugLog(f"Start with copy module {moduleType} to {appPath}.")
        if (moduleType in list(self.__appModulesMapping.keys())):
            if (os.path.exists(appPath)):
                shutil.rmtree(appPath)
            shutil.copytree(src=ModulesBaker.APP_MODULE, dst=appPath)
            self.__mainLogger.printDebugLog(f"Copy {moduleType} done successfully!")
            ModulesBaker.APP_MODULES.update({moduleType: appPath})
            self.__mainLogger.printInfoLog(f"You can find module {moduleType} in {appPath}!")
        elif (moduleType in list(self.__secModulesMapping.keys())):
            if (os.path.exists(appPath)):
                shutil.rmtree(appPath)
            shutil.copytree(src=ModulesBaker.SEC_MODULE, dst=appPath)
            self.__mainLogger.printDebugLog(f"Copy {moduleType} done successfully!")
            ModulesBaker.SEC_MODULES.update({moduleType: appPath})
            self.__mainLogger.printInfoLog(f"You can find module {moduleType} in {appPath}!")
        elif (moduleType in list(self.__secModulesMapping.keys())):
            if (os.path.exists(appPath)):
                shutil.rmtree(appPath)
            shutil.copytree(src=ModulesBaker.INT_MODULE, dst=appPath)
            self.__mainLogger.printDebugLog(f"Copy {moduleType} done successfully!")
            ModulesBaker.INT_MODULES.update({moduleType: appPath})
            self.__mainLogger.printInfoLog(f"You can find module {moduleType} in {appPath}!")
    
    # def __copySSH(self, tomcatPath: str, moduleTypeMapping: str, moduleType: int):
    #     self.__sshConnection.transferFile()
    
    def moduleMimic(self, modulesType: int, tomcatPath: str) -> dict:
        self.__mainLogger.printDebugLog("Start with creating modules and duplicate modules based on ID!")
        self.__mainLogger.printDebugLog("Getting local IP!")
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(("8.8.8.8", 80))
        # localIP = s.getsockname()[0]
        # self.__mainLogger.printInfoLog(f"Your local IP is {localIP}")
        # self.__sshConnection = SSHConnection(self.__nodeIP, self.__osUsername, self.__osPassword)
        if (modulesType in list(self.__appModulesMapping.keys())):
            # if (localIP == nodeIP):
            self.__copyToLocal(tomcatPath=tomcatPath, moduleTypeMapping=self.__appModulesMapping[modulesType], moduleType=modulesType)
        elif (modulesType in list(self.__secModulesMapping.keys())):
            # if (localIP == nodeIP):
            self.__copyToLocal(tomcatPath=tomcatPath, moduleTypeMapping=self.__secModulesMapping[modulesType], moduleType=modulesType)
        elif (modulesType in list(self.__intModulesMapping.keys())):
            # if (localIP == nodeIP):
            self.__copyToLocal(tomcatPath=tomcatPath, moduleTypeMapping=self.__intModulesMapping[modulesType], moduleType=modulesType)
        # self.updateSecAppInstance(modulesType, f"http://{localIP}:{connectorPort}/{self.__appModulesMapping[modulesType]}/", secUser=secUser, shdwUser=shdwUser)

    def copyToTomcat(self, tomcatPath: str):
        pass

    def configureDBConnection(self, data: dict, moduleType: int) -> bool:
        self.__mainLogger.printDebugLog(f"Start with configuring DB connection for module {moduleType}!")
        nodeInfo: dict = data["DB_INFO"]["DB_NODES"][0]
        self.__DBURL = "jdbc:oracle:thin:@" + str(nodeInfo[1]["DB_IP"]) + ":" + str(nodeInfo[1]["DB_PORT"]) + "/" + str(nodeInfo[1]["DB_SID"])
        self.__mainLogger.printInfoLog(f"DB URL: {self.__DBURL}.")
        pass
        if (moduleType in list(self.__appModulesMapping.keys())):
            self.__appDBConnection(data=data, moduleType=moduleType)
        elif (moduleType in list(self.__secModulesMapping.keys())):
            self.__secDBConnection(data=data, moduleType=moduleType)
        elif (moduleType in list(self.__intModulesMapping.keys())):
            self.__intDBConnection(data=data, moduleType=moduleType)

    def __appDBConnection(self, data: dict, moduleType: int) -> None:
        self.__mainLogger.printDebugLog(f"Start reading context.xml file for module {self.__appModulesMapping[moduleType]}")
        contextFilePath: str = os.path.join(ModulesBaker.APP_MODULES[moduleType], "META-INF", "context.xml")
        parsedXML = ET.parse(contextFilePath)
        root = parsedXML.getroot()
        self.__mainLogger.printInfoLog(f"context.xml file: {contextFilePath}")
        self.__mainLogger.printDebugLog("Start parsing xml!")
        for child in root:
            if (child.get("name") == "jdbc/ECC"):
                moduleSchemaInfo = [item[moduleType] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if moduleType in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)
            elif (child.get("name") == "jdbc/PSSEC"):
                moduleSchemaInfo = [item[1] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if 1 in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)
            elif (child.get("name") == "jdbc/PSSHDW"):
                moduleSchemaInfo = [item[2] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if 2 in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)

    def __secDBConnection(self, data: dict, moduleType: int) -> None:
        self.__mainLogger.printDebugLog(f"Start reading context.xml file for module {self.__secModulesMapping[moduleType]}")
        contextFilePath: str = os.path.join(ModulesBaker.SEC_MODULES[moduleType], "META-INF", "context.xml")
        self.__mainLogger.printInfoLog(f"context.xml file: {contextFilePath}")
        self.__mainLogger.printDebugLog("Start parsing xml!")
        parsedXML = ET.parse(contextFilePath)
        root = parsedXML.getroot()
        for child in root:
            if (child.get("name") == "jdbc/PSSHDW"):
                moduleSchemaInfo = [item[2] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if 2 in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)
                self.__mainLogger.printDebugLog(f"Username, password and DB URL updated successfully for {self.__secModulesMapping[moduleType]}")

    def __intDBConnection(self, data: dict, moduleType: int) -> None:
        self.__mainLogger.printDebugLog(f"Start reading context.xml file for module {self.__intModulesMapping[moduleType]}")
        contextFilePath: str = os.path.join(ModulesBaker.APP_MODULES[moduleType], "META-INF", "context.xml")
        parsedXML = ET.parse(contextFilePath)
        root = parsedXML.getroot()
        self.__mainLogger.printInfoLog(f"context.xml file: {contextFilePath}")
        self.__mainLogger.printDebugLog("Start parsing xml!")
        for child in root:
            if (child.get("name") == "jdbc/ECC"):
                moduleSchemaInfo = [item[moduleType] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if moduleType in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)
                self.__mainLogger.printDebugLog(f"Username, password and DB URL updated successfully for {self.__intModulesMapping[moduleType]}")
            elif (child.get("name") == "jdbc/PSSEC"):
                moduleSchemaInfo = [item[2] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if 2 in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)
                self.__mainLogger.printDebugLog(f"Username, password and DB URL updated successfully for {self.__intModulesMapping[moduleType]}")
            elif (child.get("name") == "jdbc/PSSHDW"):
                moduleSchemaInfo = [item[2] for item in data["DB_INFO"]["APPS_SCHEMAS_INFO"] if 2 in item][0]
                self.__updateUPU(moduleSchemaInfo, child)
                try:
                    parsedXML.write(contextFilePath)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing the parsed xml: {error}!")
                    sys.exit(1)
                self.__mainLogger.printDebugLog(f"Username, password and DB URL updated successfully for {self.__intModulesMapping[moduleType]}")

    def __updateUPU(self, moduleSchemaInfo: Any, child: ET.Element) -> None:
        self.__mainLogger.printDebugLog(f"Updating the username, password and connection for {moduleSchemaInfo['USERNAME']}")
        child.set("username", moduleSchemaInfo["USERNAME"])
        child.set("password", moduleSchemaInfo["PASSWORD"])
        child.set("url", self.__DBURL)

    def configureIntUrl(self, data: dict, moduleType: int) -> None:
        self.__mainLogger.printDebugLog(f"Configuring INT URL for {self.__appModulesMapping[moduleType]}")
        intTagFile = os.path.join(ModulesBaker.APP_MODULES[moduleType], "WEB-INF", "tags", "IntConfiguration.tag")
        self.__mainLogger.printInfoLog(f"INT tag file: {intTagFile}.")
        intURL = data["INT_INFO"]["INT_IP_OR_HOST"]
        self.__mainLogger.printInfoLog(f"INT URL: {intURL}")
        intPort = data["INT_INFO"]["INT_PORT"]
        self.__mainLogger.printInfoLog(f"INT Port: {intPort}")
        with open(intTagFile, "r+") as file:
            fileLines = file.readlines()
            file.seek(0)
            file.truncate()
            for lineNumber, line in enumerate(fileLines, 1):
                intLine = re.search(r".*var\s*=\s*(?:\'|\")integrationPath(?:\'|\").*value\s*=\s*(?:\'|\").*(?:\'|\").*", line)
                try:
                    if (intLine != None):
                        self.__mainLogger.printDebugLog(f"INT line before update: {intLine}")
                        intLine = re.sub(r"value\s*=\s*(?:\'|\").*(?:\'|\")", f"value=\"http://{intURL}:{intPort}/{self.__intModulesMapping[moduleType + 0.1]}\"", intLine.group()) + "\n"
                        self.__mainLogger.printDebugLog(f"INT line after update: {intLine}")
                        file.write(intLine)
                    else:
                        file.write(line)
                except Exception as error:
                    self.__mainLogger.printErrorLog(f"An error occured while writing updating and writing INT URL: {error}")
    
    def configureSecWebXMLFile(self, data: dict, moduleType: int):
        webXMLFile = os.path.join(ModulesBaker.SEC_MODULES[moduleType], "WEB-INF", "web.xml")
        parsedXML = ET.parse(webXMLFile)
        root = parsedXML.getroot()
        ET.register_namespace('', etree.QName(root.tag).namespace)
        # print(etree.QName(root.tag).namespace)
        for element in root:
            if (etree.QName(element.tag).localname == "env-entry"):
                found = False
                for subElement in element:
                    if (not found):
                        if ((etree.QName(subElement.tag).localname ==  "env-entry-name") and ("ApplicationId") in subElement.text):
                            found = True
                    else:
                        if (etree.QName(subElement.tag).localname == "env-entry-value"):
                            subElement.text = str(moduleType)
                parsedXML.write(webXMLFile)
    
    def configureIntWebXMLFile(self, data: dict, moduleType: int):
        webXMLFile = os.path.join(ModulesBaker.INT_MODULES[moduleType], "WEB-INF", "web.xml")
        parsedXML = ET.parse(webXMLFile)
        if (moduleType == 10):
            pass

    def updateSecAppInstance(self, appID: int, url: str, secUser: str, shdwUser: str):
        self.__mainLogger.printDebugLog(f"Updating the app instance in security and shadow modules!")
        self.__deployConnection.executeStatement(text(f"UPDATE {secUser}.SEC_APP_INSTANCES SET APPINST_INST_URL='{url}' WHERE APP_ID={appID}"))
        self.__deployConnection.executeStatement(text(f"UPDATE {shdwUser}.SEC_APP_INSTANCES SET APPINST_INST_URL='{url}' WHERE APP_ID={appID}"))
        self.__mainLogger.printDebugLog(f"Done updating the app ID {appID} in SEC_APP_INSTANCES table!")
        self.__mainLogger.printInfoLog(f"App with app ID {appID} will be accessible using this URL: {url} !")