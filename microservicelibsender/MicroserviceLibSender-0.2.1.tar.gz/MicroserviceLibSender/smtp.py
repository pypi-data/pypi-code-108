import requests


class SenderSMTPClient:
    def __init__(self, dsn: str, secret_key: str, project_id: str, content_type: str = 'html'):
        self.dsn = dsn
        self.secret_key = secret_key
        self.project_id = project_id
        self.content_type = content_type

        self.headers = {
            'X-Secret-Key': self.secret_key,
            'X-Project-ID': self.project_id,
        }

    def get_response(self, response):
        pass

    def send(self, subject: str, message: str, to: str):
        message = {
            'subject': subject,
            'message': message,
            'to': to,
            'content-type': self.content_type,
        }
        response = requests.post(self.dsn, headers=self.headers, json=message, verify=False, timeout=10)
        # {"id":"47cd99bf-c5cd-11ea-8a39-76133ed1bebd"}
        return response.json()
