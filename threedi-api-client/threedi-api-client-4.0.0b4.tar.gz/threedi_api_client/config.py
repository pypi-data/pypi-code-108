import os


class ConfigError(Exception):
    pass


class Config:
    def __init__(self, env_file=None):
        self.file_values = {}
        if env_file is not None and os.path.isfile(env_file):
            self.file_values = self._read_file(env_file)
        else:
            raise ConfigError("Could not find %s", env_file)

    def __call__(self, key):
        return self.get(key)

    def get(self, key):
        if key in self.file_values:
            return self.file_values[key]
        return None

    def _read_file(self, file_name):
        file_values = {}
        with open(file_name) as input_file:
            for line in input_file.readlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    file_values[key] = value
        return file_values


class EnvironConfig:
    def __call__(self, key):
        return self.get(key)

    def get(self, key):
        if key in os.environ:
            value = os.environ[key]
            return value
        return None
