import requests
import json
import zipfile
import os
import datetime
import glob
import shutil
import sys
from urllib.parse import urlparse
from typing import Optional, Union
from requests.exceptions import HTTPError, ConnectTimeout, InvalidURL
from PSAPP.Logging.loggingModule import  Logging
from PSAPP.appsReader import AppsReader

class ECCReleaseBaker:

    def __init__(self, mainLogger: Logging = None) -> None:
        self.__releasePath: str = ''
        self.__result: dict = {}
        self.__url: str = ''
        self.__targetPath: str = ''
        # self.__modulesMapping = AppsReader.modulesMapping
        self.__downloadedReleasePath: str = ''
        self.__mainLogger: Logging = mainLogger
        self.__newReleasePath: str = ''
    
    def deployApps(self, result: dict) -> str:
        self.__result = result
        self.__mainLogger = self.__mainLogger
        APP_INFO: dict = self.__result["APP_INFO"]
        self.__releasePath = APP_INFO["RELEASE_PATH"]
        self.__targetPath = APP_INFO["TARGET_PATH"]
        if (APP_INFO["DOWNLOAD_RELEASE"] == True):
            self.__mainLogger.printDebugLog("Start downloading release process ...")
            self.__downloadedReleasePath = os.path.join(self.__targetPath, 'artifacts.zip')
            self.__mainLogger.printInfoLog("Start checking availability of the release ...")
            self.downloadRelease(APP_INFO["RELEASE_INFO"]["TAG_NAME"], APP_INFO["RELEASE_INFO"]["PROJECT_ID"], self.__targetPath)
            self.__mainLogger.printInfoLog(f"Release downloaded successfully, you can find it here: {self.__downloadedReleasePath}")
            self.pathRead(self.__downloadedReleasePath, None, True)
        else:
            self.pathRead(self.__releasePath, self.__targetPath, False)
        return self.__newReleasePath

    def downloadRelease(self, tagName: str, projectID: int, path: str) -> bool:
        self.__mainLogger.printInfoLog(f"Release version: {tagName}")
        self.__mainLogger.printInfoLog(f"Project ID: {projectID}")
        self.__mainLogger.printInfoLog(f"Release will be downloaded in: {path}")
        parsedData = self.__checkGitLabRelease(tagName, projectID)
        if (isinstance(parsedData, dict)):
            artifactUrl = parsedData["assets"]["links"][0]["url"]
            parsedUrl = urlparse(artifactUrl).path.split('/')
            self.__url = f"https://gitlab.com/api/v4/projects/{projectID}/jobs/{parsedUrl.__getitem__(parsedUrl.index('jobs')+1)}/artifacts"
            try:
                self.__mainLogger.printDebugLog(f"Requesting to get the release from this URL: {self.__url}")
                fileContent = requests.get(self.__url, allow_redirects=True, headers={"PRIVATE-TOKEN": "g-YpbyTyhxdCpYbDxpcD"}, timeout=3)
                self.__mainLogger.printDebugLog(f"Start writing file downloaded: {self.__downloadedReleasePath}")
                with open(self.__downloadedReleasePath, "wb") as file:
                    file.write(fileContent.content)
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
            return True
        else:
            self.__mainLogger.printErrorLog(f"Tag Name ({tagName}) is not correct, please recheck the configurations!")
            sys.exit(1)
            

    def __checkGitLabRelease(self, tagName: str, projectID: int) -> Union[bool, dict]:
        releasesUrl = f"https://gitlab.com/api/v4/projects/{projectID}/releases"
        if (not tagName.lower().startswith('v')):
            tagName = 'v' + tagName
        else:
            tagName = tagName.lower()
        try:
            data = requests.get(releasesUrl, allow_redirects=True, headers={"PRIVATE-TOKEN": "g-YpbyTyhxdCpYbDxpcD"}, timeout=3)
        except HTTPError as error:
            self.__mainLogger.printErrorLog("Error while collecting project releases!", error)
            return False
        except ConnectTimeout as error:
            self.__mainLogger.printErrorLog("Connection timeout while collecting project releases!", error)
            return False
        except Exception as error:
            self.__mainLogger.printErrorLog("An error occured collecting project releases!", error)
        except InvalidURL as error:
            self.__mainLogger.printErrorLog(f"URL error while collecting project releases: {error}")
            return False
        parsedData = json.loads(data.text)
        for record in parsedData:
            if (record["tag_name"].lower() == tagName):
                return record
        self.__mainLogger.printErrorLog(f"We could not find the tag name specified!")
        return False

    def pathRead(self, path: str, targetPath: Optional[str], download: bool) -> None:
        self.__mainLogger.printInfoLog(f"Reading the release from {path}")
        self.__unpackArchive(path, targetPath, download)

    def __unpackArchive(self, archivePath: str, targetPath: Optional[str], download: bool):
        self.__mainLogger.printDebugLog(f"Start with unpacking the release archive: {archivePath}")
        if (targetPath == None):
            targetPath = os.path.dirname(archivePath)
        self.__mainLogger.printInfoLog(f"The release will unpacked in: {targetPath}")
        if (download == True):
            try:
                self.__mainLogger.printDebugLog("Start reading the zip file!")
                with zipfile.ZipFile(archivePath, 'r') as zFile:
                    folderName = f"PS_Deploy_{(os.path.basename(archivePath)).rsplit('.', 1)[0]}_" + datetime.date.today().strftime("%b-%d-%Y")
                    unpackedReleaseDir = os.path.join(targetPath, folderName)
                    self.__mainLogger.printInfoLog(f"You can find the unpacked release here: {unpackedReleaseDir}")
                    if not os.path.exists(unpackedReleaseDir):
                        os.makedirs(unpackedReleaseDir, 0o777, exist_ok=True)
                    else:
                        self.__mainLogger.printDebugLog("The unpacked release directory already exists; start clearing!")
                        self.__clearReleaseDirectory(unpackedReleaseDir)
                        self.__mainLogger.printDebugLog("The existing unpacked release directory sucessfully cleared!")
                    zFile.extractall(unpackedReleaseDir)
                    newPath = os.path.join(unpackedReleaseDir, "artifacts")
                    for tempFile in os.listdir(newPath):
                        if (zipfile.is_zipfile(os.path.join(newPath, tempFile))):
                            self.__unpackArchive(os.path.join(newPath, tempFile), targetPath, False)
            except IOError as error:
                self.__mainLogger.printErrorLog(f"An error occured while reading the downloaded release: {error}")
                sys.exit(1)
            except zipfile.BadZipfile as error:
                self.__mainLogger.printErrorLog(f"An error occured while unpacking the downloaded release: {error}")
                sys.exit(1)
        else:
            try:
                self.__mainLogger.printDebugLog("Start reading the zip file!")
                with zipfile.ZipFile(archivePath, 'r') as file:
                    folderName = f"PS_Deploy_{(os.path.basename(archivePath)).rsplit('.', 1)[0]}_" + datetime.date.today().strftime("%b-%d-%Y")
                    unpackedReleaseDir = os.path.join(targetPath, folderName)
                    self.__newReleasePath = unpackedReleaseDir
                    self.__mainLogger.printInfoLog(f"You can find the unpacked file here: {unpackedReleaseDir}")
                    if not os.path.exists(unpackedReleaseDir):
                        os.makedirs(unpackedReleaseDir, 0o777, exist_ok=True)
                    else:
                        self.__mainLogger.printDebugLog("The unpacked file directory already exists; start clearing!")
                        self.__clearReleaseDirectory(unpackedReleaseDir)
                        self.__mainLogger.printDebugLog("The existing unpacked release directory sucessfully cleared!")
                    file.extractall(unpackedReleaseDir)
                    self.__mainLogger.printDebugLog("Started looping on all modules to unpack archives...")
                    for tempFile in os.listdir(unpackedReleaseDir):
                        if (zipfile.is_zipfile(os.path.join(unpackedReleaseDir, tempFile))):
                            self.__mainLogger.printDebugLog(f"Start unpacking {tempFile}")
                            folderName = f"PS_Deploy_{(os.path.basename(os.path.join(unpackedReleaseDir, tempFile))).rsplit('.', 1)[0]}_" + datetime.date.today().strftime("%b-%d-%Y")
                            unpackedReleaseDir = os.path.join(unpackedReleaseDir, folderName)
                            self.__mainLogger.printInfoLog(f"You can find the unpacked {tempFile} here: {unpackedReleaseDir}")
                            with zipfile.ZipFile(os.path.join(os.path.dirname(unpackedReleaseDir), tempFile)) as newFile:
                                newFile.extractall(unpackedReleaseDir)
                                unpackedReleaseDir = os.path.dirname(unpackedReleaseDir)
            except IOError as error:
                self.__mainLogger.printErrorLog(f"An error occured while reading the release path: {error}")
                sys.exit(1)
            except zipfile.BadZipfile as error:
                self.__mainLogger.printErrorLog(f"An error occured while unpacking the release path: {error}")
                sys.exit(1)

    def __clearReleaseDirectory(self, path: str) -> None:
        """
        This function clearing the target release directory before using it!
        """
        try:
            content = glob.glob(path)
            for file in content:
                print(file)
                if (os.path.isfile(file)):
                    os.unlink(file)
                elif (os.path.isdir(file)):
                    shutil.rmtree(file)
        except Exception as error:
            self.__mainLogger.printErrorLog(f"An error occured during clearing the path spacified ,,, {path} ,,,: {error}")