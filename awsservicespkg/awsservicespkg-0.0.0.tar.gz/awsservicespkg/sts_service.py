import sys

from botocore.config import Config

from awsservicespkg.utils import constants


class STSService:
    # Instantiate STS service
    def __init__(self, _logger, session, aws_region):
        try:
            self.sts_client = session.client('sts', region_name=aws_region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('STS client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while creating STS client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def get_account_id(self):
        try:
            account_id = self.sts_client.get_caller_identity()["Account"]
            self.logger.info('Account id: {}'.format(account_id))
            return account_id
        except Exception as e:
            self.logger.exception(e)
            print("Error while retrieving account id. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)
