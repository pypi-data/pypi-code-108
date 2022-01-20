import sys
from typing import Tuple, Union
from colorama import Fore
import platform,subprocess,os

'''
Remaining tasks:
1- Implement logging for validations
2- Add target path validation
'''
class ValidationConfig:

    numberOfModules: int = 0

    def checkDependencies(dependancy,cmd):
        checkdep = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        checkdep.communicate()
        if int(checkdep.returncode) > 0 :
            print('\n'+dependancy+' Not Found!\n')
            return False
        else:
            return True
    
    @staticmethod
    def validateAppInfo(appInfoData: dict) -> Union[bool, Tuple[str, bool]]:
        if (appInfoData["DOWNLOAD_RELEASE"] != True and appInfoData["DOWNLOAD_RELEASE"] != False):
            print('DOWNLOAD_RELEASE parameter is invalid!')
            return False
        elif (appInfoData["DOWNLOAD_RELEASE"] == True):
            if (appInfoData["RELEASE_INFO"]["TAG_NAME"] == None or appInfoData["RELEASE_INFO"]["PROJECT_ID"] == None):
                print('TAG_NAME parameter is invalid!')
                return False
        elif (appInfoData["DOWNLOAD_RELEASE"] != True and appInfoData["RELEASE_PATH"] == None):
            print('DOWNLOAD_RELEASE parameter is invalid!')
            return False
        elif (appInfoData["BANK_NAME"] == None or appInfoData["BANK_CD"] == None):
            print("BANK_NAME parameter is invalid!")
            return False
        return True

    @staticmethod
    def validateTomcatParams(TomcatInfoData: dict) -> Union[bool, Tuple[str, bool]]:
        if ValidationConfig.checkDependencies('JAVA','java -version'):
            deployTomcat = TomcatInfoData['DEPLOY_TOMCAT']
            downloadTomcat = TomcatInfoData['DOWNLOAD_TOMCAT']
            configureTomcat = TomcatInfoData['CONFIGURE_TOMCAT']
            tomcatVersion = TomcatInfoData['TOMCAT_VERSION']
            tomcatSourcePath = TomcatInfoData['TOMCAT_SOURCE_PATH']
            if not os.path.exists(tomcatSourcePath):
                os.mkdir(tomcatSourcePath)
                print('\nTOMCAT_SOURCE_PATH Created.')
            if ( deployTomcat and downloadTomcat and configureTomcat ):
                if (tomcatVersion and os.path.exists(tomcatSourcePath) and os.path.isdir(tomcatSourcePath)):
                        return True
                else:
                    print('\nTomcat Path: ' + "'" + tomcatSourcePath + "'" + ' No Such File Or Directory!\n')
                    sys.exit(1)
            elif (deployTomcat and not downloadTomcat and not configureTomcat):
                if os.path.exists(tomcatSourcePath) and os.path.isdir(tomcatSourcePath):
                    print('Will Be Using The Tomcat Assigned To TOMCAT_SOURCE_PATH Parameter!')
                    return True
            elif (not deployTomcat and downloadTomcat):
                print('DOWNLOAD_TOMCAT parameter can\'t be True if DEPLOY_TOMCAT parameter is False!')
                return False
            elif (not deployTomcat and not downloadTomcat and not configureTomcat):
                print('No Tomcat Configurations will be done..')
                return True
            elif (downloadTomcat and not configureTomcat):
                print('CONFIGURE_TOMCAT parameter can\'t be False if DOWNLOAD_TOMCAT is True!')
                return False
        else:
            return False

    @staticmethod
    def validateDBInfo(DBInfoData: dict) -> bool:
        print("Working on ( DBInfo ) Validation Module!\n")
        print(DBInfoData)
        return False

    @staticmethod
    def validateOSType() -> str:
        OS_IS = platform.system()
        print(Fore.YELLOW +'\nOperating System Tyspe: ' + Fore.RESET + OS_IS + '\n')
        return OS_IS