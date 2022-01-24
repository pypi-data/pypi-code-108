
from .abstract_channel import AbstractChannel

from builtins import int

try:
    basestring
except NameError:
    basestring = str


class CustomerIO(AbstractChannel):

    timeout = 10

    def __init__(self, campaign_id, data, additional_recipient_emails=[]):
        self.set_campaign_id(campaign_id)
        self.set_additional_recipient_emails(additional_recipient_emails)
        self.set_data(data)

    def set_campaign_id(self, campaign_id):
        if not isinstance(campaign_id, int):
            raise ValueError('campaign id have to be an integer')
        self.campaign_id = campaign_id

    def set_data(self, data):
        if not isinstance(data, dict):
            raise ValueError('data have to be a dicionary')
        self.data = data

    def set_data_key(self, key, value):
        if not isinstance(key, basestring):
            raise ValueError('key have to be a string')
        self.data[key] = value

    def set_additional_recipient_emails(self, additional_recipient_emails):
        if not isinstance(additional_recipient_emails, (list,)):
            additional_recipient_emails = [additional_recipient_emails]
        self.additional_recipient_emails = additional_recipient_emails

    def json(self):
        payload = dict()
        payload['campaignId'] = self.campaign_id
        payload['data'] = self.data
        payload['additionalEmails'] = self.additional_recipient_emails
        return payload

    def attachments(self):
        return []

    def notif_type(self):
        return 'CUSTOMERIO_NOTIFICATION'
