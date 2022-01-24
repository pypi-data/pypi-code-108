from .abstract_channel import AbstractChannel

try:
    basestring
except NameError:
    basestring = str

class CreateGroupWhatsapp(AbstractChannel):

    def __init__(self, subject):
        self.set_subject(subject)

    def set_subject(self, subject):
        if not isinstance(subject, basestring):
            raise ValueError('subject have to be string')
        self.subject = subject

    def json(self):
        payload = dict()
        payload['subject'] = self.subject
        return payload

    def notif_type(self):
        return 'CREATE_GROUP_WHATSAPP'

    def attachments(self):
        return []