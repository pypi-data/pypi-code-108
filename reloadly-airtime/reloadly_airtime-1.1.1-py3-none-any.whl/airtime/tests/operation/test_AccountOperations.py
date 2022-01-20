from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
from reloadly_auth.authentication.client.AuthenticationAPI import AuthenticationAPI
from reloadly_core.core.enums.Service import Service
from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
import pytest

class TestAccountOperations():
    
    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server.stop()

    def test_GetAccountBalance(self):
        airtimeAPI = AirtimeAPI(clientId=AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer.clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.accounts().getBalance()
        assert request!=None
        accountBalance = request
        assert type(accountBalance)==dict
        self.assertIsValidAccountBalance(request)

    def test_shouldThrowExceptionWhenProvidedAccessTokenIsInvalid(self):
        with pytest.raises(Exception):
            AccountBalance = AirtimeAPI(accessToken="abcd").accounts().getBalance()

    def assertIsValidAccountBalance(self, accountBalance):
        assert accountBalance["balance"]!=None
        assert accountBalance["currencyCode"]!=None
        assert accountBalance["currencyName"]!=None
        assert accountBalance["updatedAt"]!=None
        
        