from taobao_open.api.base import RestApi


class TbkDgVegasSendReportRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.activity_id = None
        self.biz_date = None
        self.page_no = None
        self.page_size = None
        self.relation_id = None

    def getapiname(self):
        return 'taobao.tbk.dg.vegas.send.report'
