from reloadly_airtime.airtime.sdk.dto.Response import Operator
from reloadly_airtime.airtime.sdk.dto.Response import OperatorFxRate
from reloadly_core.core.internal.Filter.OperatorFilter import OperatorFilter
from reloadly_airtime.airtime.sdk.Internal.FxRateRequest import FxRateRequest
from reloadly_core.core.internal.dto.request.interfaces.Request import Request
from reloadly_core.core.internal.util.Asserter import Asserter
from reloadly_airtime.airtime.sdk.operation.BaseAirtimeOperation import BaseAirtimeOperation
import http

class OperatorOperations(BaseAirtimeOperation):
    END_POINT = "operators"
    PATH_SEGMENT_FX_RATE = "/fx-rate"
    PATH_SEGMENT_COUNTRIES = "/countries"
    PATH_SEGMENT_AUTO_DETECT = "/auto-detect"
    PATH_SEGMENT_AUTO_DETECT_PHONE = "/phone"
    def __init__(self, client, baseUrl : str, apiToken : str):
        self.baseUrl = baseUrl
        self.client = client
        self.apiToken = apiToken
        super().__init__(self.client, self.baseUrl, self.apiToken)

    def List_with_filter(self, Filter):
        return super().createGetRequest(super().buildFilters(Filter, self.END_POINT))

    def List_without_filter(self):
        return super().createGetRequest(super().getBuilder(self.END_POINT))

    def getById_with_filter(self,operatorId : int, Filter):
        self.validateOperatorId(operatorId)
        builder = super().buildFilters(Filter, self.END_POINT)
        builder = builder + "/" + str(operatorId)
        return super().createGetRequest(str(builder))

    def getById_without_filter(self,operatorId : int):
        self.validateOperatorId(operatorId)
        builder = super().getBuilder(self.END_POINT)
        builder = builder + "/" + str(operatorId)
        return super().createGetRequest(str(builder))
    
    def autoDetect(self,phone : str, countryCode , Filter):
        self.validatePhoneAndCountryCode(phone, countryCode)
        return super().createGetRequest(self.buildAutoDetectRequest(phone, countryCode, super().buildFilters(Filter, self.END_POINT)))

    def autoDetect(self,phone : str, countryCode):
        self.validatePhoneAndCountryCode(phone, countryCode)
        return super().createGetRequest(self.buildAutoDetectRequest(phone, countryCode, None))

    def listByCountryCode_with_Filters(self,countryCode , Filter):
        Asserter().assertNotNull(countryCode, "Country code")
        builder = self.buildListByCountryCodeRequestUrl(countryCode, None)
        return super().createGetRequest(self.buildListByCountryCodeRequestUrl(countryCode, super().buildFilters(Filter, str(builder))))

    def listByCountryCode_without_Filters(self, countryCode):
        Asserter().assertNotNull(countryCode, "Country code")
        return super().createGetRequest(self.buildListByCountryCodeRequestUrl(countryCode, None))

    def calculateFxRate(self, operatorId : int, amount : float):
        self.validateOperatorId(operatorId)
        Asserter().assertNotNull(amount, "Amount")
        Asserter().assertGreaterThanZero(amount, "Amount")
        return super().createPostRequest(self.buildCalculateFxRateRequestUrl(operatorId), amount)
        
    def buildListByCountryCodeRequestUrl(self ,countryCode , builder : str):
        if builder == None:
            builder = super().getBuilder(self.END_POINT)
        return builder + self.PATH_SEGMENT_COUNTRIES + "/" + str(countryCode)

    def buildCalculateFxRateRequestUrl(self,operatorId : int):
        return super().getBuilder(self.END_POINT + self.PATH_SEGMENT_FX_RATE + "/" + str(operatorId)) 

    def buildAutoDetectRequest(self,phone : str, countryCode, builder : str):
        if "+" not in str(phone):
            phone = int("+" + str(phone))
        if builder == None:
            builder = super().getBuilder(self.END_POINT)
        return builder + self.PATH_SEGMENT_AUTO_DETECT + self.PATH_SEGMENT_AUTO_DETECT_PHONE + "/" + str(phone) + self.PATH_SEGMENT_COUNTRIES + "/" + str(countryCode)

    def validateOperatorId(self,operatorId : int):
        Asserter().assertNotNull(operatorId, "Operator id")
        Asserter().assertGreaterThanZero(operatorId, "Operator id")

    def validatePhoneAndCountryCode(self,phone : str, countryCode):
        Asserter().assertGreaterThanZero(phone, "Phone")
        Asserter().assertNotNull(countryCode, "Country code")