from taobao_open.api.base import RestApi


class OpenAccountCreateRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.param_list = None

    def getapiname(self):
        return 'taobao.open.account.create'
