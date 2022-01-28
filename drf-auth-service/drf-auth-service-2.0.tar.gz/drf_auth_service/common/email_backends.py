from abc import abstractmethod

import sib_api_v3_sdk
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from mailchimp3 import MailChimp

from drf_auth_service.common.constants import MAILCHIMP_BACKEND_NAME, SENDINBLUE_BACKEND_NAME, HTML_BACKEND_NAME
from drf_auth_service.models import ActivationCode
from drf_auth_service.settings import settings


class BaseEmailBackend:
    configs = {}
    template_reset = None
    template_confirm = None
    request = None

    def __init__(self, configs: dict, request):
        self.configs = configs
        self.request = request
        self.config_backend()

    @abstractmethod
    def send(self, template_id, **context):
        pass

    @abstractmethod
    def config_backend(self):
        pass

    def send_reset_password(self, user):
        token = ActivationCode.create_token(user, ActivationCode.CodeTypes.RESET_PASSWORD)
        send_reset_pass_url = f"{settings.SEND_RESET_PASSWORD_URL}{token.key}"
        self.send(self.get_template(self.template_reset), email=user.username,
                  send_reset_pass_url=send_reset_pass_url)

    def send_confirmation(self, user):
        token = ActivationCode.create_token(user, ActivationCode.CodeTypes.CONFIRM_ACCOUNT)
        send_confirmation_url = f"{settings.SEND_CONFIRMATION_URL}{token.key}"
        self.send(self.get_template(self.template_confirm), email=user.username,
                  send_confirmation_url=send_confirmation_url)

    def get_template(self, template_type):
        return self.configs[template_type]


class MailchimpBackend(BaseEmailBackend):
    name = MAILCHIMP_BACKEND_NAME
    client = None
    template_reset = 'MAILCHIMP_RESET_PASS_TEMPLATE'
    template_confirm = 'MAILCHIMP_CONFIRMATION_TEMPLATE'

    def send(self, template_id, **context):
        pass

    def config_backend(self):
        self.client = MailChimp(self.configs['MAILCHIMP_USERNAME'], self.configs['MAILCHIMP_SECRET_KEY'])


class SendInBlueBackend(BaseEmailBackend):
    name = SENDINBLUE_BACKEND_NAME
    configurations = None
    send_in_blue_instance = None
    template_reset = 'SENDINBLUE_RESET_PASS_TEMPLATE'
    template_confirm = 'SENDINBLUE_CONFIRMATION_TEMPLATE'

    def send(self, template_id, **context):
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[{"email": context['email']}],
                                                       template_id=template_id, params=context)
        self.send_in_blue_instance.send_transac_email(send_smtp_email)

    def config_backend(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.configs['SENDINBLUE_API_KEY']
        self.send_in_blue_instance = sib_api_v3_sdk.SMTPApi(sib_api_v3_sdk.ApiClient(configuration))


class HtmlTemplateBackend(BaseEmailBackend):
    name = HTML_BACKEND_NAME
    email_backend = None
    template_reset = 'HTML_EMAIL_RESET_TEMPLATE'
    template_confirm = 'HTML_EMAIL_CONFIRM_TEMPLATE'

    def send(self, html_template, **context):
        try:
            email_html_message = render_to_string((html_template, context.get('default_template')), context)
        except TemplateDoesNotExist:
            raise ImproperlyConfigured(F"{html_template} invalid path in settings")
        send_mail(context['subject'], email_html_message, self.configs['HTML_DEFAULT_FROM_EMAIL'],
                  [context['email']], connection=self.email_backend, html_message=email_html_message)

    def config_backend(self):
        self.email_backend = EmailBackend(host=self.configs['EMAIL_HOST'],
                                          port=self.configs['EMAIL_PORT'],
                                          username=self.configs['EMAIL_USERNAME'],
                                          password=self.configs['EMAIL_PASSWORD'],
                                          use_tls=self.configs['EMAIL_USE_TLS'],
                                          fail_silently=False)

    def send_reset_password(self, user):
        token = ActivationCode.create_token(user, ActivationCode.CodeTypes.RESET_PASSWORD)
        send_reset_pass_url = f"{settings.RESET_PASSWORD_URL}{token.key}"
        self.send(self.get_template(self.template_reset), email=user.username, default_template='reset_password.html',
                  send_reset_pass_url=send_reset_pass_url, subject=self.configs['HTML_RESET_PASSWORD_SUBJECT'])

    def send_confirmation(self, user):
        token = ActivationCode.create_token(user, ActivationCode.CodeTypes.CONFIRM_ACCOUNT)
        send_confirmation_url = f"{settings.SEND_CONFIRMATION_URL}{token.key}"
        self.send(self.get_template(self.template_confirm), email=user.username,
                  send_confirmation_url=send_confirmation_url, subject=self.configs['HTML_CONFIRMATION_SUBJECT'],
                  default_template='confirm_account.html')
