from enum import Enum

from pony.orm.dbapiprovider import StrConverter

class AUTH_TYPE(Enum):
    LOCAL = 1
    AD = 2



class AuthTypeConverter(StrConverter):

    def validate(self, val, *args):
        if not isinstance(val, AUTH_TYPE):
            raise ValueError('Must be an Enum.  Got {}'.format(type(val)))
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, value):
        # Any enum type can be used, so py_type ensures the correct one is used to create the enum instance
        return self.py_type[value]