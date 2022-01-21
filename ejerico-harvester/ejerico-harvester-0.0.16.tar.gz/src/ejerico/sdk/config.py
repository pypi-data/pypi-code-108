"""
TODO doc
"""

import os
import pkg_resources
import random
import sys
import time
import logging

from pathlib import Path

from everett import NO_VALUE
from everett.ext.inifile import ConfigIniEnv
from everett.manager import ConfigManager as ConfigMgr
from everett.manager import ConfigOSEnv
from everett.manager import ConfigDictEnv
from everett.manager import listify
from everett.manager import ListOf

from ejerico.sdk.annotations import singleton

__all__ = ["ConfigManager"]

@singleton
class ConfigManager(object):

    def __init__(self):
        self._manager = None

        self._config_path = None
        self._config_url = None
        self._config_username = None
        self._config_password = None
        self._config_token = None

        #self._default_domain = "http://www.ejerico.org" 
        #self._default_namespace = "http://www.ejerico.org/ns#" 
        self._default_domain = "http://core.jerico-ri.eu"
        self._default_namespace = "http://core.jerico-ri.eu/ns#"

    def boot(self):
        paths = _defaultConfigPaths()
        
        my_paths = [
            os.path.dirname(sys.modules['__main__'].__file__),
            os.getcwd(),
            os.path.dirname(os.path.realpath(sys.argv[0])) if sys.argv[0] else None,

        ]
        for my_path in my_paths:
            my_path = "{}{}harvester.ini".format(my_path, os.sep) if my_path is not None else my_path
            if os.path.exists(my_path):
                logging.info("[ConfigManager:boot] appending config path '{}'".format(my_path))
                paths.insert(0,my_path)
        paths = list(dict.fromkeys(paths))

        if self._config_path and os.path.exists(_config_path): paths.insert(0,self._config_path)

        environments = [ConfigOSEnv()]
        environments.extend([ConfigIniEnv(p) for p in paths])
        environments.append(RemoteConfig(url=self._config_url, username=self._config_username, password=self._config_password, token=self._config_token))

        self._manager = ConfigMgr(environments=environments,doc='TODO doc')
    
    def get(self, key, namespace=None, default=None):
        namespace = "EJERICO" if namespace is None else namespace.upper()
        key = "MISSING_KEY_".format(random.randrange(1000)) if key is None else key.upper()
        
        my_parser = _getConfigParser(key)
        my_raise_error=False
        my_default = NO_VALUE

        if self._manager is None: self.boot()
        value = self._manager(key,namespace=namespace, default=my_default, parser=my_parser, raise_error=my_raise_error)
        return default if NO_VALUE == value else value

    @property
    def configPATH(self):
        return self._config_path  
    @configPATH.setter
    def configPATH(self, value):
        #raise ValueError("'TODO' is not valid")
        self._config_path = value

    @property
    def configURL(self):
        return self._config_url
    @configURL.setter
    def configURL(self, value):
        #raise ValueError("'TODO' is not valid")
        self._config_url = value

    @property
    def configUSERNAME(self):
        return self._config_username
    @configUSERNAME.setter
    def configUSERNAME(self, value):
        #raise ValueError("'TODO' is not valid")
        self._config_username = value

    @property
    def configPASSWORD(self):
        return self._config_password
    @configPASSWORD.setter
    def configPASSWORD(self, value):
        #raise ValueError("'TODO' is not valid")
        self._config_password = value

    @property
    def configTOKEN(self):
        return self._config_token
    @configTOKEN.setter
    def configTOKEN(self, value):
        #raise ValueError("'TODO' is not valid")
        self._config_token = value

    @property
    def defaultDOMAIN(self):
        return self._default_domain

    @property
    def defaultNAMESPACE(self):
        return self._default_namespace

class RemoteConfig(object):
    def __init__(self, url=None, username=None, password=None, token=None):
        pass

    def get(self, key, namespace=None):
        namespace = listify(namespace)
        return NO_VALUE

def _defaultConfigPaths():
    paths = []
    
    if 'EJERICO_CONFIG_PATH' in os.environ: paths.append(os.environ.get('EJERICO_CONFIG_PATH'))

    if sys.platform == "linux" or sys.platform == "linux2":
        paths.append("{}/.ejerico/harvester.ini".format(str(Path.home()))) 
        paths.append("/etc/ejerico/harvester.ini")
    elif sys.platform == "darwin":
        paths.append("{}/.ejerico/harvester.ini".format(str(Path.home())))
        pass
    elif sys.platform == "win32":
        pass

    
    return paths

def _getConfigParser(key):
    if not hasattr(_getConfigParser, "parsers"):
        _getConfigParser.parsers = {
            "TIMEOUT": int,
            "WORKERS": int,
            "RANGE": int,
            "RUN_ONCE": bool,
            "URLS": ListOf(str),
            "HARVESTERS": ListOf(str),
            "TAGS": ListOf(str),
            "LANGUAGES": ListOf(str),
            "USERS": ListOf(str),
            "ORGANIZATIONS": ListOf(str),
            "SOURCE_PATH": ListOf(str),
            "TOPICS": ListOf(str),
            "SEARCH_TERMS": ListOf(str),
            "FORCE_UPDATE": bool,
            "SAVE_DUMMY_MODE": bool,
            "PROFILE": bool,
        }
    
    return _getConfigParser.parsers[key] if key in _getConfigParser.parsers else str

