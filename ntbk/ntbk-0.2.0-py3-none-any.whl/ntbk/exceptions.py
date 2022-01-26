"""Custom exceptions for the application"""

class InvalidConfigException(Exception):
    """Exception that is thrown if the configuration file is not valid"""

    def __init__(self):
        super().__init__('Configuration file is not valid. \
            Please review the docs and check your config file.')
    