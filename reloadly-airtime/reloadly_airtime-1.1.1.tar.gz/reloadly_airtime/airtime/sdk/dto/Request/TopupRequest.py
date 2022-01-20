from reloadly_airtime.airtime.sdk.dto.Request.Topupable import Topupable


class TopupRequest(Topupable):
    def __init__(self, amount = 0.00, operatorId = 1, useLocalAmount = False, customIdentifier=""):
        self.value['amount'] = amount
        self.value['operatorId'] = operatorId
        #Amount (in sender's currency) to credit recipient phone for
        