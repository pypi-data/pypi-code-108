import pprint

class ServerError(RuntimeError):
    def __init__(self, code, msg, resp):
        super().__init__(f'({code}) {msg}')
        self.code = code
        self.msg = msg
        self.resp = resp

class RemoteCallError(RuntimeError):
    def __init__(self, server, resp):
        super().__init__(resp['exc_str'])
        self.exc_str = resp['exc_str']
        self.exc_type = resp['exc_type']
        self.traceback = resp['traceback']
        self.formatted = resp['formatted']
        self.server = server

    def __str__(self):
        return f'from {self.server}\nRemote Traceback (most recent call last):\n' + ''.join(self.formatted)

def json_or_err(resp):
    try:
        obj = resp.json
        if callable(obj):
            obj = obj()
    except Exception as e:
        raise ServerError(500, f'Server did not return JSON: {resp.data}', resp)

    if resp.status_code != 200:
        raise ServerError(resp.status_code, obj.get('err', obj), resp)

    return obj



