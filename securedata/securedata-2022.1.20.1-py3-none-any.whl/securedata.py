import os
import json
import pathlib
import logging
from sys import argv, exit, stdout
from datetime import date

initialized = False

def main():
    global securePath
    global settings
    global logPath
    global configPath
    global initialized
    settings = None

    if initialized:
        return

    # config file, stored within the package
    configPath = f'{pathlib.Path(__file__).resolve().parent}/config.json'

    # Determines where data is stored; by default, this is ~/securedata
    securePath = os.path.expanduser(getConfigItem('path_securedata') or '~/securedata')

    # initialize settings file if it doesn't exist
    try:
        with open(f'{securePath}/settings.json', 'r+') as f:
            f.seek(0, os.SEEK_END)
    except:
        if not os.path.exists(securePath):
            os.makedirs(securePath)
        with open(f'{securePath}/settings.json', 'x+') as f:
            print(f"\n\nWarning: settings.json not found; created a blank one in {securePath}")
            print("You can change this location by calling 'securedata config'.\n\n")
            f.write('{}')

    try:
        settings = json.load(open(f'{securePath}/settings.json'))
    except json.decoder.JSONDecodeError as e:
        response = input(f"The settings file ({securePath}/settings.json) is not valid JSON. Do you want to replace it with an empty JSON file? (you will lose existing data) (y/n)\n")
        if(response.lower().startswith("y")):
            with open(f'{securePath}/settings.json', 'w+') as f:
                f.write('{}')
            print("Done. Please try your last command again.")
        else:
            print(f"OK. Please fix {configPath}/settings.json and try again.")

        exit(-1)


    logPath = getItem('path_log') 
    if logPath == None:
        logPath = setItem('path_log', f"{securePath}/log", fileName='settings.json')
        print(f"\n\nCalling securedata.log in Python will now write to {securePath}/log by default.")
        print(f"You can change this in {securePath}/settings.json.\n\n")
    if not os.path.exists(logPath):
        os.makedirs(logPath)
    if not logPath[-1] == '/':
        logPath += '/'

    initialized = True


def getItem(*attribute):
    """
    Returns a property in settings.json.
    Usage: get('person', 'name')
    """

    global settings
    if settings == None:
        return None

    _settings = settings

    for index, item in enumerate(attribute):
        if item in _settings:
            _settings = _settings[item]
        else:
            print(
                f"Warning: {item} not found in {_settings if index > 0 else f'{securePath}/settings.json'}")
            return None

    return _settings


def setItem(*attribute, value=None, fileName='settings.json'):
    """
    Sets a property in settings.json (or some other `fileName`).
    Usage: set('person', 'name', 'Tyler')
    The last argument is the value to set, unless value is specified.
    Returns the value set.
    """

    global settings
    secureFullPath = f"{securePath}/{fileName}"

    if(not value):
        value = attribute[-1]

    _settings = settings if fileName == 'settings.json' else json.load(
        open(secureFullPath))

    # iterate through entire JSON object and replace 2nd to last attribute with value

    partition = _settings
    for index, item in enumerate(attribute[:-1]):
        if item not in partition:
            partition[item] = value if index == len(attribute) - 2 else {}
            partition = partition[item]
            print(
                f"Warning: Adding new key '{item}' to {partition if index > 0 else secureFullPath}")
        else:
            if(index == len(attribute) - 2):
                partition[item] = value
            else:
                partition = partition[item]

    with open(secureFullPath, 'w+') as file:
        json.dump(_settings, file, indent=4)

    return value


def getFileAsArray(item, filePath=None):
    """
    Returns the file as an array
    """

    global logPath
    if(filePath == None):
        filePath = logPath
    elif(filePath == "notes"):
        filePath = getItem('path_tasks_notes')

        if(not filePath[-1] == '/'):
            filePath += '/'

        # pull from cloud
        try:
            os.system(f"rclone copy {getItem('path_cloud_notes')} {filePath}")
        except Exception as e:
            log(f"Could not pull Notes from cloud: {e}", level="error")

    try:
        content = open(filePath + item, "r").read()
        return content.split('\n')
    except Exception as e:
        log(f"getFileAsArray: {e}", level="error")
        return ""


def writeFile(fileName, filePath=None, content=None, append=False):
    """
    Writes a file to the specified path and creates subfolders if necessary
    """

    global logPath
    _filePath = filePath
    
    if filePath == None:
        filePath = logPath
    elif filePath == "notes":
        filePath = getItem('path_tasks_notes')

    if content == None:
        content = ""

    if not os.path.exists(filePath):
        os.makedirs(filePath)

    with open(filePath + "/" + fileName, 'w+' if not append else 'a+') as file:
        file.write(content)

    # push to cloud
    if _filePath == "notes":
        try:
            os.system(f"rclone copy {filePath} {getItem('path_cloud_notes')}")
        except Exception as e:
            log(f"Could not sync Notes to cloud: {e}", level="error")

def getConfigItem(key=None):
    global configPath

    try:
        with open(configPath, 'r+') as file:
            return json.load(file)[key]
    except FileNotFoundError as e:
        if key == 'path_securedata':
            setConfigItem(key, str(pathlib.Path(__file__).parent.resolve()))
            return str(pathlib.Path(__file__).parent.resolve())
    except KeyError:
        return None
    except json.decoder.JSONDecodeError as e:
        response = input(f"The config file ({configPath}) is not valid JSON. Do you want to replace it with an empty JSON file?  (you will lose existing data) (y/n)\n")
        if(response.lower().startswith("y")):
            with open(configPath, 'w+') as f:
                f.write('{}')
            print("Done. Please try your last command again.")
        else:
            print(f"OK. Please fix {configPath} and try again.")

        exit(-1)

def setConfigItem(key=None, value=None):
    """
    Updates the internal configuration file
    """

    global configPath

    if value == "":
        print("No changes were made.")
        exit(1)
    else:
        
        # error correction
        if(key == 'path_securedata' and value[0] != '/' and value[0] != '~'):
            value = f"/{value}"
        if(key == 'path_securedata' and value[-1] == '/'):
            value = f"{value[:-1]}"

        # warn about potential problems
        if(not os.path.exists(os.path.expanduser(value))):
            print(f"Warning: {value} is not a valid path.")
        if(value[0] == '~'):
            print("Warning: using tilde expansions may cause problems if using securedata for multiple users. It is recommended to use full paths.")

    try:
        with open(configPath, 'r+') as file:
            config =  json.load(file)
    except FileNotFoundError:
        with open(configPath, 'x+') as f:
            print(f"Note: Could not find an existing config file... creating a new one.")
            f.write('{}')
            config = {}
            
    config[key] = value

    with open(configPath, 'w+') as file:
        json.dump(config, file, indent=4)

    print(f"\n\nUpdated configuration file ({configPath}).")
    print(f"{key} is now {value}\n")

    return value

def getLogger(logName=None, level=logging.INFO, filePath=None):
    """
    Returns a custom logger with the given name and level
    """

    today = str(date.today())

    if filePath == None:
        filePath = f"{logPath}{today}"
    if logName == None:
        logName = f"LOG_DAILY {today}"

    # create path if necessary
    if not os.path.exists(filePath):
        print(f"Creating {filePath}")
        os.makedirs(filePath)
    
    logger = logging.getLogger(logName)
    logger.setLevel(level)
    
    if logger.handlers:
        logger.handlers = []

    format_string = ("%(asctime)s — %(levelname)s — %(message)s")
    log_format = logging.Formatter(format_string)
    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler(f"{filePath}/{logName}", mode='a')
    file_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    return logger

def log(message=None, logName=None, level="info", filePath=None):

    if message == None:
        message = ""
    
    if level == None or level == "info":
        logger = getLogger(logName=logName, level=logging.INFO, filePath=filePath)
        logger.info(message)
    elif level == "debug":
        logger = getLogger(logName=logName, level=logging.DEBUG, filePath=filePath)
        logger.debug(message)
    elif level == "warn" or level == "warning":
        logger = getLogger(logName=logName, level=logging.WARN, filePath=filePath)
        logger.warning(message)
    elif level == "error":
        logger = getLogger(logName=logName, level=logging.ERROR, filePath=filePath)
        logger.error(message)
    elif level == "critical":
        logger = getLogger(logName=logName, level=logging.CRITICAL, filePath=filePath)
        logger.critical(message)
    else:
        logger = getLogger(logName=logName, level=logging.ERROR, filePath=filePath)
        logger.error(f"Unknown log level: {level}; using ERROR")
        logger.error(message)


# Initialize
main()

if __name__ == "__main__":
    print(f"SecureData is a library not intended to be directly run. See README.md.")

if argv[-1] == 'config':
    setConfigItem('path_securedata', input(f"Enter the full path of where you want to store all data (currently {securePath}/settings.json):\n"))