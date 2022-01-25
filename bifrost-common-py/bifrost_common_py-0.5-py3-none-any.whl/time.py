"""
* Some useful time operations.
* 
* @module time.js
* @author Ralf Mosshammer <bifrost.at@siemens.com>
* @copyright Siemens AG, 2020
* Python implementation
* @author Manuel Matzinger <manuel.matzinger@siemens.com>
"""
from datetime import datetime
from datetime import timezone
from math import floor
import re
from tokenize import String

class bifrostTime:
    unitInMs = {
        'ms' : 1,
        's'   : 1000,
        'm'   : 60 * 1000,
        'h'   : 60 * 60 * 1000,
        'd'   : 24 * 60 * 60 * 1000,
        'w'   : 7 * 24 * 60 * 60 * 1000,
        'M'   : 30 * 24 * 60 * 60 * 1000,
        'y'   : 365 * 24 * 60 * 60 * 1000
    }

    """
    returns given time in ms to a timeString
    """
    def msToTime(ms:int):
        timeObject = datetime.fromtimestamp(ms/1000.0)
        timeString = timeObject.strftime("%X")
        return timeString

    """
    returns the current system time as a UTC string
    """
    def utcString():
        timeObject = datetime.now(timezone.utc)
        UTCString = timeObject.strftime("%a %d %b %Y %X %Z")
        return UTCString


    """
    Convert a conversational duration string to an actual duration in milliseconds.
    
    @param str A duration string, formatted as [value][ms|s|m|h|d|w|M|y]
    @returns The time the string represents in milliseconds.
    @throws {Error} if the string was malformed.
    """
    def durationStringToMs(stri:str):
        match = re.search('([0-9]+)([a-zA-Z]+)', stri)
        if match == None:
            raise Exception('Error in duration string conversion, input must match format [value][ms|s|m|h|d|w|M|y], was '+str(stri))
        value = int(match[1])
        unit = match[2]
        result = floor(value * bifrostTime.unitInMs[unit])
        return result

    """
    Convert a conversational duration string to an actual duration in seconds.
    @param str @see durationStringToMs
    @returns The duration string in seconds
    """
    def durationStringToS(stri:str):
        return bifrostTime.durationStringToMs(stri) / 1e3