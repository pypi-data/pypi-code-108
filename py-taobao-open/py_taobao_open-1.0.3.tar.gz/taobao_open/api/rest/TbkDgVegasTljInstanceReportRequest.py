from taobao_open.api.base import RestApi


class TbkDgVegasTljInstanceReportRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.rights_id = None

    def getapiname(self):
        return 'taobao.tbk.dg.vegas.tlj.instance.report'
