from taobao_open.api.base import RestApi


class TradeConfirmfeeGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.tid = None

    def getapiname(self):
        return 'taobao.trade.confirmfee.get'
