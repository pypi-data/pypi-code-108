from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string

from drf_auth_service.common.email_backends import HtmlTemplateBackend
from drf_auth_service.common.register_backends import PhoneCodeBackend
from drf_auth_service.common.sms_backends import TwilioBackend
from drf_auth_service.models import ActivationCode


class CustomHtmlTemplateBackend(HtmlTemplateBackend):
    def send(self, html_template, **context):
        try:
            email_html_message = render_to_string((html_template, context.get('default_template')), context)
        except ImproperlyConfigured:
            pass
        print('was successfully success')

    def send_reset_password(self, user):
        ActivationCode.create_token(user, ActivationCode.CodeTypes.RESET_PASSWORD)


class CustomTwilioBackend(TwilioBackend):
    def send(self, to_phone, message, from_phone=None):
        print(to_phone, message, 'success')


class CustomPhoneCodeBackend(PhoneCodeBackend):
    def register(self):
        user, code = self.register_user()

        return dict(code=code)
