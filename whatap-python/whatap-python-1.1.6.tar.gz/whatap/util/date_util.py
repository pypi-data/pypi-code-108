import time

from datetime import datetime


class DateUtil(object):
    delta = 0

    MILLIS_PER_SECOND = 1000
    MILLIS_PER_MINUTE = 60 * MILLIS_PER_SECOND
    MILLIS_PER_FIVE_MINUTE = 5 * 60 * MILLIS_PER_SECOND
    MILLIS_PER_TEN_MINUTE = 10 * MILLIS_PER_MINUTE
    MILLIS_PER_HOUR = 60 * MILLIS_PER_MINUTE
    MILLIS_PER_DAY = 24 * MILLIS_PER_HOUR

    @classmethod
    def setServerTime(cls, time, syncfactor):
        now = cls.now()
        delta = time - now
        if delta:
            delta *= syncfactor
        cls.delta = delta
        return cls.delta

    @classmethod
    def currentTime(cls):
        return int(round(time.time() * 1000)) + cls.delta

    @classmethod
    def getServerDelta(cls):
        return cls.delta

    @classmethod
    def now(cls):
        return cls.currentTime()

    @classmethod
    def nowSystem(cls):
        return int(round(time.time() * 1000))

    @classmethod
    def getFiveMinUnit(cls):
        return int(int(
            cls.currentTime() / cls.MILLIS_PER_FIVE_MINUTE) * cls.MILLIS_PER_FIVE_MINUTE)

    @classmethod
    def datetime(cls):
        return datetime.now()

    @classmethod
    def yyyymmdd(cls, time=None):
        if not time:
            time = cls.currentTime()
        return datetime \
            .fromtimestamp(time / 1000).strftime('%Y%m%d')
