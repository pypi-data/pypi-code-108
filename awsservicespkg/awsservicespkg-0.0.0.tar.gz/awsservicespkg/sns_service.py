import sys
from botocore.config import Config
from awsservicespkg.utils import constants


class SNSService:
    # Instantiate SNS service
    def __init__(self, _logger, session, region):
        try:
            sns_client = session.client('sns', region_name=region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.sns_client = sns_client
            self.logger.info('SNS Client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while creating SNS client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def publish_email(self, topic_arn, subject, message):
        try:
            self.sns_client.publish(TopicArn=topic_arn, Subject=subject, Message=message)
            self.logger.info('Email notification sent successfully')
        except Exception as e:
            self.logger.exception(e)
            print("Error while publishing email to given topicARN: " + str(topic_arn) + ". Please refer to the log "
                                                                                        "file at- "
                  + constants.logger_path)
            sys.exit(1)
