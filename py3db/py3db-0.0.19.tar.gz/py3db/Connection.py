import abc
import json
from hashlib import md5
from pickle import dumps


class Connection(metaclass=abc.ABCMeta):
    _instance = {}
    _link_id = None
    config = {}

    def get_config(self, config: str = ""):
        if config == "":
            return self.config
        else:
            return self.config.get(config)

    @classmethod
    def create_instance(cls, module_name: str, class_name: str, config: dict = {}):
        module_meta = __import__(
            module_name, globals(), locals(), [class_name])
        class_meta = getattr(module_meta, class_name)
        print(config)
        obj = class_meta(config)
        return obj

    @classmethod
    def instance(cls, config: dict = {}):
        md = md5()
        md.update(dumps(config))
        name = md.hexdigest()
        if not cls._instance.get(name):
            cls._instance[name] = cls.create_instance(
                'py3db.connector',
                config['type'].capitalize(),
                config
            )
        return cls._instance[name]

    @abc.abstractmethod
    def query(self, sql: str, bind: list = []):
        pass

    @abc.abstractmethod
    def execute(self, sql: str, bind: list = []):
        pass


if __name__ == "__main__":
    Connection.instance({
        "type": "mysql"
    })
