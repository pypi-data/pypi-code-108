# coding: utf-8
class ENUMSBASE:
    @classmethod
    def values(cls):
        if hasattr(cls, '_values'):
            return getattr(cls, '_values')
        _values = [getattr(cls, i) for i in list(cls.__dict__.keys()) if str(i).isupper()]
        setattr(cls, '_values', _values)
        return _values
    @classmethod
    def keys(cls):
        if hasattr(cls, '_keys'):
            return getattr(cls, '_keys')
        _keys = [i for i in list(cls.__dict__.keys()) if str(i).isupper()]
        setattr(cls, '_keys', _keys)
        return _keys

class POOLTYPE(ENUMSBASE):
    SIMPLE = "simple"
    STEADY = "steady"

class DBTYPE(ENUMSBASE):
    SQLITE3 = 'sqlite3'
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'

SESSION_CONF = {}
MSGPASS_CONF = {}
ETCD_CONF = {}
SENTRY_CONF = {}
LOG_CONF = {}
