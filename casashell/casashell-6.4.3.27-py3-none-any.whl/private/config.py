##
## this module is populated by casa_shell(...)
##
import os
import time
from casashell.private import userconfig

_tstamp = time.strftime("%Y%m%d-%H%M%S",time.gmtime())

def __get_user_config_bool(user_config, attrName, defValue, logList):
    # returns value of named attribute in user_config if it is bool, else defValue
    if hasattr(user_config, attrName):
        thisValue = getattr(user_config,attrName)
        if isinstance(thisValue,bool):
            return thisValue
        else:
            # try and make strings look like strings
            valStr = str('\'%s\'' % thisValue) if isinstance(thisValue,str) else str('%s' % thisValue)
            logList.append(("%s in config.py is not a bool: %s (choose from either True or False); using %s" % (attrName, valStr, defValue), "WARN"))
    return defValue

## log messages to be used in init_welcome, list of tuples (msg,priority)
startup_log = []

##
## path to config directory
##
internal_configpath = os.path.realpath(os.path.join(os.path.dirname(__file__),'ttconfig'))

##
## paths added to the default casatools data path
##
datapath = userconfig.datapath if 'datapath' in dir(userconfig) else None
##
## path to log file
##
logfile = os.path.realpath(userconfig.logfile) if 'logfile' in dir(userconfig) else os.path.join(os.getcwd( ),'casa-'+_tstamp+'.log')
##
## path to ipython log file
##
iplogfile = os.path.realpath(userconfig.iplogfile) if 'iplogfile' in dir(userconfig) else os.path.join(os.getcwd( ),'ipython-'+_tstamp+'.log')
##
## directory containing casashell configuration files - use command line option to change this
##
rcdir = os.path.realpath(os.path.expanduser("~/.casa"))
##
## direct log output to terminal if True
##
log2term = __get_user_config_bool(userconfig,'log2term',False, startup_log)
##
## do not start the CASA logger
##
nologger = __get_user_config_bool(userconfig,'nologger',False, startup_log)
##
## do not create a log file
##
nologfile = __get_user_config_bool(userconfig,'nologfile',False, startup_log)
##
## avoid starting GUI tools
##
nogui = __get_user_config_bool(userconfig,'nogui',False, startup_log)
##
## ipython prompt color
##
colors = userconfig.colors if 'colors' in dir(userconfig) else 'Neutral'
##
## do pipeline initialization
##
pipeline = __get_user_config_bool(userconfig,'pipeline',False, startup_log)
##
## startup without graphical backend
##
agg = __get_user_config_bool(userconfig,'agg',False, startup_log)
##
## create an ipython log file
##
iplog = __get_user_config_bool(userconfig,'iplog',False, startup_log)
##
## include user's local site-packages lib in path
##
user_site = __get_user_config_bool(userconfig,'user_site',False, startup_log)
##
## command line arguments
##
flags = None
##
## non-casashell arguments
##
args = None
##
