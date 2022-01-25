"""
A set of common functions to be used in Python scripts by Esri Nederland.

### Functions
    * `configureLogging` | Configure the Logger object
    * `resetLogging` | Reset all current active Logger objects
    * `getLogger` | Get the current active Logger object, if not present, configure a new one
    * `logToArcGIS` | Log the message to the ArcGIS output window, if logging to ArcGIS is enabled
    * `logException` | Log an Exception message
    * `logError` | Log an Error message
    * `logWarning` | Log a Warning message
    * `logInfo` | Log an Info message
    * `logDebug` | Log a Debug message
    * `sendRequest` | Send a request to a URL
    * `sendGISRequest` | Send a request to a URL, using the GIS object for authentication
    * `getGIS` | Get a GIS object, either using a profile or the current active user in ArcGIS Pro
    * `dateStringToTimestamp` | Convert a date string of the given format to a timestamp
    * `timestampToDateString` | Convert a timestamp to a date string in the given format

##### Current Version: esrinlutils 0.6 | 2022-01-25

"""
from .utilities import *

__all__ = [
    "configureLogging", "resetLogging", "getLogger", "logToArcGIS",
    "logException", "logError", "logWarning", "logInfo", "logDebug",
    "sendRequest", "sendGISRequest", "getGIS", 
    "dateStringToTimestamp", "timestampToDateString"
]
