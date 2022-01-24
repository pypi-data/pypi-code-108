
from .abstract_channel import AbstractChannel


class ProjectPushNotification(AbstractChannel):

    def __init__(self, project_key, event_type, title, body, data, url=None):
        self.set_project_key(project_key)
        self.set_event_type(event_type)
        self.set_title(title)
        self.set_body(body)
        self.set_data(data)
        if url is not None:
            self.set_url(url)

    def set_project_key(self, project_key):
        self.project_key = project_key

    def set_event_type(self, event_type):
        self.event_type = event_type

    def set_title(self, title):
        self.title = title

    def set_body(self, body):
        self.body = body

    def set_data(self, data):
        self.data = data

    def set_url(self, url):
        self.url = url

    def json(self):
        payload = dict()
        payload['projectKey'] = self.project_key
        payload['eventType'] = self.event_type
        payload['title'] = self.title
        payload['body'] = self.body
        payload['data'] = self.data
        if hasattr(self, 'url'):
            payload['url'] = self.url
        return payload

    def notif_type(self):
        return 'PROJECT_PUSH_NOTIFICATION'

    def attachments(self):
        return []
