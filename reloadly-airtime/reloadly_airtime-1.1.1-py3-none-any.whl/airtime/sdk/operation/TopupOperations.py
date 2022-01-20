from reloadly_airtime.airtime.sdk.dto.Phone import Phone
from reloadly_airtime.airtime.sdk.operation.BaseAirtimeOperation import BaseAirtimeOperation
from reloadly_core.core.internal.dto.request.interfaces.Request import Request
from reloadly_core.core.internal.util.Asserter import Asserter

class TopupOperations(BaseAirtimeOperation):
    END_POINT = "topups"
    def __init__(self, client, baseUrl : str, apiToken : str):
        self.client = client
        self.baseUrl = baseUrl
        self.apiToken = apiToken
        super().__init__(self.client, self.baseUrl, self.apiToken)

    def send(self, request):
        self.validateTopupRequest(request)
        return super().createPostRequest(super().getBuilder(self.END_POINT), request)

    def validateTopupRequest(self,request):
        Asserter().assertNotNull(request["amount"], "Amount")
        Asserter().assertGreaterThanZero(request["amount"], "Amount")
        Asserter().assertNotNull(request["operatorId"], "Operator id")
        Asserter().assertGreaterThanZero(request["operatorId"], "Operator id")
        if "recipientPhone" in request:
            if "senderPhone" in request:
                self.assertValidPhone(request["senderPhone"], "senderPhone")
            self.assertValidPhone(request["recipientPhone"], "recipientPhone")
        if "customIdentifier" in request:
            Asserter().assertValidEmail(request["customIdentifier"], "RecepientEmail")

    def assertValidPhone(self, phone , fieldName : str):
        messagePrefix1 = "Phone"
        messagePrefix2 = "Phone number"
        messagePrefix3 = "Phone country code"
        if fieldName!=None and fieldName=="recipientPhone":
            messagePrefix1 = "Recepient phone"
            messagePrefix2 = "Recepient phone number"
            messagePrefix3 = "Recepient phone country code"
        elif fieldName!=None and fieldName=="senderPhone":
            messagePrefix1 = "Sender phone"
            messagePrefix2 = "Sender phone number"
            messagePrefix3 = "Sender phone country code"

        Asserter().assertNotNull(phone, messagePrefix1)
        Asserter().assertNotEmpty(phone["number"], messagePrefix2)
        number = phone["number"]
        number = number.replace("+","")
        number = number.replace(" ","")
        number = number.strip()
        if not (len(number)>3):
            raise Exception("$messagePrefix2 must contain only numbers and an optional leading '+' sign!", messagePrefix2)

        Asserter().assertNotNull(phone, messagePrefix3)

