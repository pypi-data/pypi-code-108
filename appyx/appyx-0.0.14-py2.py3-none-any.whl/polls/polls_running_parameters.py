class CommandLineParameter:
    def __init__(self, keyword, default_value):
        self._keyword = keyword
        self._default_value = default_value

    def value(self):
        import sys
        from getopt import getopt

        opts, args = getopt(sys.argv, "", [self._keyword + "="])
        for (opt, value) in opts:
            if opt == "--" + self._keyword:
                return value

        return self._default_value


class SettingsFileParameter:
    def __init__(self, settings, parameter_key):
        self._settings = settings
        self._parameter_key = parameter_key

    def value(self):
        return getattr(self._settings, self._parameter_key)


class EnvironmentVariableParameter:
    def __init__(self, var, default):
        self._var = var
        self._default = default

    def value(self):
        try:
            import os
            return os.environ[self._var]
        except KeyError:
            import logging
            logging.info("Using default value '{}' for environment variable {}".format(self._default, self._var))
            return self._default
