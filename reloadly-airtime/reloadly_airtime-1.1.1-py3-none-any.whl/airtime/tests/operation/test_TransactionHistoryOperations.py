from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
from reloadly_core.core.internal.Filter.TransactionHistoryFilter import TransactionHistoryFilter
import pytest


class TestTransactionHistoryOperations:
    
    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server = None

    def test_ListTransactionHistoryWithNoFilters(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        request = airtimeAPI.reports().transactionHistory().List_without_filter()
        assert request!=None
        self.assertIsValidTransactionHistory(request)

    def test_ListTransactionHistoryWithFilters(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        page = 1
        pageSize = 2
        Filter = TransactionHistoryFilter().withPage(page, pageSize)
        request = airtimeAPI.reports().transactionHistory().List_with_filter(Filter)
        assert request!=None
        self.assertIsValidTransactionHistory(request)
    
    def test_GetById(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        transactionId = 10657
        request = airtimeAPI.reports().transactionHistory().getById(transactionId)
        assert request!=None
        self.assertIsValidTransactionHistory(request)

    def test_GetByIdShouldThrowExceptionWhenTransactionIdIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            transactionId = None
            request = airtimeAPI.reports().transactionHistory().getById(transactionId)
    
    def test_GetByOperatorIdShouldThrowExceptionWhenOperatorIdIsLessThanZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            transactionId = -2342
            request = airtimeAPI.reports().transactionHistory().getById(transactionId)
    
    def test_GetByOperatorIdShouldThrowExceptionWhenOperatorIdIsEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            transactionId = 0
            request = airtimeAPI.reports().transactionHistory().getById(transactionId)

    def assertIsValidTransactionHistory(self, transactionHistory):
        topupTransactionFields = ["id", "operatorTransactionId", "customIdentifier",
                "recipientPhone", "recipientEmail", "senderPhone", "countryCode", "operatorId", "operatorName",
                "discount", "discountCurrencyCode", "requestedAmount", "requestedAmountCurrencyCode",
                "deliveredAmount", "deliveredAmountCurrencyCode", "date", "pinDetail"]

        for i in transactionHistory:
            count = 0
            for j in i:
                if type(j)==str:
                    assert j!=None
                elif type(j)==dict:
                    assert j[topupTransactionFields[count]]!=None
                count = count + 1
        
