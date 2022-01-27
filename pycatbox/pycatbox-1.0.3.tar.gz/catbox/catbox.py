import requests, typing


class Uploader():
    def __init__(self,
                 token: typing.Union[str] = ''):
        self.token = token
        self.apiUrl = 'https://catbox.moe/user/api.php'

    def upload(self, file_type: typing.Union[str] = None, file_raw: typing.Union[bytes] = None):
        with requests.Session() as session:
            files = {
                'reqtype': (None, 'fileupload'),
                'userhash': (None, self.token),
                'fileToUpload': (f'file.{file_type}', file_raw),
            }

            response = session.post('https://catbox.moe/user/api.php', files=files)

            return {
                'code': response.status_code,
                'file': response.text
            }
    def moreUploader(self, ):
        pass









