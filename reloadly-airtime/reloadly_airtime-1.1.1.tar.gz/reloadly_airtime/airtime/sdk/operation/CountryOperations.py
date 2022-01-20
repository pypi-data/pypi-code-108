from reloadly_airtime.airtime.sdk.operation.BaseAirtimeOperation import BaseAirtimeOperation
from reloadly_core.core.internal.dto.request.interfaces.Request import Request
from reloadly_core.core.internal.util.Asserter import Asserter
import json

class CountryOperations(BaseAirtimeOperation):
    END_POINT = "countries"
    def __init__(self, client, baseUrl : str, apiToken : str):
        self.client = client
        self.baseUrl = baseUrl
        self.apiToken = apiToken
        super().__init__(self.client, self.baseUrl, self.apiToken)

    def List(self):
        r = self.createGetRequest(super().getBuilder(self.END_POINT))
        if type(r)==dict:
            if r['errorCode']=='INVALID_TOKEN': 
                raise Exception("Invalid token provided")
        return r

    def getByCode(self, countryCode):
        Asserter().assertNotNull(countryCode, " Country code")
        return super().createGetRequest(super().getBuilder(self.END_POINT + "/" + str(countryCode)))