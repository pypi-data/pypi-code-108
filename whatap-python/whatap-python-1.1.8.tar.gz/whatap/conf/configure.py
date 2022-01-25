import os, time

from whatap.conf.configuration import Configuration


class Configure(object):
    PCODE = 0
    OID = 0
    OKIND = 0
    OKIND_NAME = os.environ.get("ENV_OKIND", "-".join(os.environ.get("POD_NAME", "").split("-")[0:-1]))
    dev = False
    net_udp_port = 6600
    last_loaded = 0
    last_config_modified = 0
    observers = []
    POD_NAME = os.environ.get("POD_NAME") if os.environ.get('POD_NAME') else os.environ.get("PODNAME") if os.environ.get("PODNAME") else ''

    @classmethod
    def init(cls, display=True):
        
        cls.last_loaded = time.time()
        return cls.load(display)

    @classmethod
    def load(cls, display=True):
        home = 'WHATAP_HOME'
        try:
            whatap_config = os.path.join(os.environ[home],os.environ['WHATAP_CONFIG'])
            last_modified = os.path.getmtime(whatap_config)
            if cls.last_config_modified >= last_modified:
                return True
            for key, value in Configuration.items():
                setattr(cls, key, value)
            with open(whatap_config, 'r') as f:
                for line in f:
                    cls.last_config_modified = last_modified
                    line_strip = line.strip()
                    if not line_strip or line_strip.startswith('#'):
                        continue
                    try:
                        key, value = line.split('=')
                        key = key.strip()
                        value = value.strip()
                        if key and key.endswith("_set"):
                            value = value.split(",")
                        cls.setProperty(key, value)
                    
                    except Exception as e:
                        print('WHATAP: ', e)
                        continue
            for callback in cls.observers:
                callback()
        except Exception as e:
            from whatap import CONFIG_FILE_NAME, init_config
            init_config(home)
            return False
        else:
            return True
        finally:
            if display:
                from whatap import Logger
                Logger()
            
    @classmethod
    def getProperty(cls, key, value=None):
        if hasattr(cls, key):
            return getattr(cls, key)
        else:
            return value
    
    @classmethod
    def setProperty(cls, name, value):
        if hasattr(cls, name):
            if isinstance(getattr(cls, name), bool) and str(value) != 'true':
                value = False
        
        setattr(cls, name, value)
    
    def getStringSet(cls, key, default_value, deli):
        l = list()
        value = cls.getProperty(key, default_value)
        if value:
            for v in value.split(deli):
                l.append(v)
        return l

    @classmethod
    def addObserver(cls, callback):
        cls.observers.append(callback)