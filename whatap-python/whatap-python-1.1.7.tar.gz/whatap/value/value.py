class Value(object):
    def __init__(self):
        return

    def __repr__(self):
        to_str = '{0}: '.format(type(self).__name__)
        for key, value in self.__dict__.items():
            to_str += '{0}={1}, '.format(key, value)
        return to_str

    def equals(self, object):
        if isinstance(object, Value):
            return self.value == object.value
        return False

    def getValueType(self):
        return 0

    def toObject(self):
        return self

    def write(self, dout):
        return

    def read(self, din):
        return self
