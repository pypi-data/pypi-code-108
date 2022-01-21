import datetime
import json


class Log:

    def __init__(self):
        pass

    @classmethod
    def __to_json(cls, data):
        return json.dumps(data,
                          default=lambda o: o.__dict__ if hasattr(o, '__dict__') and len(
                              o.__dict__) > 0 else o.__str__())

    @classmethod
    def __log(cls, level, message, input_data):
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
        if not (isinstance(message, str)):
            message = cls.__to_json(message)
        if not (isinstance(input_data, str)):
            input_data = cls.__to_json(input_data)
        pattern = '{0} | {1} | {2} | {3}|'.format(current_time, level, message, input_data)
        print(pattern)

    @classmethod
    def info(cls, message, input_data={}):
        cls.__log('Info', message, input_data)

    @classmethod
    def debug(cls, message, input_data={}):
        cls.__log('Debug', message, input_data)

    @classmethod
    def warn(cls, message, input_data={}):
        cls.__log('Warn', message, input_data)

    @classmethod
    def error(cls, message, input_data={}):
        cls.__log('Error', message, input_data)

    @classmethod
    def fatal(cls, message, input_data={}):
        cls.__log('Fatal', message, input_data)
