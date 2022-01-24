
from .abstract_channel import AbstractChannel


class UserPushNotification(AbstractChannel):

    def __init__(
        self, recipient_email, engagement_type, title, body, object_id, url=None, tag=None, data=None,
        message_template=None, message_entity=None
    ):
        self.set_recipient_email(recipient_email)
        self.set_engagement_type(engagement_type)
        self.set_title(title)
        self.set_body(body)
        self.set_object_id(object_id)

        if url is not None:
            self.set_url(url)
        if tag is not None:
            self.set_tag(tag)
        if data is not None:
            self.set_data(data)
        if message_template is not None:
            self.set_message_template(message_template)
        if message_entity is not None:
            self.set_message_entity(message_entity)

    def set_recipient_email(self, email):
        self.email = email

    def set_engagement_type(self, engagement_type):
        self.engagement_type = engagement_type

    def set_title(self, title):
        self.title = title

    def set_body(self, body):
        self.body = body

    def set_object_id(self, object_id):
        self.object_id = object_id

    # optional
    def set_url(self, url):
        self.url = url

    # optional
    def set_tag(self, tag):
        self.tag = tag

    # optional
    def set_data(self, data):
        self.data = data

    # optional
    def set_message_template(self, message_template):
        self.message_template = message_template

    # optional
    def set_message_entity(self, message_entity):
        self.message_entity = message_entity

    def json(self):
        payload = dict()
        payload['recipientEmail'] = self.email
        payload['engagementType'] = self.engagement_type
        payload['title'] = self.title
        payload['body'] = self.body
        payload['objectId'] = self.object_id

        # optional payload
        url = getattr(self, 'url', None)
        tag = getattr(self, 'tag', None)
        data = getattr(self, 'data', None)
        message_template = getattr(self, 'message_template', None)
        message_entity = getattr(self, 'message_entity', None)

        if url is not None:
            payload['url'] = url
        if tag is not None:
            payload['tag'] = tag
        if data is not None:
            payload['data'] = data
        if message_template is not None:
            payload['messageTemplate'] = message_template
        if message_entity is not None:
            payload['messageEntity'] = message_entity

        return payload

    def notif_type(self):
        return 'USER_PUSH_NOTIFICATION'

    def attachments(self):
        return []
