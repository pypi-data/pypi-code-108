from bank_sync.Resources.banks import Bank
from bank_sync.Resources.resource import Resource


class Nash(Resource):

    _headers = {
        'Content-Type': 'application/json'
    }

    _params = {}

    _response = {}

    _is_logged_in = False

    _bank = None

    _access_token = None

    _user_id = -1

    def __init__(self):
        super().__init__("NashAPI", self._headers, self._params)

    def login(self, payload=None, method='POST', endpoint="/auth/login"):
        # authenticate and provide user credentials
        # set response here

        self._is_logged_in = True

        return self

    def sign_up(self, payload=None, method='POST', endpoint="/users", log_in_user=True):
        # authenticate and provide user credentials
        # set response here

        self.login(payload={"username": payload.get(
                    "username"), "password": payload.get("password")}).response()

        return self

    def bank(self, bank_id=None):

        if self._bank is None:
            self._bank = Bank(self, bank_id)

        return self._bank

    # def user(self):
    #     return Users(self)

    def is_logged_in(self):
        return self._is_logged_in

    def _set_access_token(self, access_token):
        self._access_token = access_token
        return self

    def get_access_token(self):
        return self._access_token
