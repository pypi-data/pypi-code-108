from taobao_open.api.base import RestApi


class ProductGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.cid = None
        self.fields = None
        self.product_id = None
        self.props = None

    def getapiname(self):
        return 'taobao.product.get'
