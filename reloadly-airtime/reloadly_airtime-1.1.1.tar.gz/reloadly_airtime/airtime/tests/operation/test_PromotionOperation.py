from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
from reloadly_core.core.internal.Filter.QueryFilter import QueryFilter
import pytest

class TestPromotionOperations():

    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server.stop()

    def test_ListPromotionsWithNoFilters(self):
        self.server = AirtimeAPIMockServer()
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        request = airtimeAPI.promotions().List_without_filter()
        assert request!=None
        self.assertIsValidPromotion(request)

    def test_ListPromotionsWithFilters(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        page = 1
        pageSize = 5
        Filter = QueryFilter().withPage(page, pageSize)
        request = airtimeAPI.promotions().List_with_filter(Filter)
        assert request!=None
        self.assertIsValidPromotion(request)
        assert len(request['content']) == pageSize
        

    def test_GetById(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        promotionId = 5665
        request = airtimeAPI.promotions().getById(promotionId)
        assert request!=None
        self.assertIsValidPromotion(request)


    def test_GetByCountryCode(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        countryCode = "HT"
        request = airtimeAPI.promotions().getByCountryCode(countryCode)
        assert request!=None
        self.assertIsValidPromotion(request)
    
    def test_GetByOperatorId(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        self.baseUrlField = airtimeAPI.baseUrl
        operatorId = 173
        request = airtimeAPI.promotions().getByOperatorId(operatorId)
        assert request!=None
        self.assertIsValidPromotion(request)

    def test_GetByCodeShouldThrowExceptionWhenCountryCodeIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getByCountryCode(None)

    def test_GetByOperatorIdShouldThrowExceptionWhenOperatorIdIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getByOperatorId(None)
    
    def test_GetByOperatorIdShouldThrowExceptionWhenOperatorIdIsLessThanZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getByOperatorId(-105)

    def test_GetByOperatorIdShouldThrowExceptionWhenOperatorIdIsEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getByOperatorId(0)

    def test_GetByIdShouldThrowExceptionWhenPromotionIdIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getById(None)

    def test_GetByIdShouldThrowExceptionWhenPromotionIdIsLessThanZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getById(-105)

    def test_GetByIdShouldThrowExceptionWhenPromotionIdIsEqualToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
            request = airtimeAPI.promotions().getById(0)
        
    def assertIsValidPromotion(self, promotion):
        if len(promotion)==6:
            countryFields = ["timeStamp", "message", "path", "errorCode", "infoLink", "details"]
        else:
            countryFields = ["id", "promotionId", "title", "title2", "description", "endDate", "denominations", "localDenominations"]
        for i in promotion:
            count = 0
            for j in i:
                if type(j)==str:
                    assert j!=None
                elif type(j)==dict:
                    assert j[countryFields[count]]!=None
                count = count + 1


