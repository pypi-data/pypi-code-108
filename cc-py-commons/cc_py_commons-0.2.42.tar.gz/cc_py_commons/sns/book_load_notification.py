import json

from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils.logger import logger

class BookLoadNotification:

  def __init__(self, app_config):
    self._app_config = app_config

  def send(self, load_id, user_id):
    message = '{' + f'"userId" : {user_id}, ' \
                    f'"loadId": "{load_id}", ' \
                    f'"subject" : "{self._app_config.BOOK_LOAD_SNS_SUBJECT}", ' \
                    f'"className":  "{self._app_config.BOOK_LOAD_SNS_CLASS_NAME}"' + '}'
    logger.debug(f"sending BookLoadNotification {message} to {self._app_config.BOOK_LOAD_SNS_TOPIC_ARN}")

    try:
      sns_service = SnsService()
      sns_service.send(self._app_config.BOOK_LOAD_SNS_TOPIC_ARN,
        self._app_config.BOOK_LOAD_SNS_SUBJECT, message)
    except Exception as e:
      logger.exception(f"failed to send message to {self._app_config.BOOK_LOAD_SNS_TOPIC_ARN}: {message} - {e}", e)
