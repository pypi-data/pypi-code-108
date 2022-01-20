from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
import pytest
import json

class TestCountryOperations():

    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server.stop()

    def test_ListCountries(self):
        self.baseUrlField = AirtimeAPI(clientId=AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret).baseUrl
        request = AirtimeAPI(clientId=AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret).countries().getByCode('HT')
        assert request!=None
        self.assertIsValidCountry(request)

    def test_GetByCodeShouldThrowExceptionWhenCountryCodeIsNull(self):
        with pytest.raises(Exception):
            self.airtimeAPI = AirtimeAPI(accessToken=AirtimeAPIMockServer().accessToken).countries().getByCode(None)

    def assertIsValidCountry(self, country):
        isoName = country["isoName"]
        name = country["name"]
        currencyCode = country["currencyCode"]
        currencyName = country["currencyName"]
        currencySymbol = country["currencySymbol"]
        flag = country["flag"]
        callingCodes = country["callingCodes"]
        assert isoName!=None
        assert name!=None
        assert currencyCode!=None
        assert currencyName!=None
        assert currencySymbol!=None
        assert flag!=None
        assert callingCodes!=None