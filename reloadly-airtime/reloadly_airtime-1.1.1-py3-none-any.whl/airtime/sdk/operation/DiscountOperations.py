from reloadly_airtime.airtime.sdk.dto.Response.Discount import Discount
from reloadly_core.core.internal.dto.request.interfaces.Request import Request
from reloadly_core.core.internal.Filter.QueryFilter import QueryFilter
from reloadly_core.core.internal.util.Asserter import Asserter
from reloadly_airtime.airtime.sdk.operation.BaseAirtimeOperation import BaseAirtimeOperation

class DiscountOperations(BaseAirtimeOperation):
    END_POINT = "operators"
    PATH_SEGMENT_DISCOUNT = "/commissions"

    def __init__(self, client, baseUrl : str, apiToken : str):
        self.client = client
        self.baseUrl = baseUrl
        self.apiToken = apiToken
        super().__init__(self.client, self.baseUrl, self.apiToken)

    def List_without_filter(self):
        return super().createGetRequest(super().getBuilder(self.END_POINT + self.PATH_SEGMENT_DISCOUNT))
        

    def List_with_filter(self,Filter):
        return super().createGetRequest(super().buildFilters(Filter, self.END_POINT + self.PATH_SEGMENT_DISCOUNT))

    def getByOperatorId(self,operatorId : int):
        Asserter().assertNotNull(operatorId, "Operator_id")
        Asserter().assertGreaterThanZero(operatorId, "Operator_id")
        return super().createGetRequest(super().getBuilder(self.END_POINT + "/" + str(operatorId) + self.PATH_SEGMENT_DISCOUNT))

