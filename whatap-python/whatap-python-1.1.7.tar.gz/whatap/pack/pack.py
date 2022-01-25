from datetime import datetime


class Pack(object):
    def __init__(self):
        self.pcode = 0
        self.oid = 0
        self.time = 0
    
    def __repr__(self):
        to_str = '{0}: '.format(type(self).__name__)
        
        data = self.__dict__.copy()
        for key, value in data.items():
            if key == 'time':
                value = datetime.fromtimestamp(value / 1000) \
                    .strftime('%Y-%m-%d %H:%M:%S')
                
            to_str += '{0}={1}, '.format(key, value)
        return to_str
    
    def getPackType(self):
        return 0
    
    def write(self, dout):
        dout.writeDecimal(self.pcode)
        dout.writeInt(self.oid)
        dout.writeLong(self.time)
    
    def read(self, din):
        self.pcode = din.readDecimal()
        self.oid = din.readInt()
        self.time = din.readLong()
        return self
