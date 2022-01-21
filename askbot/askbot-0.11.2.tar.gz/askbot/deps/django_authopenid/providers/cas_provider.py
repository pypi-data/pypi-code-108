from askbot.deps.django_authopenid.protocols.base import BaseProtocol
from askbot.conf import settings as askbot_settings
from askbot.utils.html import site_url
from askbot.utils.functions import encode_jwt
from cas import CASClient
from django.conf import settings as django_settings
from django.urls import reverse
import urllib.request, urllib.parse, urllib.error

class CASLoginProvider(BaseProtocol):

    def __init__(self, success_redirect_url=None):
        self.name = 'cas'
        self.protocol_type = 'cas'
        self.display_name = askbot_settings.CAS_SERVER_NAME
        self.icon_media_path = askbot_settings.CAS_LOGIN_BUTTON
        self.one_click_registration = getattr(
                                        django_settings,
                                        'ASKBOT_CAS_ONE_CLICK_REGISTRATION_ENABLED',
                                        False
                                             )
        self.client = CASClient(version=askbot_settings.CAS_PROTOCOL_VERSION,
                                server_url=askbot_settings.CAS_SERVER_URL,
                                service_url=self.get_service_url(success_redirect_url))

    def verify_ticket(self, *args, **kwargs):
        return self.client.verify_ticket(*args, **kwargs)

    def get_login_url(self):
        return self.client.get_login_url()

    @classmethod
    def get_service_url(cls, success_redirect_url):
        service_url = site_url(reverse('user_complete_cas_signin'))
        if success_redirect_url:
            next_param_value = encode_jwt({'next_url': success_redirect_url})
            service_url += '?' + urllib.parse.urlencode({'next': next_param_value})
        return service_url
