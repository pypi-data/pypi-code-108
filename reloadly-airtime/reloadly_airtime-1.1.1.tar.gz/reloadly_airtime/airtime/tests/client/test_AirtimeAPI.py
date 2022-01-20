# test_with_pytest.py
from reloadly_airtime.airtime.sdk.client.AirtimeAPI import AirtimeAPI
from reloadly_airtime.airtime.tests.AirtimeAPIMockServer import AirtimeAPIMockServer
import pytest
import os
from dotenv import load_dotenv

load_dotenv('.env')

class TestAirtimeAPI():
    accessToken = os.environ.get('AIRTIME_ACCESS_TOKEN')

    def setUp(self):
        self.server = AirtimeAPIMockServer()

    def tearDown(self):
        self.server.stop()

    def test_shouldEnableTelemetryByDefault(self):
        airtimeAPI = AirtimeAPI(accessToken=self.accessToken)
        field = airtimeAPI.enableTelemetry
        assert field==True

    def test_shouldEnableTelemetryExplicitly(self):
        airtimeAPI = AirtimeAPI(accessToken = self.accessToken, enableTelemetry = True)
        field = airtimeAPI.enableTelemetry
        assert field==True

    def test_shouldDisableTelemetry(self):
        airtimeAPI = AirtimeAPI(accessToken = self.accessToken, enableTelemetry=False)
        field = airtimeAPI.enableTelemetry
        assert field==False

    def test_shouldDisableLoggingByDefault(self):
        airtimeAPI = AirtimeAPI(accessToken = self.accessToken)
        field = airtimeAPI.enablelogging
        assert field==False

    def test_shouldEnableLogging(self):
        airtimeAPI = AirtimeAPI(accessToken = self.accessToken , enablelogging = True)
        field = airtimeAPI.enablelogging
        assert field==True

    def test_shouldDisableLoggingInterceptorExplicitly(self):
        airtimeAPI = AirtimeAPI(accessToken = self.accessToken , enablelogging=False)
        field = airtimeAPI.enablelogging
        assert field==False

    def test_shouldThrowExceptionWhenCredentialsAndAccessTokenAreMissing(self):
        with pytest.raises(Exception):
            airtimeAPI = AirtimeAPI()
            