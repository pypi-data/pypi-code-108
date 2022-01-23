#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
from enum import Enum
from colorama import Fore
from colorama import Style

class DataLayoutType(Enum):
    DATA_TEMPLATE = "template"
    DATA_CONTAINER = "container"

class EnvironmentTypes(Enum):
    UNIX = "unix"
    WIN = "windows"
    LINUX = "linux"

class EnvironmentHostTypes(Enum):
    WIN = "WindowsHostEnvironment"
    WINCLUSTER = "WindowsCluster"

class HostTypes(Enum):
    WIN = "WindowsHost"
    UNIX = "UnixHost"

#TODO: Remove 1.3.3
class EnvironmentOps(Enum):
    ADD = "add"
    UPDATEHOST = "updatehost"
    DELETE = "delete"
    REFRESH = "refresh"
    ENABLE = "enable"
    DISABLE = "disable"
    LIST = "list"

#TODO: Remove 1.3.3
class BranchOps(Enum):
    CREATE = "create"
    DELETE = "delete"
    ACTIVATE = "activate"
    LIST = "list"

#TODO: Remove 1.3.3
class BookmarkOps(Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    SHARE = "share"
    UNSHARE = "unshare"
    LIST = "list"

# TODO: Convert to int values and update dependencies.
class VirtualOps(Enum):
    PROVISION = "create"
    REFRESH = "refresh"
    REWIND = "rewind"
    SNAPSHOT = "snapshot"
    START = "start"
    STOP = "stop"
    ENABLE = "enable"
    DISABLE = "disable"
    DELETE = "delete"
    LIST = "list"

#TODO: Remove 1.3.3
class SourceOps(Enum):
    CREATE = "create"
    DELETE = "delete"
    LINK = "link"
    UNLIK = "unlink"

# TODO: Remove 1.3.3
class TemplateOps(Enum):
    CREATE = "create"
    DELETE = "delete"
    LIST = "list"

class UserOps(Enum):
    CREATE = 1
    DELETE = 2
    LIST = 3
    UPDATE = 4
    UPDATEROLE = 5

class UserRoles(Enum):
    OWNER = "OWNER"
    PROVISIONER = "PROVISIONER"
    DATA = "OPERTOR"
    READ = "READER"

# Timestamp Formats
FORMAT_TS_MILLIS = '%Y-%m-%dT%H:%M:%S.%fZ'
FORMAT_TS_SEC = '%Y-%m-%dT%H:%M:%S'

# Default Ports
PORT_ORACLE_DEFAULT="1521"
PORT_MSSQL_DEFAULT="1433"
PORT_POSTGRES_DEFAULT = "5432"
PORT_SYBASE_DEFAULT = "5000"

# Error Messages
MSG_CONFIG_NOTFOUND1 = f"Could not find dxtools.conf at the " \
                       f"default location or the provided config location."

MSG_CONFIG_NOTFOUND2 = f"If you want to use a non-default config file, please " \
                       f"provide the full path to dxtools.conf file (including filename)"

MSG_LOG_NOTFOUND1 = f"Could not find the default logs directory or " \
                       f"the provided logs directory/file."

MSG_LOG_NOTFOUND2 = f"If you want to use a non-default logs location, please " \
                    f"provide the full path to the log file (including log filename)\n"

MSG_AUTH_TIMEOUT1 = "Authentication Request to Delphix Engine IP {} timedout after 60s."
MSG_AUTH_TIMEOUT2 = "The IP address may be incorrect or inaccessible."

MSG_AUTH_FAILED1 = "Failed to authenticate to Delphix Engine IP {} with the credentials provided."

# Error Codes
ERR_CONFIG_NOTFOUND="ERR_DXI_CONFIGNOTFOUND"
ERR_LOG_NOTFOUND="ERR_DXI_LOGNOTFOUND"
ERR_AUTH_TIMEDOUT="ERR_DXI_AUTHTIMEOUT"
ERR_AUTH_FAILED="ERR_DXI_AUTHFAILED"
ERR_OBJ_NOTFOUND="ERR_OBJ_NOTFOUND"
ERR_DXI_MISSINGINPUT="ERR_DXI_MISSINGINPUT"

# Error Actions
ACTION_CONFIG_NOTFOUND=f"Did you initialize dxi using {Fore.CYAN}'dxi config init'{Style.RESET_ALL}?\n" \
                       f"\tIf you did not, please run {Fore.CYAN}'dxi config init'{Style.RESET_ALL} before using dxi.\n\tRefer to " \
                       f"https://integrations.delphix.com/GettingStarted/index.html#configuring-dxi \n\t" \
                       f"for step-by-step instructions."

ACTION_LOG_NOTFOUND=f"Did you initialize dxi using {Fore.CYAN}'dxi config init'{Style.RESET_ALL}?\n" \
                    f"\tIf you did not, please run {Fore.CYAN}'dxi config init'{Style.RESET_ALL} before using dxi.\n\tRefer to " \
                    f"https://integrations.delphix.com/GettingStarted/index.html#configuring-dxi \n\t" \
                    f"for step-by-step instructions."

ACTION_AUTH_TIMEOUT = f"Please ensure that the engine configuration in your config file is accurate \n" \
                      f"\tand the engine is accessible over the network."

ACTION_AUTH_FAILED = f"Please ensure that credentials provided in your config file are accurate.\n"


#Common constants
FORMAT_GITHUB = "github"