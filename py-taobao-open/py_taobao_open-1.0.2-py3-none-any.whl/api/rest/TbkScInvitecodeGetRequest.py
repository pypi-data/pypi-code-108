from taobao_open.api.base import RestApi


class TbkScInvitecodeGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.code_type = None
        self.relation_app = None
        self.relation_id = None

    def getapiname(self):
        return 'taobao.tbk.sc.invitecode.get'
