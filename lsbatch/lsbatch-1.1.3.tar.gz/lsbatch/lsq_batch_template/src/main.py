import traceback
from helper import LS


# Every Batch Job code main.py and must have a 'main' function which should not have any parameters is an entry point
# If you fail to follow this, you will get error while uploading the code in Batch Job application.
# Always make sure to handle exceptions
# Import 'LS' Library to write logs or access the variable values in the code
# We have info, debug, warn, error, fatal logs
# Do not include more packages if not used in code. Zip file should not be more than 1MB
def main():
    try:
        # write a simple log
        LS.log.info('Hello')
        # pass additional JSON object to log
        LS.log.info('Hello', {"Support Email": "support@leadsquared.com"})
        # To Access Variable value - LS.settings.<KeyName> (Key-Pair eg. Key = mykey)
        LS.log.info(LS.settings.mykey)
        # To write Debug Logs
        LS.log.debug('Debug Log Example')
    except TypeError as err:
        LS.log.fatal(type(err).__name__, traceback.format_exc())
    except Exception as err:
        LS.log.error(type(err).__name__, traceback.format_exc())
