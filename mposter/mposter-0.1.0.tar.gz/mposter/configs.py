import os
import yaml


class AddConfigs(object):
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.path_dir = os.path.dirname(os.path.realpath(__file__))

    def read_config(self, method: str, key: str = None):
        try:
            with open(os.path.join(self.path_dir, self.config_file), 'r') as yml_file:
                _config = yaml.load(yml_file)

                if method in _config:
                    if key is None:
                        return _config[method]
                    else:
                        return _config[method][key] if key in _config[method] else None
        except Exception as ex:
            print(ex)

        return None

    def change_config(self, method: str, key: str, value):
        with open(os.path.join(self.path_dir, self.config_file)) as f:
            list_doc = yaml.load(f)

        list_doc[method][key] = value

        with open(os.path.join(self.path_dir, self.config_file), "w") as f:
            yaml.dump(list_doc, f)
