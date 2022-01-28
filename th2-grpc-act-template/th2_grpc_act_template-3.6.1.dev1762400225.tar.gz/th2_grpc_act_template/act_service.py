from . import act_template_pb2_grpc as importStub

class ActService(object):

    def __init__(self, router):
        self.connector = router.get_connection(ActService, importStub.ActStub)

    def placeOrderFIX(self, request, timeout=None):
        return self.connector.create_request('placeOrderFIX', request, timeout)

    def placeCancelFIX(self, request, timeout=None):
        return self.connector.create_request('placeCancelFIX', request, timeout)

    def sendMessage(self, request, timeout=None):
        return self.connector.create_request('sendMessage', request, timeout)

    def placeQuoteRequestFIX(self, request, timeout=None):
        return self.connector.create_request('placeQuoteRequestFIX', request, timeout)

    def placeQuoteFIX(self, request, timeout=None):
        return self.connector.create_request('placeQuoteFIX', request, timeout)

    def placeOrderMassCancelRequestFIX(self, request, timeout=None):
        return self.connector.create_request('placeOrderMassCancelRequestFIX', request, timeout)

    def placeQuoteCancelFIX(self, request, timeout=None):
        return self.connector.create_request('placeQuoteCancelFIX', request, timeout)

    def placeQuoteResponseFIX(self, request, timeout=None):
        return self.connector.create_request('placeQuoteResponseFIX', request, timeout)

    def placeSecurityStatusRequest(self, request, timeout=None):
        return self.connector.create_request('placeSecurityStatusRequest', request, timeout)