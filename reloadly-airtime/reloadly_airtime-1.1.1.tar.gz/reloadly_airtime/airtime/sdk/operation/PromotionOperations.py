from reloadly_airtime.airtime.sdk.dto.Response.Promotion import Promotion
from reloadly_core.core.internal.dto.request.interfaces.Request import Request
from reloadly_core.core.internal.Filter.QueryFilter import QueryFilter
from reloadly_core.core.internal.util.Asserter import Asserter
from reloadly_airtime.airtime.sdk.operation.BaseAirtimeOperation import BaseAirtimeOperation

class PromotionOperations(BaseAirtimeOperation):
    END_POINT = "promotions"
    PATH_SEGMENT_COUNTRIES = "/countries"
    PATH_SEGMENT_OPERATORS = "/operators"
    def __init__(self, client, baseUrl : str, apiToken : str):
        self.client = client
        self.baseUrl = baseUrl
        self.apiToken = apiToken
        super().__init__(self.client, self.baseUrl, self.apiToken)

    def List_without_filter(self):
        return super().createGetRequest(super().getBuilder(self.END_POINT))

    def List_with_filter(self, Filter):
        return super().createGetRequest(super().buildQueryFilters(Filter, self.END_POINT))

    def getById(self,promotionId : int):
        Asserter().assertNotNull(promotionId, "Promotion id")
        Asserter().assertGreaterThanZero(promotionId, "Promotion id")
        return super().createGetRequest(super().getBuilder(self.END_POINT) + "/" + str(promotionId))

    def getByCountryCode(self, countryCode):
        Asserter().assertNotNull(countryCode, "Country code")
        return super().createGetRequest(super().getBuilder(self.END_POINT) + self.PATH_SEGMENT_COUNTRIES + "/" + str(countryCode))

    def getByOperatorId(self, operatorId : int):
        Asserter().assertNotNull(operatorId, "Operator id")
        Asserter().assertGreaterThanZero(operatorId, "Operator id")
        return super().createGetRequest(super().getBuilder(self.END_POINT) + self.PATH_SEGMENT_OPERATORS + "/" + str(operatorId))
