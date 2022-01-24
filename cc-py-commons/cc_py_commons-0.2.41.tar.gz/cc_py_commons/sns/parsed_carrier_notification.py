import json

from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils.logger import logger

class ParsedCarrierNotification:

  def __init__(self, app_config):
    self._app_config = app_config

  def send(self, parsed_carrier, c4_account_id, import_stats_id):
    message = {
      'accountId': c4_account_id,
      'parsedCarrier': parsed_carrier,
      'importStatsId': import_stats_id,
      'subject' : f'{self._app_config.PARSED_CARRIER_SNS_SUBJECT}', 
      'className': f'{self._app_config.PARSED_CARRIER_SNS_CLASS_NAME}'
    }
    logger.debug(f"sending message {message} to {self._app_config.PARSED_CARRIER_SNS_TOPIC_ARN}")

    sns_service = SnsService()
    sns_service.send(self._app_config.PARSED_CARRIER_SNS_TOPIC_ARN,
      self._app_config.PARSED_CARRIER_SNS_SUBJECT, json.dumps(message))
