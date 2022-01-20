from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
from reloadly_core.core.internal.Filter.OperatorFilter import OperatorFilter
import pytest

class TestOperatorOperations:

    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server = None

    def test_ListOperatorsWithNoFilters(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrl = airtimeAPI.baseUrl
        request = airtimeAPI.operators().List_without_filter()
        assert request!=None
        
    def test_ListOperatorsWithFilters(self):
        page = 1
        pageSize =5
        Filter = OperatorFilter().withPage(page, pageSize).includePin(True).includeData(True).includeBundles(True).includeSuggestedAmounts(True).includeSuggestedAmountsMap(True)
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.operators().List_with_filter(Filter)
        self.assertIsValidOperator(request)

    def test_ListOperatorsByCountryCodeWithNoFilters(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.operators().listByCountryCode_without_Filters("HT")
        assert request!=None
        self.assertIsValidOperator(request)

    def test_ListOperatorsByCountryCodeWithFilters(self):
        Filter = OperatorFilter().includeBundles(True).includeSuggestedAmountsMap(True)
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.operators().listByCountryCode_with_Filters("HT", Filter)
        assert request!=None
        self.assertIsValidOperator(request)

    def test_GetOperatorIdWithNoFilters(self):
        operatorId = 174
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.operators().getById_without_filter(operatorId)
        assert request!=None
        self.assertIsValidOperator(request)

    def test_GetOperatorIdWithFilters(self):
        operatorId = 174
        Filter = OperatorFilter().includeSuggestedAmountsMap(True)
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.operators().getById_with_filter(operatorId, Filter)
        assert request!=None
        self.assertIsValidOperator(request)

    def test_AutoDetectOperatorWithNoFilters(self):
        phone = "+50936377111"
        countryCode = "HT"
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.operators().autoDetect(phone, countryCode)
        assert request!=None
        self.assertIsValidOperator(request)


    def test_CalculateOperatorFxRate(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        amount = 5.00
        operatorId = 174
        request = airtimeAPI.operators().calculateFxRate(operatorId, amount)
        assert request!=None
        
    def test_CalculateFxRateShouldThrowExceptionWhenOperatorIdIsEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().calculateFxRate(0, 5.00)

    def test_CalculateFxRateShouldThrowExceptionWhenOperatorIdIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().calculateFxRate(None, 5.00)

    def test_CalculateFxRateShouldThrowExceptionWhenAmountIsLessThanZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().calculateFxRate(174, -1)

    def test_CalculateFxRateShouldThrowExceptionWhenAmountIsEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().calculateFxRate(174, 0.00)

    def test_CalculateFxRateShouldThrowExceptionWhenAmountIsEqualToNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().calculateFxRate(174, None)

    def test_AutoDetectOperatorShouldThrowExceptionWhenPhoneIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().autoDetect(None, "CO")

    def test_AutoDetectOperatorShouldThrowExceptionWhenPhoneIsEmpty(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().autoDetect(" ", "CO")

    
    def test_AutoDetectOperatorShouldThrowExceptionWhenCountryCodeIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().autoDetect("50936377111", None)

    def test_GetOperatorByIdShouldThrowExceptionWhenOperatorIdIsLessThanZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().autoDetect("50936377111", -1)

    def test_GetOperatorByIdShouldThrowExceptionWhenOperatorIdIsEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().getById(0)

    def test_GetOperatorByIdShouldThrowExceptionWhenOperatorIdIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().getById(None)

    def test_GetOperatorByCountryCodeShouldThrowExceptionWhenCountryCodeIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().listByCountryCode(None)

    def shouldThrowExceptionWhenRequestFilterPageIsLessThanOrEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().List_with_filter(OperatorFilter().withPage(0,5))

    def shouldThrowExceptionWhenRequestFilterPageSizeIsLessThanOrEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.operators().List_with_filter(OperatorFilter().withPage(1,0))

    def assertIsValidOperator(self, operator):
        operatorFields = ["id", "name", "bundle", "data", "pinBased", "supportsLocalAmounts",
                "denominationType", "senderCurrencyCode", "senderCurrencySymbol", "destinationCurrencyCode",
                "destinationCurrencySymbol", "internationalDiscount", "localDiscount", "mostPopularInternationalAmount",
                "mostPopularLocalAmount", "country", "fxRate", "suggestedAmounts", "suggestedAmountsMap", "minAmount",
                "maxAmount", "localMinAmount", "localMaxAmount", "fixedAmounts", "localFixedAmounts",
                "fixedAmountsDescriptions", "localFixedAmountsDescriptions", "logoUrls", "promotions"]

        for i in operator:
            count = 0
            for j in i:
                if type(j)==str:
                    assert j!=None
                elif type(j)==dict:
                    assert j[operatorFields[count]]!=None
                count = count + 1
