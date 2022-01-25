from taobao_open.api.base import RestApi


class TbkDgOptimusPromotionRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.adzone_id = None
        self.page_num = None
        self.page_size = None
        self.promotion_id = None

    def getapiname(self):
        return 'taobao.tbk.dg.optimus.promotion'
