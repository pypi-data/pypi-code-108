from .abstract_channel import AbstractChannel

try:
    basestring
except NameError:
    basestring = str


class Email(AbstractChannel):

    def __init__(self, subject, sender, recipients):
        self.set_subject(subject)
        self.set_sender(sender)
        self.set_recipients(recipients)

        self.content_subtype = 'plain'
        self.recipients_cc = []
        self.recipients_bcc = []
        self.email_attachments = []

    def set_subject(self, subject):
        self.subject = subject

    def set_sender(self, sender):
        self.sender = sender

    def set_recipients(self, recipients):
        if isinstance(recipients, basestring):
            recipients = [recipients]
        self.recipients = list(recipients)

    def add_recipients(self, recipients):
        if isinstance(recipients, basestring):
            recipients = [recipients]
        self.recipients.extend(list(recipients))

    def set_recipients_cc(self, recipients_cc):
        if isinstance(recipients_cc, basestring):
            recipients_cc = [recipients_cc]
        self.recipients_cc = list(recipients_cc)

    def add_recipients_cc(self, recipients_cc):
        if isinstance(recipients_cc, basestring):
            recipients_cc = [recipients_cc]
        self.recipients_cc.extend(list(recipients_cc))

    def set_recipients_bcc(self, recipients_bcc):
        if isinstance(recipients_bcc, basestring):
            recipients_bcc = [recipients_bcc]
        self.recipients_bcc = list(recipients_bcc)

    def add_recipients_bcc(self, recipients_bcc):
        if isinstance(recipients_bcc, basestring):
            recipients_bcc = [recipients_bcc]
        self.recipients_bcc.extend(list(recipients_bcc))

    def set_html_message(self, html_message):
        self.message = html_message
        self.set_content_subtype('html')

    def set_text_message(self, message):
        self.message = message
        self.set_content_subtype('plain')

    def set_message(self, message, content_subtype):
        self.message = message
        self.set_content_subtype(content_subtype)

    def set_content_subtype(self, content_subtype):
        self.content_type = content_subtype

    def add_attachment(self, filename, content, content_type):
        attachment = (filename, content, content_type)
        self.email_attachments.append(attachment)

    def notif_type(self):
        return 'EMAIL_NOTIFICATION'

    def json(self):
        return {
            'subject': self.subject,
            'body': self.message,
            'sender': self.sender,
            'recipient': self.recipients,
            'cc': self.recipients_cc,
            'bcc': self.recipients_bcc,
            'contentSubtype': self.content_type
        }

    def attachments(self):
        return self.email_attachments
