from whatap.io.data_inputx import DataInputX
from whatap.io.data_outputx import DataOutputX


class IPUtil(object):
    empty = bytearray([0, 0, 0, 0])

    @classmethod
    def toString(cls, ip):
        if isinstance(ip, int):
            return cls.toString(DataOutputX.toBytes(ip))
        elif isinstance(ip, bytes) or isinstance(ip, bytearray):
            try:
                to_str = '{0}.{1}.{2}.{3}'.format(ip[0] & 0xff, ip[1] & 0xff,
                                                  ip[2] & 0xff, ip[3] & 0xff)
                return to_str
            except Exception:
                return '0.0.0.0'

    @classmethod
    def toBytes(cls, ip):
        if isinstance(ip, int):
            return DataOutputX.toBytes(ip)
        elif isinstance(ip, str):
            # if not ip:
            #     return cls.empty

            try:
                ss = ip.split('.')
                ss_ln = len(ss)
                if ss_ln != 4:
                    return cls.empty

                result = bytearray(ss_ln)
                for i in range(ss_ln):
                    s = int(ss[i])
                    if s < 0 or s > 0xff:
                        return cls.empty

                    result[i] = s & 0xff
                return result
            except Exception as e:
                import traceback
                traceback.print_stack()
                return cls.empty

    @classmethod
    def toInt(cls, ip):
        if isinstance(ip, bytes):
            if cls.isOK(ip):
                return DataInputX.toInt(ip, 0)
            else:
                return 0
        elif isinstance(ip, str):
            return DataInputX.toInt(cls.toBytes(ip), 0)

    @classmethod
    def isOK(cls, ip):
        return ip is not None and len(ip) == 4

    @classmethod
    def isNotLocal(cls, ip):
        return cls.isOK(ip) and (ip[0] & 0xff) != 127
