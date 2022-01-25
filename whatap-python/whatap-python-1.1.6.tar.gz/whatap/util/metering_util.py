from whatap.util.date_util import DateUtil


class MeteringUtil(object):
    def MeteringUtil(self, timeUnit=1000, bucketSize=301,
                     create=None, clear=None):
        self.TIME_UNIT = timeUnit
        self.BUCKET_SIZE = bucketSize
        self._time_ = self.getTime()
        self._pos_ = self._time_ % self.BUCKET_SIZE
        self.table = [self.create() for _ in range(bucketSize)]

        self.create = create
        self.clear = clear

    def create(self):
        return self.create

    def clear(self):
        return self.clear

    def getLastBucket(self):
        pos = self.getPosition()
        return self.table[self.stepback(pos)]

    def getLastTwoBucket(self):
        pos = self.stepback(self.getPosition())
        t1 = self.table[pos]
        pos = self.stepback(pos)
        t2 = self.table[pos]
        if not t1:
            return None

        return [t1, t2]

    def getCurrentBucket(self, time=None):
        if not time:
            pos = self.getPosition()
            return self.table[pos]
        else:
            pos = self.getPosition(time)
            if pos >= 0:
                return self.table[pos]
            else:
                return None

    def getPosition(self, time=None):
        curTime = self.getTime()
        if curTime != self._time_:
            i = 0
            while (curTime - self._time_) and i < self.BUCKET_SIZE:
                _pos_ = 0 if self._pos_ + 1 > self.BUCKET_SIZE - 1 \
                    else self._pos_ + 1
                self.clear(self.table[_pos_])
            i += 1

            self._time_ = curTime
            self._pos_ = int(self._time_ % self.BUCKET_SIZE)

        if not time:
            return self._pos_
        else:
            theTime = time / self.TIME_UNIT
            if theTime > curTime or theTime < curTime - self.BUCKET_SIZE + 2:
                return -1
        return int(theTime % self.BUCKET_SIZE)

    def check(self, period):
        if period >= self.BUCKET_SIZE:
            period = self.BUCKET_SIZE - 1
        return period

    def stepback(self, pos):
        if not pos:
            pos = self.BUCKET_SIZE - 1
        else:
            pos -= 1
        return pos

    def search(self, period, h=None, skip=None):
        period = self.check(period)
        pos = self.getPosition()

        if not h and not skip:
            out = []
            for i in range(period):
                out.append(self.table[pos])
            return out
        else:
            if skip:
                for _ in skip:
                    pos = self.stepback(pos)

            i = 0
            while i < period:
                h.process(self.table[pos])
                pos = self.stepback(pos)
                i += 1

            return period

    def getTime(self):
        return DateUtil.currentTime() / self.TIME_UNIT
