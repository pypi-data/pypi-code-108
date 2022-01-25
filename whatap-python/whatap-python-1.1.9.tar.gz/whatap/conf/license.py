import io

from whatap.io.data_inputx import DataInputX
from whatap.io.data_outputx import DataOutputX

from whatap.util.hexa32 import Hexa32


class Key(object):
    def __init__(self):
        self.pcode = None
        self.security_key = io.BytesIO()

    def __repr__(self):
        to_str = '{0}: '.format(type(self).__name__)

        res = []
        for key, value in self.__dict__.items():
            if type(value).__name__.find('bytes') > -1:
                dout = DataOutputX()
                dout.writeIntBytes(value)

                if isinstance(value, bytes) or isinstance(value, bytearray):
                    for o in value:
                        if o > 128:
                            o -= 256
                        res.append(o)

            to_str += '{0}={1}, '.format(key, res)
        return to_str


class License(object):
    @staticmethod
    def getKey(lic):
        tokens = lic.split('-')
        dout = DataOutputX(len(tokens) * 8)
        for token in tokens:
            dout.writeLong(Hexa32.toLong32(token))
        key = Key()
        din = DataInputX(dout.toByteArray())
        key.pcode = din.readDecimal()
        key.security_key = din.readBlob()
        return key

    @staticmethod
    def getProjectCode(lic):
        k = License.getKey(lic)
        return k.pcode
