from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
import pytest


class TestDiscountOperations:

    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server.stop()

    def test_ListDiscounts(self):
        airtimeAPI = AirtimeAPI(clientId=AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrl = airtimeAPI.baseUrl
        request = airtimeAPI.discounts().List_without_filter()
        assert request!=None
        self.assertIsValidDiscount(request)

    def test_GetByOperatorId(self):
        airtimeAPI = AirtimeAPI(clientId=AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrl = airtimeAPI.baseUrl
        operatorId = 174
        request = airtimeAPI.discounts().getByOperatorId(operatorId)
        assert request!=None
        self.assertIsValidDiscount(request)

    def test_GetByOperatorIdShouldThrowExceptionWhenOperatorIdIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId=self.clientId, clientSecret=self.clientSecret)
            a = airtimeAPI.discounts().getByOperatorId(None)

    def assertIsValidDiscount(self, discount):
        discountFields = [
            "percentage", "internationalPercentage", "localPercentage", 
            "updatedAt", "operator"
            ]

        for i in discount:
            count = 0
            for j in i:
                if type(j)==str:
                    assert j!=None
                elif type(j)==dict:
                    assert j[discountFields[count]]!=None
                count = count + 1






