from reloadly_airtime.airtime.sdk.operation.BaseAirtimeOperation import BaseAirtimeOperation
import reloadly_core.core.internal.dto.request.interfaces.Request as Request

class AccountOperations(BaseAirtimeOperation):
    END_POINT = '/accounts'
    PATH_BALANCE = '/balance'
    def __init__(self, client, baseUrl : str, apiToken : str):
        self.baseUrl = baseUrl + self.END_POINT + self.PATH_BALANCE
        self.client = client
        self.apiToken = apiToken
        super().__init__(self.client, self.baseUrl, self.apiToken)
    

    def getBalance(self):
        a = super().createGetRequest(self.baseUrl)
        if "errorCode" in a:
            raise Exception("Invalid access token")
        return a
