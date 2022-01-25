from taobao_open.api.base import RestApi


class TbkActivityInfoGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.activity_material_id = None
        self.adzone_id = None
        self.relation_id = None
        self.sub_pid = None
        self.union_id = None

    def getapiname(self):
        return 'taobao.tbk.activity.info.get'
