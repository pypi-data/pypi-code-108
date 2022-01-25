from taobao_open.api.base import RestApi


class TbkDgVegasSendStatusRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.device_type = None
        self.device_value = None
        self.pid = None
        self.relation_id = None
        self.special_id = None
        self.thor_biz_code = None

    def getapiname(self):
        return 'taobao.tbk.dg.vegas.send.status'
