
class Credential(object):
    _instance = None
    api_key = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Credential, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance