from taobao_open.api.base import RestApi


class TbkDgCpaActivityReportRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.biz_date = None
        self.event_id = None
        self.page_no = None
        self.page_size = None
        self.pid = None
        self.query_type = None
        self.relation_id = None

    def getapiname(self):
        return 'taobao.tbk.dg.cpa.activity.report'
