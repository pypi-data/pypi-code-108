from abc import abstractmethod

from django.template import Context, Template
from rest_framework.exceptions import ValidationError
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from drf_auth_service.common.constants import TWILIO_BACKEND_NAME
from drf_auth_service.models import ActivationCode


class BasePhoneBackend:
    configs = {}
    template_reset = 'SMS_RESET_PASSWORD_MESSAGE'
    template_confirm = 'SMS_CONFIRMATION_MESSAGE'
    request = None

    def __init__(self, configs: dict, request):
        self.configs = configs
        self.request = request
        self.config_backend()

    @abstractmethod
    def send(self, to_phone, message, from_phone=None):
        pass

    @abstractmethod
    def config_backend(self):
        pass

    def send_reset_password(self, user):
        self.send(message=self.get_message(self.template_reset, user), to_phone=user.username)

    def send_confirmation(self, user):
        self.send(message=self.get_message(self.template_confirm, user), to_phone=user.username)

    def get_message(self, template_type, user):
        message = self.configs[template_type]
        if template_type == self.template_reset:
            code = ActivationCode.create_token(
                user, ActivationCode.CodeTypes.RESET_PASSWORD, for_phone=True
            )

        else:
            code = ActivationCode.create_token(
                user, ActivationCode.CodeTypes.CONFIRM_ACCOUNT, for_phone=True
            )

        template = Template(message)
        context = Context({"code": str(code.key)})
        return template.render(context)


class TwilioBackend(BasePhoneBackend):
    name = TWILIO_BACKEND_NAME
    client = None

    def send(self, to_phone, message, from_phone=None):
        if from_phone is None:
            from_phone = self.configs['TWILIO_FROM_NUMBER']
        try:
            self.client.messages.create(to=f"+{to_phone}", from_=from_phone, body=message)
        except TwilioRestException:
            raise ValidationError(dict(detail='Improperly configuration for twilio'))

    def config_backend(self):
        self.client = Client(self.configs['TWILIO_ACCOUNT_SID'], self.configs['TWILIO_AUTH_TOKEN'])
