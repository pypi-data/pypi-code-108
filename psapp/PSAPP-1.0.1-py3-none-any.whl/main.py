import getopt
import re
import sys
import os
import platform
import click
from click.decorators import option
from cryptography.fernet import Fernet
import yaml
import copy
from getpass import getpass
from typing import Any, Tuple, Union
from PSAPP.Validation.configParser import ConfigParser
from PSAPP.ReleaseProcess.eccReleaseBaker import ECCReleaseBaker
from PSAPP.Logging.loggingModule import Logging
from PSAPP.ReleaseProcess.configureModules import ModulesBaker
from PSAPP.ReleaseProcess.configureTomcat import TomcatBaker
from PSAPP.DB.dbBaker import DBBaker
from PSAPP.DB.dbConnection import DBConnection
from PSAPP.dataEncryption import DataEncryption
from PSAPP.appsReader import AppsReader
# import data


ENCRYPTION_KEY = None

@click.group()
def main() -> tuple:
    # click.echo(clean)
    pass

@main.command()
def help(clean) -> None:
    '''Printing a tool documentation and help!'''
    click.echo(clean)
    print("Hello from print doc!")
    pass

@main.command()
@click.option('-c', '--clean', is_flag=True)
@click.option('-e', '--edit', is_flag=True)
def run(clean, edit):
    if (edit):
        editConfigs(edit)
    readApplicationsDetails()
    result: Union[dict, Tuple[str, bool]] = ConfigParser.validateConfigs(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ecc-configs.yaml"))        
    if (clean):
        result = askForSensInfo(result)
    else:
        result = readEncryptedDataAndUpdate(result=result)
    if (isinstance(result, dict)):
        logPath = os.path.dirname(result["APP_INFO"]["RELEASE_PATH"])
        mainLogger = Logging("MainLog.log", logPath)
        deployConnection: DBConnection = None
        if (result["DB_INFO"]["DB_DEPLOY"] == True):
            dbBaker = DBBaker(mainLogger=mainLogger)
            deployConnection = dbBaker.deployDB(result)
        if (result["APP_INFO"]["APP_DEPLOY"] == True):
            mainLogger.printInfoLog("Start deploying ECC Apps!")
            eccReleaseBaker = ECCReleaseBaker(mainLogger=mainLogger)
            newReleasePath: str = eccReleaseBaker.deployApps(result)
            mainLogger.printDebugLog("Start checking the Applications and decide application type!")
            appsTypes: list = ModulesBaker.modulesChecker(newReleasePath)
            modules = result["APP_INFO"]["MODULES"]
            mainLogger.printInfoLog(f"Applications after checking the type: {[*appsTypes]}")
            tomcatRefs: dict
            for node in result["APP_INFO"]["APP_NODES"]:
                nodeValue = [*node.values()][0]
                if (result["TOMCAT_INFO"]["DEPLOY_TOMCAT"]):
                    tomcatBaker = TomcatBaker(mainLogger, nodeIP=nodeValue["NODE_IP"], nodeOSUsername=nodeValue["OS_USERNAME"], nodeOSPassword=nodeValue["OS_PASSWORD"])
                    tomcatBaker.prepareTomcat(result)
                    for tomcatRef in result["TOMCAT_INFO"]["TOMCAT_REFERENCE"]:
                        tomcatSourcePathUpdated = tomcatBaker.configureTomcatPorts(tomcatRef=tomcatRef)
                        tomcatRefKey = [*tomcatRef.keys()][0]
                        tomcatRefValue = [*tomcatRef.values()][0]
                        tomcatBaker.cleanWebApps()
                        for module in modules:
                            moduleObject = ModulesBaker(deployConnection, mainLogger=mainLogger, nodeIP=nodeValue["NODE_IP"], nodeOSUsername=nodeValue["OS_USERNAME"], nodeOSPassword=nodeValue["OS_PASSWORD"])
                            moduleType = [*module.keys()][0]
                            moduleValues = [*module.values()][0]
                            if (moduleValues["TOMCAT_REFERENCE"] == tomcatRefKey):
                                moduleObject.moduleMimic(modulesType=moduleType, tomcatPath=tomcatSourcePathUpdated)
                                moduleObject.configureDBConnection(result, moduleType)
                                if (moduleType in list(AppsReader.appModulesMapping.keys())):
                                    moduleObject.configureIntUrl(result, moduleType)
                                elif (moduleType in list(AppsReader.secModulesMapping.keys())):
                                    moduleObject.configureSecWebXMLFile(result, moduleType)
                        tomcatUpdatedPath = tomcatBaker.createTomcatCopies(result["TOMCAT_INFO"], tomcatRefKey, tomcatRefValue)
                        tomcatBaker.runTomcats(tomcatUpdatedPath, result["TOMCAT_INFO"]["JAVA_HOME"])
    elif (isinstance(result, tuple)):
        print(f"Please recheck the configurations!\n{result[1]}")

@main.command()
def db_deploy():
    result: Union[dict, Tuple[str, bool]] = ConfigParser.validateConfigs(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ecc-configs.yaml"))
    if (result["DB_INFO"]["DB_DEPLOY"] == True):
            dbBaker = DBBaker()
            dbBaker.deployDB(result)

@main.command()
def import_dumps():
    result: Union[dict, Tuple[str, bool]] = ConfigParser.validateConfigs(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ecc-configs.yaml"))

@main.command()
def configs_edit():
    editConfigs()

@main.command()
def add_app():
    fOut = open("applications-details.yaml", 'r')
    dataRead = yaml.safe_load(fOut.read())
    print("*************************************************\n")
    print("Please find the current defined applications:\n")
    pretty(dataRead)
    print("*************************************************\n")
    print("Please to add the below details:")
    typeOfApplication = input("Application Type \nSEC => 1\nECC MODULE => 2\nType: ")
    if (typeOfApplication not in ['1', '2']):
        isCorrect = True
        while(isCorrect):
            hasInt = input("The value shoud be either [SEC => 1, ECC MODULE => 2]? ").lower()
            if (hasInt not in ['1', '2']):
                isCorrect = True
            else:
                isCorrect = False
    appID = input("Please enter the app ID: ")
    appID = int(appID)
    appLabel = input("Please enter the application label name: ")
    hasInt = None
    if (typeOfApplication == "2" or typeOfApplication == 2):
        hasInt = input("Does the application has integration with core banking? [y,n]: ").lower()
        if (hasInt not in ['y', 'n']):
            isChar = True
            while(isChar):
                hasInt = input("The value shoud be either [y,n]? ").lower()
                if (hasInt not in ['y', 'n']):
                    isChar = True
                else:
                    isChar = False
    if (typeOfApplication == '1'):
        for item in dataRead["SEC"]:
            if (appID == [*item.keys()][0]):
                dataRead["SEC"].remove(item)
        dataRead["SEC"].append({appID: {"LABEL": appLabel}})
    elif (typeOfApplication == '2' and hasInt == 'y'):
        for item in dataRead["ECC"]:
            if (appID == [*item.keys()][0]):
                dataRead["ECC"].remove(item)
        for item in dataRead["INT"]:
            if (appID + 0.1 == [*item.keys()][0]):
                dataRead["INT"].remove(item)
        dataRead["ECC"].append({appID: {"LABEL": appLabel}})
        dataRead["INT"].append({appID + 0.1: {"LABEL": "INT" + appLabel}})
    else:
        for item in dataRead["ECC"]:
            if (appID == [*item.keys()][0]):
                dataRead["ECC"].remove(item)
        dataRead["ECC"].append({appID: {"LABEL": appLabel}})
    fIn = open("applications-details.yaml", 'w')
    fIn.write(yaml.safe_dump(dataRead))
    fOut.close()
    fIn.close()

def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            print(value)
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))

def editConfigs(edit = None):
    print("*************************************************\n")
    print(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ecc-configs.yaml"))
    print("\n*************************************************")
    print("Please to edit it and re-run without edit option!")
    print("*************************************************")
    sys.exit(1)

def askForSensInfo(result: dict):
    ENCRYPTION_KEY = DataEncryption(storeNew=True)
    tempResult = copy.deepcopy(result)
    secretFileWrite = open(os.path.join(os.path.dirname(__file__), "secretFile.txt"), 'wb')
    secretFileLine = ''.encode()
    secretFileLine += "{".encode()
    firstFlag = True
    for node in result["APP_INFO"]["APP_NODES"]:
        nodeKey = list(node.keys())[0]
        nodeValue = list(node.values())[0]
        osUsername = getpass(f"Please enter OS username for APP node {nodeValue['NODE_IP']}: ")
        if (osUsername == '' or osUsername == None):
            pass
        else:
            osUsernameEncrypted = ENCRYPTION_KEY.encryptData(osUsername)
            if (firstFlag):
                secretFileLine += (f"\"PSTOOL_APP_OS_USERNAME_{str(nodeKey)}\":{osUsernameEncrypted}".encode())
                firstFlag = False
            else:
                secretFileLine += (f", \"PSTOOL_APP_OS_USERNAME_{str(nodeKey)}\":{osUsernameEncrypted}".encode())
            osPassword = getpass(f"Please enter OS password for APP node {nodeValue['NODE_IP']}: ")
            osPassEncrypted = ENCRYPTION_KEY.encryptData(osPassword)
            secretFileLine += (f", \"PSTOOL_APP_OS_PASSWORD_{str(nodeKey)}\":{osPassEncrypted}".encode())

    for node in result["DB_INFO"]["DB_NODES"]:
        nodeKey = list(node.keys())[0]
        nodeValue = list(node.values())[0]
        sysPass = getpass(f"Please enter SYS password for node {nodeValue['DB_IP']}: ")
        if (sysPass == None or sysPass == ''):
            pass
        else:
            sysPassEncrypted = ENCRYPTION_KEY.encryptData(sysPass)
            if (firstFlag):
                secretFileLine += (f"\"PSTOOL_SYS_PASS_{str(nodeKey)}\":{sysPassEncrypted}".encode())
                firstFlag = False
            else:
                secretFileLine += (f", \"PSTOOL_SYS_PASS_{str(nodeKey)}\":{sysPassEncrypted}".encode())
            systemPass = getpass(f"Please enter SYSTEM password for node {nodeValue['DB_IP']}: ")
            systemPassEncrypted = ENCRYPTION_KEY.encryptData(systemPass)
            secretFileLine += (f", \"PSTOOL_SYSTEM_PASS_{str(nodeKey)}\":{systemPassEncrypted}".encode())
            osUsername = getpass(f"Please enter OS username for DB node {nodeValue['DB_IP']}: ")
            osUsernameEncrypted = ENCRYPTION_KEY.encryptData(osUsername)
            secretFileLine += (f", \"PSTOOL_DB_OS_USERNAME_{str(nodeKey)}\":{osUsernameEncrypted}".encode())
            osPassword = getpass(f"Please enter OS password for DB node {nodeValue['DB_IP']}: ")
            osPasswordEncrypted = ENCRYPTION_KEY.encryptData(osPassword)
            secretFileLine += (f", \"PSTOOL_DB_OS_PASSWORD_{str(nodeKey)}\":{osPasswordEncrypted}".encode())
    
    for user in result["DB_INFO"]["APPS_SCHEMAS_INFO"]:
        userKey = list(user.keys())[0]
        userValue = list(user.values())[0]
        userPassword = getpass(f"Please enter {userValue['USERNAME']} password: ")
        userPasswordEncrypted = ENCRYPTION_KEY.encryptData(userPassword)
        if (firstFlag):
            secretFileLine += (f"\"PSTOOL_SCHEMA_{str(userValue['USERNAME'])}\":{userPasswordEncrypted}".encode())
            firstFlag = False
        else:
            secretFileLine += (f", \"PSTOOL_SCHEMA_{str(userValue['USERNAME'])}\":{userPasswordEncrypted}".encode())
    secretFileLine += ("}".encode())
    secretFileWrite.write(ENCRYPTION_KEY.encryptData(secretFileLine.decode()))
    secretFileWrite.close()
    return readEncryptedDataAndUpdate(result)

def readEncryptedDataAndUpdate(result: dict) -> dict:
    ENCRYPTION_KEY = DataEncryption(storeNew=False)
    if ("secretFile.txt" not in os.listdir(os.path.dirname(os.path.realpath(__file__)))):
        askForSensInfo(result)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "secretFile.txt"), 'rb') as file:
        line = file.readline()
        if (line != b''):
            encryptedData = eval((ENCRYPTION_KEY.decryptData(line)).decode())
        else:
            askForSensInfo(result=result)
        for key, value in encryptedData.items():
            if ("PSTOOL_APP_OS_USERNAME" in key):
                updateTheSensDataOnConfigNodes(result["APP_INFO"]["APP_NODES"], key, value, "OS_USERNAME")
            elif ("PSTOOL_APP_OS_PASSWORD" in key):
                updateTheSensDataOnConfigNodes(result["APP_INFO"]["APP_NODES"], key, value, "OS_PASSWORD")
            elif ("PSTOOL_SYS_PASS" in key):
                updateTheSensDataOnConfigNodes(result["DB_INFO"]["DB_NODES"], key, value, "SYS_PASS")
            elif ("PSTOOL_SYSTEM_PASS" in key):
                updateTheSensDataOnConfigNodes(result["DB_INFO"]["DB_NODES"], key, value, "SYSTEM_PASS")
            elif ("PSTOOL_DB_OS_USERNAME" in key):
                updateTheSensDataOnConfigNodes(result["DB_INFO"]["DB_NODES"], key, value, "OS_USERNAME")
            elif ("PSTOOL_DB_OS_PASSWORD" in key):
                updateTheSensDataOnConfigNodes(result["DB_INFO"]["DB_NODES"], key, value, "OS_PASSWORD")
            elif ("PSTOOL_SCHEMA" in key):
                updateTheSensDataOnConfigUsers(result["DB_INFO"]["APPS_SCHEMAS_INFO"], key, value, "PASSWORD")
        return result

def updateTheSensDataOnConfigNodes(result: dict, key: str, value: str, keyToUpdate: str):
    ENCRYPTION_KEY = DataEncryption(storeNew=False)
    nodeID = key[-1]
    item = next(item for item in result if [*item.keys()][0] == int(nodeID))
    itemIndex = (result).index(item)
    itemKeys = [*item.keys()][0]
    itemValues = [*item.values()][0]
    itemValues.update({keyToUpdate: ENCRYPTION_KEY.decryptData(value).decode()})
    item.update({itemKeys: itemValues})
    (result[itemIndex]).update(item)

def updateTheSensDataOnConfigUsers(result: dict, key: str, value: str, keyToUpdate: str):
    ENCRYPTION_KEY = DataEncryption(storeNew=False)
    usernameKey = key[14:]
    item = next((item for item in result if [*item.values()][0]['USERNAME'] == usernameKey), None)
    if (item != None):
        itemIndex = (result).index(item)
        itemKeys = [*item.keys()][0]
        itemValues = [*item.values()][0]
        itemValues.update({keyToUpdate: ENCRYPTION_KEY.decryptData(value).decode()})
        item.update({itemKeys: itemValues})
        (result[itemIndex]).update(item)

def readApplicationsDetails():
    applicationsDetails = AppsReader.readApplications()
    AppsReader.parseApplicationsDetails(applicationsDetails=applicationsDetails)

if __name__ == "__main__":
    main()