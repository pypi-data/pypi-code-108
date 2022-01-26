from requests.auth import AuthBase  # type: ignore


class BearerAuth(AuthBase):
    def __init__(self, access_token=None):
        self.access_token = access_token

    def __call__(self, req):
        if self.access_token:
            req.headers['Authorization'] = 'Bearer ' + self.access_token
        return req
