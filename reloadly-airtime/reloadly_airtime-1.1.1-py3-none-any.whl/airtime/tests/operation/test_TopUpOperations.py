from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
from reloadly_airtime.airtime.sdk.dto.Request.EmailTopUpRequest import EmailTopupRequest
from reloadly_airtime.airtime.sdk.dto.Request.PhoneTopUpRequest import PhoneTopupRequest
from reloadly_airtime.airtime.sdk.dto.Phone import Phone
from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
import pytest

class TestTopupOperations():

    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server = None

    def test_SendPhoneTopup(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        baseUrlField = airtimeAPI.baseUrl
        amount = 500.00
        operatorId = 173
        phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("+50936377111", "HT")).value
        request = airtimeAPI.topups().send(phoneTopupRequest)
        assert request!=None

    def test_SendPinBasedPhoneTopup(self):
        airtimeAPI = AirtimeAPI(clientId = AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
        baseUrlField = airtimeAPI.baseUrl
        Amount = 500.00
        operatorId = 341
        phoneTopupRequest = PhoneTopupRequest(Amount, operatorId).recipientPhone(Phone("08147658721", "NG")).value
        request = airtimeAPI.topups().send(phoneTopupRequest)
        assert request!=None

    def test_SendEmailTopup(self):
        airtimeAPI = AirtimeAPI(clientId=AirtimeAPIMockServer().clientId, clientSecret=AirtimeAPIMockServer().clientSecret)
        baseUrlField = airtimeAPI.baseUrl
        amount = 5000.00
        operatorId = 683
        emailTopupRequest = EmailTopupRequest(amount, operatorId, "testing@nauta.com.cu").value
        request = airtimeAPI.topups().send(emailTopupRequest)
        assert request!=None

    def test_SendPhoneTopupShouldThrowExceptionWhenRecipientPhoneIsMissing(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 500
            operatorId = 672
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).value
            request = airtimeAPI.topups().send(phoneTopupRequest)

    def test_SendPhoneTopupShouldThrowExceptionWhenRecipientPhoneNumberIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 19.23
            operatorId = 132
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone(None, 'GR')).value
            request = airtimeAPI.topups().send(phoneTopupRequest)
    
    def test_SendPhoneTopupShouldThrowExceptionWhenRecipientPhoneNumberIsEmpty(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 123.21
            operatorId = 190
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("", 'GR')).value
            request = airtimeAPI.topups().send(phoneTopupRequest)
    
    def test_SendPhoneTopupShouldThrowExceptionWhenRecipientPhoneNumberContainsInvalidCharacters(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 5000.00
            operatorId = 190
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("+3ABCD069-7039456", 'GR')).value
            request = airtimeAPI.topups().send(phoneTopupRequest)

    def test_SendPhoneTopupShouldThrowExceptionWhenRecipientPhoneCountryCodeIsNull(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 123.21
            operatorId = 190
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("+306907039456", None)).value
            request = airtimeAPI.topups().send(phoneTopupRequest)

    def test_SendPhoneTopupShouldThrowExceptionWhenAmountIsMissing(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 123.21
            operatorId = 190
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("+306907039456", None)).value
            request = airtimeAPI.topups().send(phoneTopupRequest)

    def test_SendPhoneTopupShouldThrowExceptionWhenAmountEqualsToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = 0
            operatorId = 190
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("+306907039456", 'GR')).value
            request = airtimeAPI.topups().send(phoneTopupRequest)

    def test_SendPhoneTopupShouldThrowExceptionWhenAmountLessThanToZero(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI(clientId= AirtimeAPIMockServer().clientId, clientSecret= AirtimeAPIMockServer().clientSecret)
            amount = -123.21
            operatorId = 190
            phoneTopupRequest = PhoneTopupRequest(amount, operatorId).recipientPhone(Phone("+306907039456", 'GR')).value
            request = airtimeAPI.topups().send(phoneTopupRequest)
