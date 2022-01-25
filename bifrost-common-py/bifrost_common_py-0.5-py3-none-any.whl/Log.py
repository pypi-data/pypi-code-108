"""
* A generic logging module.
* 
* @module Log
* @author Ralf Mosshammer <ralf.mosshammer@siemens.com>
* @copyright Siemens AG 2019, 2020

* Python implementation and adaptation
* @author Manuel Matzinger <manuel.matzinger@siemens.com>
"""
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import date, datetime

class colors: 
    black='\033[30m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'
    purple='\033[35m'
    cyan='\033[36m'
    lightgrey='\033[37m'
    darkgrey='\033[90m'
    lightred='\033[91m'
    lightgreen='\033[92m'
    yellow='\033[93m'
    lightblue='\033[94m'
    pink='\033[95m'
    lightcyan='\033[96m'
    white='\033[37m'
    bgRed='\033[41m'
    bold='\033[1m'
    end='\033[0m'

cfg_enableLogFiles = 'enableLogFiles'
DEFAULT_ENABLE_LOGFILES = False
cfg_maxLogFileSize = 'maxLogFileSize'
DEFAULT_MAX_LOGFILE_SIZE = 1e6
cfg_maxArchiveSize = 'maxArchiveSize'
DEFAULT_MAX_ARCHIVE_SIZE = 5
cfg_logDir = 'logDir'
DEFAULT_LOG_DIR = 'log'

STYLE_DEBUG           = colors.lightgrey
STYLE_INFO            = colors.white
STYLE_WARNING         = colors.yellow
STYLE_ERROR           = colors.red
STYLE_FAILURE         = colors.bold + colors.bgRed
MAX_APP_LENGTH        = 15
MAX_COMPONENT_LENGTH  = 35
MAX_LEVEL_LENGTH      = 10



DEFAULT_APP_NAME      = 'BIFROST'

class BaseLogger:
    def __init__(self, options, appName=DEFAULT_APP_NAME):
        self._logger = logging.getLogger().setLevel(logging.NOTSET)
        self.handler = None

        if self._logger is None:
            self._logger = logging.getLogger(appName)
            self.handler = logging.StreamHandler()
            self.handler.setFormatter(Formatter())
            #self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(self.handler)

        enableLogFiles = BaseLogger.get(options, cfg_enableLogFiles, DEFAULT_ENABLE_LOGFILES)
        if enableLogFiles:
            logDir = BaseLogger.get(options, cfg_logDir, DEFAULT_LOG_DIR)
            print(logDir)
            maxLogFileSize = BaseLogger.get(options, cfg_maxLogFileSize, DEFAULT_MAX_LOGFILE_SIZE)
            maxArchiveSize = BaseLogger.get(options, cfg_maxArchiveSize, DEFAULT_MAX_ARCHIVE_SIZE)
            now = datetime.now()
            dt_string = now.strftime('%Y-%m-%d_%H-%M-%S') #now.strftime("%d/%m/%Y_%H-%M-%S")
            filename = str(logDir)+'/'+str(appName)+'-'+dt_string+'.log'
            rotatingHandler = RotatingFileHandler(filename, maxBytes=maxLogFileSize, backupCount=maxArchiveSize)
            self._logger.addHandler(rotatingHandler)
            logging.getLogger().addHandler
    
    def log(self, obj, level = 'INFO'):
        message = ''
        if type(obj) is object:
            message = '\n-- (json)\n'+json.dumps(obj, None, 2)+'\n--'
        else:
            message = obj
        self._logger.log(getattr(logging, level), message)

    def get(objectp, path, default = None):
        try:
            return objectp[path]
        except Exception as e:
            #print(e)
            return default

BaseLoggerByApp = {}

class Log:

    DEBUG   = 'DEBUG'
    INFO    = 'INFO'
    WARNING = 'WARNING'
    ERROR   = 'ERROR'
    FATAL   = 'FATAL'

    def __init__(self, component, options = {}, appName = DEFAULT_APP_NAME):
        if not appName in BaseLoggerByApp:
            BaseLoggerByApp[appName] = BaseLogger(options, appName)
        self.baseLogger = BaseLoggerByApp[appName]
        self.component = component
        # self._from = component
        # length = len(self._from)
        # self._from = self._from[0:MAX_COMPONENT_LENGTH-3] + '...' if length > MAX_COMPONENT_LENGTH else self._from
        # self._from = str(self._from).ljust(MAX_COMPONENT_LENGTH)

    def log(self, obj, level = 'INFO'):
        self.baseLogger.log(obj, level)

    def print(self, obj, level = 'INFO'):
        self.log(obj, level)

    def write(self, obj, level = 'INFO'):
        self.log(obj, level)


class Formatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = STYLE_INFO +"%(asctime)s %(name)s "+ "%(message)s" + colors.end
        elif record.levelno == logging.DEBUG:
            self._style._fmt = STYLE_DEBUG  +"%(levelname)s %(asctime)s %(name)s "+ "%(message)s" + colors.end
        elif record.levelno == logging.WARNING:
            self._style._fmt = STYLE_WARNING +"%(levelname)s %(asctime)s %(name)s "+ "%(message)s" + colors.end
        elif record.levelno == logging.ERROR:
            self._style._fmt = STYLE_ERROR +"%(levelname)s %(asctime)s %(name)s "+ "%(message)s" + colors.end
        elif record.levelno == logging.FATAL:
            self._style._fmt = STYLE_FAILURE +"%(levelname)s %(asctime)s %(name)s "+ "%(message)s" + colors.end
        else:
            self._style._fmt = "%(levelname)s: %(message)s"
        return super().format(record)