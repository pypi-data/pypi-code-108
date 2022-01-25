import sys

import boto3

from awsservicespkg.utils import constants


class Session:
    # Instantiate Boto3 session
    def __init__(self, _logger, aws_access_key, aws_secret_access_key, aws_session_token):
        try:
            self.session = boto3.Session(aws_access_key_id=aws_access_key,
                                         aws_secret_access_key=aws_secret_access_key,
                                         aws_session_token=aws_session_token)
        except Exception as e:
            _logger.exception(e)
            print("Error while creating boto3 session. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def getSession(self):
        return self.session
