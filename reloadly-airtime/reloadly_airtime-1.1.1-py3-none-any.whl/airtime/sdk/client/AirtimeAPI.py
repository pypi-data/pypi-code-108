from reloadly_airtime.airtime.sdk.operation.AccountOperations import AccountOperations
from reloadly_airtime.airtime.sdk.operation.CountryOperations import CountryOperations
from reloadly_airtime.airtime.sdk.operation.DiscountOperations import DiscountOperations
from reloadly_airtime.airtime.sdk.operation.OperatorOperations import OperatorOperations
from reloadly_airtime.airtime.sdk.operation.PromotionOperations import PromotionOperations
from reloadly_airtime.airtime.sdk.operation.ReportOperations import ReportOperations
from reloadly_airtime.airtime.sdk.operation.TopupOperations import TopupOperations
from reloadly_airtime.airtime.sdk.operation.TransactionHistoryOperations import TransactionHistoryOperations
from reloadly_auth.authentication.client.AuthenticationAPI import AuthenticationAPI
from reloadly_auth.authentication.client.OAuth2ClientCredentialsOperation import OAuth2ClientCredentialsOperation
from reloadly_core.core.enums.Environment import Environment
from reloadly_core.core.enums.Service import Service
import reloadly_core.core.exception.ReloadlyException as ReloadlyException
import reloadly_core.core.internal.constant.HttpHeader as HttpHeader
import reloadly_core.core.internal.dto.request.CustomizableRequest as CustomizableRequest 
import reloadly_core.core.internal.dto.request.interfaces.Request as Request
from reloadly_core.core.internal.enums.Version import Version
from reloadly_core.core.internal.net.ServiceAPI import ServiceAPI
from reloadly_core.core.internal.util.Asserter import Asserter
from reloadly_core.core.net.HttpOptions import HttpOptions
from xml.etree import ElementTree as et
from requests.compat import urljoin
import json
import requests
import ssl
import http
from datetime import datetime
from urllib3 import PoolManager, logging, disable_warnings, exceptions
import time


class AirtimeAPI(ServiceAPI):
    
    def __init__(self, clientId = "", clientSecret = "", client = PoolManager() , accessToken = "", environment = Environment, enablelogging = False, redactHeaders = [], options = HttpOptions(), enableTelemetry = True):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.enablelogging = enablelogging
        self.enableTelemetry = enableTelemetry
        self.accessToken = accessToken
        self.environment = environment
        self.redactHeaders = redactHeaders
        self.options = options
        self.client = client
        super().ServiceAPI(clientId, clientSecret, accessToken, enablelogging, redactHeaders, options, enableTelemetry)
        self.validateCredentials(clientId, clientSecret, accessToken)
        self.environment = environment
        self.baseUrl = self.createBaseUrl()

    def refreshAccessToken(self, request):
        self.accessToken = None
        request = CustomizableRequest()
        newAccessToken = self.retrieveAccessToken()
            
        request.addHeader(HttpHeader.AUTHORIZATION,"Bearer " + newAccessToken)

    def createBaseUrl(self):
        service = self.getServiceByEnvironment(self.environment)
        Asserter().assertNotNull(service, "Service")
        if self.environment == Environment.LIVE:
            url = Service.AIRTIME
        else:
            url = Service.AIRTIME_SANDBOX
        if not url:
            raise Exception("The airtime base url had an invalid format and coudnt be parsed as a Url.")
        return url

    def getServiceByEnvironment(self, environment):
        if (self.environment == environment.LIVE):
            return "AIRTIME"
        else:
            return "AIRTIME_SANDBOX"

    def retrieveAccessToken(self):
        if (self.accessToken):
            return self.accessToken
        return self.doGetAccessToken(self.getServiceByEnvironment(self.environment))

    def doGetAccessToken(self, service):
        try:
            if self.enablelogging:
                logging.basicConfig(level = logging.DEBUG)
            if self.accessToken:
                return self.accessToken
            else:
                return OAuth2ClientCredentialsOperation(self.baseUrl, self.clientId, self.clientSecret).getAccessToken(self.baseUrl)

        except:
            raise Exception("ReloadlyException")

    def operators(self):
        try:
            a = self.retrieveAccessToken()
            return OperatorOperations(self.client, self.baseUrl, a)
        except:
            raise Exception("ReloadlyException")

    def countries(self):
        try:
            a = self.retrieveAccessToken()
            return CountryOperations(self.client, self.baseUrl, a)
        except:
            raise Exception("ReloadlyException")
            pass

    def accounts(self):
        try:
            a = self.retrieveAccessToken()
            return AccountOperations(self.client, self.baseUrl, a)
        except:
            raise Exception("ReloadlyException")

    def discounts(self):
        try:
            a = self.retrieveAccessToken()
            return DiscountOperations(self.client, self.baseUrl, self.retrieveAccessToken())
        except:
            raise Exception("ReloadlyException")

    def promotions(self):
        try:
            a = self.retrieveAccessToken()
            return PromotionOperations(self.client, self.baseUrl, a)
        except:
            raise Exception("ReloadlyException")
        
    def topups(self):
        try:
            return TopupOperations(self.client, self.baseUrl, self.retrieveAccessToken())
        except:
            raise Exception("ReloadlyException")

    def reports(self):
        try:
            return ReportOperations(self.client, self.baseUrl, self.retrieveAccessToken())
        except:
            raise Exception("ReloadlyException")
