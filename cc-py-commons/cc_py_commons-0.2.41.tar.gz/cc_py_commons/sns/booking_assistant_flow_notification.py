import json

from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils.logger import logger

class BookingAssistantFlowNotification:

  def __init__(self, app_config):
    self._app_config = app_config

  def send(self, user_id, load, params):
    message = {
      'userId': user_id,
      'loadDTO': load,
      'payload': params,
      'subject': f'{self._app_config.BOOKING_ASSISTANT_SNS_SUBJECT}',
      'className': f'{self._app_config.BOOKING_ASSISTANT_SNS_CLASS_NAME}'
    }
    logger.debug(f"sending messsage {message} to {self._app_config.BOOKING_ASSISTANT_SNS_TOPIC_ARN}")

    try:
      sns_service = SnsService()
      sns_service.send(self._app_config.BOOKING_ASSISTANT_SNS_TOPIC_ARN,
        self._app_config.BOOKING_ASSISTANT_SNS_SUBJECT, json.dumps(message))
    except Exception as e:
      logger.error(f"failed to send BookingAssistantFlowNotification message: {e}")
      logger.error(f"BookingAssistantFlowNotification message: {message}")
