import json

from cc_py_commons.sns.sns_service import SnsService

class ImportMovementsNotification:

  def __init__(self, app_config):
    self._app_config = app_config

  def send(self, mcleod_token, c4_account_id, company_id):
    message = '{' + f'"accountId" : {c4_account_id}, ' \
                    f'"mcleodToken" : "{mcleod_token}", ' \
                    f'"companyId": "{company_id}", ' \
                    f'"subject" : "{self._app_config.IMPORT_MOVEMENTS_SNS_SUBJECT}", ' \
                    f'"className":  "{self._app_config.IMPORT_MOVEMENTS_SNS_CLASS_NAME}"' + '}'
    sns_service = SnsService()
    sns_service.send(self._app_config.IMPORT_MOVEMENTS_SNS_TOPIC_ARN,
      self._app_config.IMPORT_MOVEMENTS_SNS_SUBJECT, message)
