from datetime import datetime
import dateutil.parser
import copy
import sys

class ParseTimeStamp(object):
    '''
    Helper object for parsing time stamps in a variety of formats.
    Caches last matching time stamp format string to speed subsequent calls.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.lastTimeStampFormat = None
        

    def parseTimeStamp(self, timeStampString):
        '''
        Parses and tries to find the format of the given timeStampString.
        Several formats are explicitly supported. If none of those match it uses a slower smart-matching algorithm.
        Returns a datetime object.
        Side-effect: If succesful determing the format, sets self.timeStampFormat to the matching format string.
        
        :param timeStampString: A string representation of a timeStamp, such as "2020-05-21 14:30:15.100"
        '''
        self.lastTimeStampFormat = None
        
        # try SQL format:
        timeStamp = self.parseTimeStampWithFormatString(timeStampString, '%Y-%m-%d %H:%M:%S')
        if timeStamp:
            return timeStamp
        
        # try SQL format with milliseconds:
        timeStamp = self.parseTimeStampWithFormatString(timeStampString, '%Y-%m-%d %H:%M:%S.%f')
        if timeStamp:
            # was parsed as microseconds; convert to ms:
            timeStamp.replace(microsecond= timeStamp.microsecond // 1000)
            return timeStamp
        
        # try with seconds and AM/PM:
        timeStamp = self.parseTimeStampWithFormatString(timeStampString, '%Y-%m-%d %I:%M:%S %p')
        if timeStamp:
            return timeStamp
        
        # ask dateutil.parser to do its best:
        try:
            timeStamp = dateutil.parser.parse(timeStampString)
        except ValueError as err:
            return False
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            return timeStamp
        
    def parseTimeStampWithFormatString(self, timeStampString, timeStampFormat):
        '''
        Private, though is called directly by test cases.
        Test parsing timeStamp using the given timeStampFormat
        returns a datetime object if successful, False otherwise
        Side-effect: If succesful, sets self.timeStampFormat to timeStampFormat.
        :param timeStampString: string to parse
        :type timeStampString:  str
        :param timeStampFormat: format to try, using the format codes from datetime.strptime()
        :type timeStampFormat:  str
        '''
        self.lastTimeStampFormat = None
        try:
            timeStamp = datetime.strptime(timeStampString, timeStampFormat)
        except ValueError as err:
            return False
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            self.lastTimeStampFormat = timeStampFormat
            return timeStamp

def makeTimeStamp(timeStamp = None):
    '''
    initialized a timestamp from provided, or now() if None provided
    :param timeStamp: string or datetime or None
    '''
    if not timeStamp:
        return datetime.now()
    if isinstance(timeStamp, datetime):
        return copy.copy(timeStamp)
    try:
        makeTimeStamp.parseTimeStamp
    except:
        makeTimeStamp.parseTimeStamp = ParseTimeStamp()
    try:
        return makeTimeStamp.parseTimeStamp.parseTimeStamp(timeStamp)
    except:
        return datetime.now()
