from reloadly_airtime.airtime.sdk.dto.Request.TopupRequest import TopupRequest
import reloadly_airtime.airtime.sdk.dto.Phone as Phone

class PhoneTopupRequest(TopupRequest):
    def __init__(self, amount, operatorId):
        self.value = {}
        super().__init__(amount, operatorId)

    def recipientPhone(self, phone):
        self.value['recipientPhone'] =  {
            "countryCode" : phone.CountryCode,
            "number" : phone.number
        }
        return self


