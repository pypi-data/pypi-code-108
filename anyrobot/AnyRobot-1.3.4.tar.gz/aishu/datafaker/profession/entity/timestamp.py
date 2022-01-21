import time
import random

class date(object):
    def getStartTime(self):
        return int(round(time.time() * 1000))

    def getEndTime(self):
        return int(round(time.time() * 1000))

    def getLastHourTime(self):
        return int(round(time.time() * 1000)) - 3600000

    def getLast24HourTime(self):
        return int(round(time.time() * 1000)) - 86400000

    def getLastFiveYearTime(self):
        year = 365
        day = 24
        h = 60
        m = 60
        endTime = year * day * h * m * 1000 * 5
        return int(round(time.time() * 1000)) -endTime

    def getLastTime(self):
        year=365
        day=24
        h=60
        m=60
        endTime=year*day*h*m*1000
        startTime=300000
        return self.getStartTime()-random.randint(startTime,endTime)

    def getDateTime(self):
        return str(time.strftime('%Y-%m-%d %H:%M:%S'))
