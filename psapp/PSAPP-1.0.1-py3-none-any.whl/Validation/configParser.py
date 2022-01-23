import json
import yaml
from typing import Any, Tuple, Union, Optional
from PSAPP.Validation.validationConfig import ValidationConfig
from colorama import Fore

'''
Remaining tasks:
1- implement logging for validations
'''
class ConfigParser:

    def __init__(self) -> None:
        pass

    @staticmethod
    def readConfig(path: str) -> dict:
        with open(path, "r") as file:
            data = yaml.safe_load(file)
            return data
    
    @staticmethod
    def validateConfigs(path: str) -> Union[dict, Tuple[bool, str]]:
        print("\nWorking on ( ValidationConfigs ):\n")
        data: dict = ConfigParser.readConfig(path)
        # if (data["APP_INFO"]["APP_DEPLOY"] == True):
        #     appInfoValid: Union[bool, Tuple[bool, str]] = ValidationConfig.validateAppInfo(data["APP_INFO"])
        #     if (isinstance(appInfoValid, tuple)):
        #         print("appInfoValid Not valid")
        #         return appInfoValid 
        # print('( ValidationConfigs ): Checked.')               
        # print("\nWorking on ( TomcatModule ):\n")
        # if (data["TOMCAT_INFO"]["DEPLOY_TOMCAT"] == True):
        #     TomcatInfoValid: Union[bool, Tuple[bool, str]] = ValidationConfig.validateTomcatParams(data["TOMCAT_INFO"])
        #     # if not (isinstance(TomcatInfoValid, tuple)):
        #     if not TomcatInfoValid:
        #         print("\ntomcatInfoValid Are Invalid!")
        #         print("\nThe Above Error Means That " + Fore.RED + "Tomcat Parameters" + Fore.RESET + " Are Not Properly Set, Please Follow The Comment's Beside Each Tomcat Parameter In The Config File!\n")
        #         return TomcatInfoValid
        # print('\n( TomcatModule ): Checked.')
        # # dbInfoValid: Tuple[bool, str] = ValidationConfig.validateDBInfo(data["DB_INFO"])
        # # if (dbInfoValid == False):
        # #     return dbInfoValid
        return data