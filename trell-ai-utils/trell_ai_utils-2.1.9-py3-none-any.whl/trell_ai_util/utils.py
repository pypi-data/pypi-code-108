import os
import json
import logging
import traceback
from datetime import datetime


class LogFormatter(logging.Formatter):
    """Log Formatter class for trell ai usage"""

    __date_format = '%d/%b/%Y:%H:%M:%S %Z'

    @staticmethod
    def apply():
        """
        Start logging in json format.
        :return:
        """
        trell_ai_json_log_format = {
            'ts': '%(asctime)s',
            'level': '%(levelname)s',
            'location': '%(pathname)s:%(lineno)d',
            'msg': '%(message)s'
        }
        log_format = json.dumps(trell_ai_json_log_format)
        logging.basicConfig(format=log_format, level=logging.INFO, datefmt=LogFormatter.__date_format)
        if len(logging.root.handlers) > 0:
            logging.root.handlers[0].setFormatter(LogFormatter(fmt=log_format,
                                                                      datefmt=LogFormatter.__date_format))

    def formatException(self, execution_info):
        """
        Handle logging in case of exceptions.
        :param execution_info:
        :return:
        """
        stacktrace = super(LogFormatter, self).formatException(execution_info)
        record = {
            'message': stacktrace,
            'levelname': 'EXCEPTION',
            'pathname': 'stacktrace in msg',
            'lineno': -1
        }
        try:
            record['asctime'] = datetime.now().strftime(LogFormatter.__date_format)
            return self._fmt % record
        except Exception as err:
            return repr(stacktrace)


class Credential:
    """ sets aws access key and secret key as environment variables """

    def set(ACCESS_KEY, SECRET_KEY):

        """
        sets aws access key and secret key as environment variables
        :param string ACCESS_KEY:  this is aws_access_key_id 
        :param string SECRET_KEY: this is aws_secret_access_key
        :return None
        """

        try:
            os.environ["ACCESS_KEY"] = ACCESS_KEY
            os.environ["SECRET_KEY"] = SECRET_KEY
            print("----- Environment Variables set successfully -----")
        except:
            print(" Something went wrong while setting environment variables")
            traceback.print_exc()
        