import sys
import struct
import subprocess
import glob
import os,requests,zipfile,shutil
from typing import Any
import xml.etree.ElementTree as ET
from PSAPP.Logging.loggingModule import Logging
from requests.exceptions import HTTPError, ConnectTimeout, InvalidURL
from PSAPP.ReleaseProcess.treeBuilder import MyTreeBuilder
from PSAPP.DB.sshConnection import SSHConnection

class TomcatBaker:

    def __init__(self, mainLogger: Logging = None, nodeIP: str = None, nodeOSUsername: str = None, nodeOSPassword: str = None) -> None:
        self.__tomcatSourcePath: str = ''
        self.__tomcatVersion: int = -1
        self.__downloadTomcat: bool = False
        self.__tomcatDirName: str = ''
        self.__tomcatRefs: dict = {}
        self.__backupDir: str = ''
        self.__mainLogger = mainLogger
        self.__sshConnection: SSHConnection = None
        self.__nodeIP: str = nodeIP
        self.__osUsername = nodeOSUsername
        self.__osPassword = nodeOSPassword

    def prepareTomcat(self, data: dict) -> dict:
        self.__tomcatSourcePath = data["TOMCAT_INFO"]["TOMCAT_SOURCE_PATH"]
        if os.path.exists(self.__tomcatSourcePath):
            self.__mainLogger.printDebugLog(f'{self.__tomcatSourcePath} Found!')
        else:
            os.makedirs(self.__tomcatSourcePath,exist_ok=True)
        self.__downloadTomcat = data['TOMCAT_INFO']['DOWNLOAD_TOMCAT']
        if (self.__downloadTomcat == True):
            self.__tomcatVersion = data['TOMCAT_INFO']['TOMCAT_VERSION']
            self.__backupDir = self.__tomcatSourcePath
            self.__backupDir = os.path.join(self.__backupDir,'BACKUPS')
            self.downloadTomcat()
            self.extractTomcat(self.__tomcatSourcePath, os.path.dirname(self.__tomcatSourcePath))
            # self.createTomcatCopies(data["TOMCAT_INFO"])
            # self.configureTomcatPorts(data['TOMCAT_INFO'])
        else:
            if (zipfile.is_zipfile(self.__tomcatSourcePath)):
                self.__tomcatDirName = os.path.basename(self.__tomcatSourcePath)
                self.extractTomcat(self.__tomcatSourcePath, os.path.dirname(self.__tomcatSourcePath))
            else:
                self.__tomcatDirName = os.path.basename(self.__tomcatSourcePath)
            self.__backupDir = os.path.join(os.path.dirname(self.__tomcatSourcePath), "BACKUP")
        # self.createTomcatCopies(data["TOMCAT_INFO"])
        # self.configureTomcatPorts(data["TOMCAT_INFO"])
        # return self.__tomcatRefs

    def downloadTomcat(self) -> None:
        try:
            self.__mainLogger.printInfoLog('Preparing Tomcat Download...')
            baseVersion = self.__tomcatVersion.split('.')[0]
            self.__mainLogger.printInfoLog("Tomcat base version: " + str(baseVersion))
            url: str = ''
            self.__mainLogger.printInfoLog("Checking OS type to download proper tomcat!")
            if (sys.platform == "linux"):
                self.__mainLogger.printInfoLog('Will Be Using Tomcat For Linux')
                url = f'https://archive.apache.org/dist/tomcat/tomcat-{baseVersion}/v{self.__tomcatVersion}/bin/apache-tomcat-{self.__tomcatVersion}.zip'
            elif (sys.platform == "win32"):
                self.__mainLogger.printInfoLog('Will Be Using Tomcat For Windows')
                windowsStructure = struct.calcsize("P") * 8
                self.__mainLogger.printDebugLog("OS architecture: " + str(windowsStructure))
                url = f'https://archive.apache.org/dist/tomcat/tomcat-{baseVersion}/v{self.__tomcatVersion}/bin/apache-tomcat-{self.__tomcatVersion}-windows-x{windowsStructure}.zip'
            self.__tomcatDirName = url.split('/')[-1]
            self.__mainLogger.printInfoLog(f'{self.__tomcatDirName}, Will be downloaded!')
            self.__tomcatSourcePath = os.path.join(self.__tomcatSourcePath, self.__tomcatDirName)
            self.__mainLogger.printDebugLog('Validating ' + self.__tomcatDirName + ' Download Links...')            
            if requests.head(url).status_code == 200:
                self.__mainLogger.printInfoLog('Tomcat download link is valid')
                if not os.path.exists(self.__tomcatSourcePath):
                    self.__mainLogger.printDebugLog(f'Downloading {self.__tomcatDirName}')
                    tomcatRelease = requests.get(url, timeout=3)
                    with open (self.__tomcatSourcePath, 'wb') as tomcat:
                        tomcat.write(tomcatRelease.content)
                    self.__mainLogger.printDebugLog(f'Downloaded. {self.__tomcatDirName}.')
            else:
                self.__mainLogger.printErrorLog('An Error Occured While Downloading Tomcat!')
                self.__mainLogger.printErrorLog('Please Check The Internet Connectivity And Try Again.\n')
                sys.exit(1)
        except requests.HTTPError as httperr:
            self.__mainLogger.printErrorLog(f'This error occured while trying to reach Tomcat download links: \n {httperr}')
        except HTTPError as error:
                self.__mainLogger.printErrorLog("Error while downloading release!", error)
                sys.exit(1)
        except ConnectTimeout as error:
            self.__mainLogger.printErrorLog(f"Connection timeout while downloading project release: {error}")
            sys.exit(1)
        except IOError as error:
            self.__mainLogger.printErrorLog(f"Error while writing file: {error}")
            sys.exit(1)
        except Exception as error:
            self.__mainLogger.printErrorLog(f"An error occured while downloading release: {error}")
            sys.exit(1)
        except InvalidURL as error:
            self.__mainLogger.printErrorLog(f"URL error while downloading release: {error}")
            sys.exit(1)
        except Exception as err:
            self.__mainLogger.printErrorLog(f"Below error occured in DownloadTomcat module:\n {err}")
            sys.exit(1)
    
    def extractTomcat(self, filePath: str, extractpath: str) -> None:
        try:
            self.__mainLogger.printDebugLog(f'Extracting {os.path.basename(filePath)} ... \n')
            with zipfile.ZipFile(filePath) as tomcatzip:
                if (os.path.exists(os.path.join(extractpath, "Unpacked_Tomcat"))):
                    self.__cleanUp(os.path.join(extractpath, "Unpacked_Tomcat"))
                tomcatzip.extractall(os.path.join(extractpath, "Unpacked_Tomcat"))
                self.__tomcatSourcePath = os.path.join(extractpath, "Unpacked_Tomcat")
                for dir in os.listdir(self.__tomcatSourcePath):
                    if (os.path.isdir(os.path.join(self.__tomcatSourcePath, dir))):
                        if (set(["conf", "bin"]).issubset(os.listdir(os.path.join(self.__tomcatSourcePath, dir)))):
                            self.__tomcatSourcePath = os.path.join(self.__tomcatSourcePath, dir)
                            break
        except Exception as err:
            self.__mainLogger.printErrorLog(f'\nCouldn\'t Extract {filePath} Please Follow The Error Below:\n {err}')
            sys.exit(1)
       
    def createTomcatCopies(self, data: dict, key, value) -> None:
        self.__sshConnection = SSHConnection(self.__nodeIP, self.__osUsername, self.__osPassword)
        newTomcatDirName = '.'.join(self.__tomcatDirName.split('.')[:-1])
        # for tomcatRef in data["TOMCAT_REFERENCE"]: #############
        # key = list(tomcatRef.keys())[0]
        # value = list(tomcatRef.values())[0]
        if (self.__sshConnection.checkIfWindows()):
            if (value["TOMCAT_PATH"].endswith("\\")):
                tomcatUpdatedPath = value["TOMCAT_PATH"] + newTomcatDirName + "_" + str(key)
            else:
                tomcatUpdatedPath = value["TOMCAT_PATH"] + "\\" + newTomcatDirName + "_" + str(key)
        else:
            if (value["TOMCAT_PATH"].endswith("/")):
                tomcatUpdatedPath = value["TOMCAT_PATH"] + newTomcatDirName + "_" + str(key)
            else:
                tomcatUpdatedPath = value["TOMCAT_PATH"] + "/" + newTomcatDirName + "_" + str(key)
        if (set(["conf", "bin"]).issubset(os.listdir(self.__tomcatSourcePath))):
            value["TOMCAT_PATH"] = tomcatUpdatedPath
        elif (len(os.listdir(self.__tomcatSourcePath)) > 1):
            self.__mainLogger.printErrorLog("Couldn't find tomcat!")
            sys.exit(1)
        else:
            value["TOMCAT_PATH"] = os.path.join(tomcatUpdatedPath, os.listdir(self.__tomcatSourcePath)[0])
        # self.__tomcatRefs.update({key: value})
        if (os.path.exists(tomcatUpdatedPath)):
            if (data["BACKUP_TOMCAT_WEBAPPS_BEFORE_DEPLOY"]):
                if (not os.path.exists(self.__backupDir)):
                    os.mkdir(self.__backupDir)
                self.takeBackup(tomcatUpdatedPath)
            self.__mainLogger.printDebugLog('Cleaning old tomcat files..')
            shutil.rmtree(tomcatUpdatedPath)
        else:
            os.makedirs(tomcatUpdatedPath,exist_ok=True)
        self.__mainLogger.printDebugLog('Creating needed tomcat copies..')
        if os.path.exists(tomcatUpdatedPath):
            shutil.rmtree(tomcatUpdatedPath)
        # shutil.copytree(self.__tomcatSourcePath, tomcatUpdatedPath)
        if (self.__sshConnection.checkIfWindows()):
            self.__sshConnection.transferDirectory(self.__tomcatSourcePath, tomcatUpdatedPath, True)
        else:
            self.__sshConnection.transferDirectory(self.__tomcatSourcePath, tomcatUpdatedPath, False)
        self.__mainLogger.printDebugLog('Tomcat copies created successfully!')
        return tomcatUpdatedPath

    def configureTomcatPorts(self, tomcatRef: dict) -> None:
        self.__mainLogger.printDebugLog('Configuring tomcat ports')
        # for key in self.__tomcatRefs:
        # for tomcatRef in data["TOMCAT_REFERENCE"]:
        key = list(tomcatRef.keys())[0]
        value = list(tomcatRef.values())[0]
        # tomcatPath = data["TOMCAT_PATH"]
        serverXMLFile = os.path.join(self.__tomcatSourcePath, "conf", "server.xml")
        parsedXML = ET.parse(serverXMLFile)
        root = parsedXML.getroot()
        root.set("port", str(value["SHUTDOWN_PORT"]))
        for child in root:
            if (child.tag == "Service" and child.get("name") == "Catalina"):
                for connector in child:
                    if (connector.tag == "Connector" and "SSLEnabled" not in connector.attrib):
                        connector.set("port", str(value["CONNECTER_PORT"]))
        parsedXML.write(serverXMLFile)
        # self.createTomcatCopies(data, key, value)
        self.__mainLogger.printDebugLog('Tomcat ports configured successfully!')
        return self.__tomcatSourcePath

    def takeBackup(self, path: str) -> None:
        self.__mainLogger.printDebugLog('Prepairing for tomcat backup creation...')
        basename = os.path.basename(path)
        newBackupDir = os.path.join(self.__backupDir, basename)
        if (os.path.exists(newBackupDir)):
            shutil.rmtree(newBackupDir)
        else:
            os.mkdir(newBackupDir)
        self.__mainLogger.printDebugLog('Creating tomcat backups...')
        if os.path.exists(newBackupDir):
            shutil.rmtree(newBackupDir)
        shutil.copytree(path, newBackupDir)
    
    def runTomcats(self, tomcatPath: str, javaHome: str):
        self.__mainLogger.printDebugLog('Starting Tomcat..')
        stdin, stdout, stderr = self.__sshConnection.runTomcats(tomcatPath=tomcatPath, JAVA_HOME=javaHome)
        resultOut = stdout.read().decode("utf-8")
        resultError = stderr.read().decode("utf-8")
        if (resultOut):
            self.__mainLogger.printDebugLog(resultOut)
        elif (resultError):
            self.__mainLogger.printErrorLog(resultError)
        # for tomcat in self.__tomcatRefs:
        #     if (sys.platform == "linux"):
        #         for root, dirs, files in os.walk(self.__tomcatRefs[tomcat]["TOMCAT_PATH"]):  
        #             for dir in dirs:  
        #                 os.chmod(os.path.join(root, dir), 0o777)
        #             for file in files:
        #                 os.chmod(os.path.join(root, file), 0o777)
        #         startUp = subprocess.Popen([os.path.join(self.__tomcatRefs[tomcat]["TOMCAT_PATH"], "bin", "startup.sh")])
        self.__mainLogger.printDebugLog('\nTomcat Started Successfully!')
    
    def __cleanUp(self, path):
        self.__mainLogger.printDebugLog('Cleaning Up!')
        try:
            content = glob.glob(path)
            for file in content:
                if (os.path.isfile(file)):
                    os.unlink(file)
                elif (os.path.isdir(file)):
                    shutil.rmtree(file)
            self.__mainLogger.printDebugLog('Cleanup Done!')
        except Exception as error:
            self.__mainLogger.printErrorLog(f"An error occured while cleaning ( {path} ), follow the error below:\n {error}")

    def cleanWebApps(self):
        webAppsPath = os.path.join(self.__tomcatSourcePath, "webapps")
        if (os.path.exists(webAppsPath)):
            for item in os.listdir(webAppsPath):
                if (os.path.isfile(os.path.join(webAppsPath, item))):
                    os.unlink(os.path.join(webAppsPath, item))
                elif (os.path.isdir(os.path.join(webAppsPath, item))):
                    shutil.rmtree(os.path.join(webAppsPath, item))