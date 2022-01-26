
from bank_sync.APIs.api_format import API
import json
from bank_sync.APIs.utils.generate_code import get_code


class Resource(API):

    _bank_id = None

    _operation = None

    _user_id = None

    _response = {}

    _read_url = ""

    _api = None

    _resource_id = -1

    COOP = 1
    EQUITY = 2
    NCBA = 3

    @property
    def READ(self):
        return 0

    @property
    def BALANCE(self):
        return 0

    @property
    def MINI_STATEMENT(self):
        return 1

    @property
    def FULL_STATEMENT(self):
        return 2

    @property
    def ACCOUNT_VALIDATION(self):
        return 3

    @property
    def ACCOUNT_TRANSACTIONS(self):
        return 4

    @property
    def IFT(self):
        return 5

    @property
    def TRANSACTION_STATUS(self):
        return 6

    @property
    def MOBILE_WALLET(self):
        return 7

    @property
    def PESALINK_TO_BANK(self):
        return 8

    @property
    def PESALINK_TO_MOBILE(self):
        return 9

    @property
    def RTGS(self):
        return 10

    @property
    def SWIFT(self):
        return 11

    @property
    def EFT(self):
        return 12

    def set_operation(self, operation):
        self._operation = operation
        return self

    def set_bank_id(self, bank_id):
        self._bank_id = bank_id
        return self

    def set_user_id(self, user_id):
        self._user_id = user_id
        return self

    def set_urls(self, urls):
        self.set_read_url(urls.get("read", ""))
        return self

    def read(self, payload=None, method='POST', endpoint=None):
        if endpoint is None:
            endpoint = self.get_read_url()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint)
        return self

    def payload(self):
        return {}

    def serialize(self):
        return self

    def response(self):
        return self._response

    def set_response(self, response={}):
        self._response = response
        return self

    def set_read_url(self, read_url):
        self._read_url = read_url
        return self

    def get_read_url(self):
        return self._read_url

    def get_bank_id(self):
        return self._bank_id

    def get_user_id(self):
        return self._user_id

    def generate_code(self, length=6):
        return get_code(length)

    def get_operation(self):
        return self._operation

    # This is the method that will be called execute an A.P.I. request.
    # Since most of the A.P.I. calls methods are similar, they are to be placed inside this method to avoid code duplication.
    #
    # It will only accept parameters unique to each A.P.I. request.
    def _exec(self, payload=None, method='POST', endpoint="", files=None):

        # NCBA send data back to our callback as XML converted to bytes
        if isinstance(payload,bytes):
            payload = payload.decode("utf-8")

        if files is None:
            payload = json.dumps(payload)
        else:
            payload = payload

        # Call the iPay A.P.I. url by passing the variables to the super class method responsible for making requests to A.P.I. endpoints
        # The super class method returns a response that is returned by this method
        return super().api_request(url=f"{super().get_base_url()}{endpoint}", payload=payload, method=method, files=files)
