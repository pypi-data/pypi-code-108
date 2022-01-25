import sys

from botocore.config import Config

from awsservicespkg.utils import constants


class IAMService:
    def __init__(self, _logger, session, region):
        try:
            self.iam_client = session.client('iam', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('IAM client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while initializing IAM client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_iam_role_arn(self, role_name):
        try:
            iam_role_info = self.iam_client.get_role(RoleName=role_name)
            iam_role_arn = iam_role_info['Role']['Arn']
            self.logger.info('IAM role ARN for role name- {} is {}'.format(role_name, iam_role_arn))
            return iam_role_arn
        except Exception as e:
            self.logger.exception(e)
            print("Error while getting IAM role ARN for role name- {}. Please refer to the log file at- ".format(role_name) + constants.logger_path)
            sys.exit(1)
