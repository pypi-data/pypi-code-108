from taobao_open.api.base import RestApi


class TbkRebateOrderGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.fields = None
        self.start_time = None
        self.span = None
        self.page_no = None
        self.page_size = None

    def getapiname(self):
        return 'taobao.tbk.rebate.order.get'
