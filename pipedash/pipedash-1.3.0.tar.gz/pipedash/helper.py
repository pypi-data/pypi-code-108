
import asyncio
import calendar
import datetime
import json
import os
import sys
from dataclasses import dataclass
import importlib
import subprocess
import logging
import re

log = logging
currentfile = sys.argv[0]

@dataclass
class Serializable(object):

    # The serialization function for JSON, if for some reason you really need pickle you can use it instead
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def serialize(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        return obj.__dict__

def serializeDTO(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime.date):
        return datetime.datetime.strftime(obj, "%Y-%m-%dT%H:%M:%S.%fZ")
    serialize_op = getattr(obj, "serialize", None)
    if callable(serialize_op):
        return obj.serialize(obj)
    if hasattr(obj, "__dict__"):
        return obj.__dict__

    return None

def debug(debug=True):
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    if debug:
        log.basicConfig(level=logging.INFO)
    else:
        log.basicConfig(level=logging.ERROR)
    return None


def set_loglevel(level):
    log.basicConfig(level=level)


if not 'workbookDir' in globals():
    workbookDir = os.getcwd()


def checkIfCodeContainsVersionorExit( code):
    found = False
    try:
        found = re.search('(#version:)[ ]*([0-9a-z]*\.[0-9a-z]*\.[0-9a-z]*)([\n,\\\n])', code).group(2)
    except AttributeError:
        found = False

    if not found:
        print("ERROR: You should add '#version: 1.X.X' to your file")
        sys.exit(0)
    return found

def periodInSeconds(period):
    if period.endswith("m"):
        return float(period.replace("m", "")) * 60
    if period.endswith("h"):
        return float(period.replace("h", "")) * 60 * 60
    if period.endswith("d"):
        return float(period.replace("d", "")) * 60 * 60 * 24
    if period.endswith("M"):
        return float(period.replace("M", "")) * 60 * 60 * 24 * 30
    if period.endswith("Y"):
        return float(period.replace("Y", "")) * 60 * 60 * 24 * 365
    return 60


def isFinalTimestamp(coinlibtimeframe, date, lastFinalDate = None):
    mydate = None
    lastFinal = None
    if lastFinalDate is not None:
        if isinstance(lastFinalDate, str):
            lastFinal = datetime.datetime.strptime(lastFinalDate, "%Y-%m-%dT%H:%M:%S.%fZ")
        if isinstance(lastFinalDate, int):
            lastFinal = datetime.datetime.fromtimestamp(lastFinalDate / 1000)
        if isinstance(lastFinalDate, datetime.datetime):
            lastFinal = lastFinalDate
    if isinstance(date, str):
        mydate = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    if isinstance(date, int):
        mydate = datetime.datetime.fromtimestamp(date / 1000)
    if isinstance(date, datetime.datetime):
        mydate = date

    nowdate = datetime.datetime.now()

    if mydate is not None:
        if nowdate.weekday() == mydate.weekday() and \
                nowdate.month == mydate.month and \
                nowdate.year == mydate.year:
            timestamp = calendar.timegm(mydate.utctimetuple())
            periodSeconds = periodInSeconds(coinlibtimeframe)
            restofseconds = timestamp % periodSeconds
            if restofseconds == 0 and mydate.microsecond < 999000:
                if lastFinalDate is not None:
                    timestamp = calendar.timegm(mydate.replace(second=0, microsecond=0).utctimetuple())
                    lastFinaltimestamp = int(calendar.timegm(lastFinal.replace(second=0, microsecond=0).utctimetuple()))
                    if lastFinaltimestamp == timestamp:
                        return False
                print(mydate)
                return True

    return False


class Timer:
    def __init__(self, timeframe, coinlibClass, params, callback):
        self._periodSeconds = periodInSeconds(timeframe)
        self._params = params
        self._c = coinlibClass
        self._timeframe = timeframe
        self._callback = callback
        self._maximumInterval = self._periodSeconds / 60
        if self._maximumInterval > 60:
            self._maximumInterval = 60
        self._minimumInterval = 0.02
        self._dynamicInterval = 1
        self._is_first_call = True
        self._ok = True
        self._lastFired = 0
        self._task = asyncio.ensure_future(self._job())

    def checkTimeFrame(self, mydate):
        timestamp = calendar.timegm(mydate.utctimetuple())
        timestampSeconds = timestamp
        periodSeconds = periodInSeconds(self._timeframe)
        restofseconds = timestamp % periodSeconds
        if restofseconds == 0 \
                and self._lastFired < timestampSeconds:
            self._lastFired = int(timestamp)
            return True

        return self._periodSeconds - restofseconds

    async def _job(self):
        try:
            while self._ok:
                if self._dynamicInterval < self._minimumInterval:
                    self._dynamicInterval = self._minimumInterval
                if not self._is_first_call:
                    await asyncio.sleep(self._dynamicInterval)
                mydate = datetime.datetime.now()
                timeFrameSlot = self.checkTimeFrame(mydate)
                if isinstance(timeFrameSlot, bool) and timeFrameSlot == True:
                    await self._callback(self._c, self._timeframe, mydate, self._params)
                else:
                    if timeFrameSlot < 60:
                        self._dynamicInterval = 1
                    if timeFrameSlot < 10:
                        self._dynamicInterval = 0.5
                    if timeFrameSlot < 5:
                        self._dynamicInterval = 0.05
                    if timeFrameSlot >= 60:
                        self._dynamicInterval = self._maximumInterval
                self._is_first_call = False
        except Exception as ex:
            print(ex)

    def cancel(self):
        self._ok = False
        self._task.cancel()

def createTimerWithTimestamp(callback, timeframe, c, params):
    timer = Timer(timeframe=timeframe, coinlibClass=c, params=params, callback=callback)
    return timer


def find_current_runner_file(searchFor=[".waitForJobs", ".connectAsLogic",".connectAsBroker",
                                        ".connectAsFeature", ".connectAsNotification",
                                        ".connectCoinlib", ".connectAsBrokerSymbol"]):
    try:
        rel_path = ""
        last_path = ""
        for i in range(30):
            cur_path = sys._getframe(i).f_globals['__file__']
            code = get_current_plugin_code(cur_path)
            containsSearchFor = False
            try:
                for sf in searchFor:
                    if sf in code and sf + "\"" not in code:
                        containsSearchFor = True
            except AttributeError:
                containsSearchFor = False
                pass
            if containsSearchFor:
                rel_path = cur_path
                break
            last_path = cur_path

        cwd = os.getcwd()
        abs_path = os.path.join(cwd, rel_path)
        only_filename = os.path.splitext(os.path.basename(abs_path))[0]
        return abs_path, only_filename
    except Exception as e:
        printError("Can not find the code for your file - look if you connected coinlib Correct. (Use one of: "+",".join(searchFor)+" )")
        sys.exit(0)


def get_current_plugin_code(abs_path):
    f = open(abs_path)
    return f.read()

def printError(msg):
    print('\033[31m'+msg+'\033[31m')


def pip_install_or_ignore(import_name, module_name):
    try:
        return importlib.import_module(import_name)
    except ImportError:
        print("missing importing of " + import_name)
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

def debug(debug=True):
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    if debug:
        log.basicConfig(level=logging.INFO)
    else:
        log.basicConfig(level=logging.ERROR)
    return None