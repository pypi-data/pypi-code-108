import requests


class RestConfException(Exception):
    """
    Raise when a error is returned by Restconf
    """

    def __init__(self, status_code, error_tag=None, error_message=None, error_type=None, error_path=None):
        super().__init__()
        self.error_message = error_message
        self.error_tag = error_tag
        self.error_type = error_type
        self.error_path = error_path
        self.status_code = status_code

    def __str__(self):
        ret = f"status_code: {self.status_code}"
        if self.error_tag:
            ret += f"\nerror-tag: {self.error_tag}"
        if self.error_message:
            ret += f"\nerror-message: {self.error_message}"
        if self.error_type:
            ret += f"\nerror-type: {self.error_type}"
        if self.error_path:
            ret += f"\nerror-type: {self.error_path}"
        return ret

    def to_dict(self):
        ret = dict()
        ret['status-code'] = self.status_code
        if self.error_tag:
            ret['error-tag'] = self.error_tag
        if self.error_message:
            ret['error-message'] = self.error_message
        if self.error_type:
            ret['error-type'] = self.error_type
        if self.error_path:
            ret['error-path'] = self.error_path
        return ret


class RestConfNotFoundException(RestConfException):
    """
    Raise when a error "not found" is returned by Restconf.
    The error details may be empty when the request is correct but the node is not found
    """
    pass


class RestConf(object):
    Root = '/restconf/'
    BasePath = '/restconf/data/'
    ActionPath = '/restconf/operations/'
    QueryBase = '/restconf/tailf/query/'
    Accept = [
        'application/yang-data+json',
        'application/yang-errors+json',
    ]
    ContentType = 'application/yang-data+json'

    def __init__(self, address="localhost", port=8080, username=None, password=None):
        self.port = port
        self.address = address
        self.username = username
        self.password = password
        self._host = f"{self.address}:{self.port}"

    def build_session(self):
        session = requests.Session()
        if self.username is not None and self.password is not None:
            session.auth = (self.username, self.password)
        session.headers.update({
            'Accept': ','.join([
                accept for accept in self.Accept
            ]),
            'Content-Type': self.ContentType,
        })
        return session

    def action(self, data, endpoint, query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.ActionPath + endpoint
        res = session.post(url, data=data, params=query_params)
        return res

    def query(self, data, endpoint, query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.QueryBase + endpoint
        res = session.post(url, data=data, params=query_params)
        return res

    def put(self, data, endpoint, query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.BasePath + endpoint
        res = session.put(url, data=data, params=query_params)
        return res

    def post(self, data, endpoint, query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.BasePath + endpoint
        res = session.post(url, data=data, params=query_params)
        return res

    def patch(self, data, endpoint, query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.BasePath + endpoint
        res = session.patch(url, data=data, params=query_params)
        return res

    def get_root(self):
        session = self.build_session()
        url = self._host + self.Root
        res = session.get(url)
        return res

    def get(self, endpoint='', content='config', query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.BasePath + endpoint
        if not query_params and content:
            query_params = {'content': content}
        elif query_params and content:
            query_params['content'] = content
        res = session.get(url, params=query_params)
        return res

    def delete(self, endpoint, query_params=None):
        session = self.build_session()
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        url = self._host + self.BasePath + endpoint
        res = session.delete(url, params=query_params)
        return res

    @staticmethod
    def parse_error(res):
        if res.status_code == 404:
            exception = RestConfNotFoundException(status_code=404)
        else:
            exception = RestConfException(status_code=res.status_code)
        if len(res.text) > 0:
            jres = res.json()
            error = jres['ietf-restconf:errors']['error']
            if len(error) > 1:
                raise Exception(f"More than one error return when parsing restconf error. Returned: {res.text}")
            error = error[0]
            exception.error_tag = error['error-tag']
            if 'error-type' in error:
                exception.error_type = error['error-type']
            if 'error-message' in error:
                exception.error_message = error['error-message']
            if 'error-path' in error:
                exception.error_path = error['error-path']

        return exception
