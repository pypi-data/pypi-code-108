import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

import jwt

from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.exceptions import AuthenticationError, ModelNotFoundAPIError

from .rest_views import BaseRestView, BodyMixin, CreateRestViewMixin

logger = logging.getLogger(__name__)

UserModel = get_user_model()


@rest_view("/auth")
class AuthenticationView(BodyMixin, BaseRestView):
    token_generator = default_token_generator

    def login_error_response(self):
        raise AuthenticationError()

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/login", public=True, method="post")
    def login(self, *args, **kwargs):
        data = self.deserialize_body()
        user = authenticate(self.request, username=data['username'],
                            password=data['password'])
        if user is not None:
            return JsonResponse({
                'token': self._prepare_token(user),
                'user': self.get_user_information(user)
            })
        return self.login_error_response()

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/change-password", method="post")
    def change_password(self, *args, **kwargs):
        data = self.deserialize_body()
        user = authenticate(self.request,
                            username=self.request.user.get_username(),
                            password=data['old_password'])
        if user is not None:
            user.set_password(data['new_password'])
            user.save()
            return JsonResponse({
                'message': _('password updated successfully')
            })
        return JsonResponse({
            'message': 'invalid password reset'
        }, status=401)

    def _prepare_token(self, user):
        payload = {
            'pfx_user_pk': user.pk,
        }
        if settings.PFX_TOKEN_VALIDITY:
            exp = datetime.utcnow() + timedelta(**settings.PFX_TOKEN_VALIDITY)
            payload.update(exp=exp)
        payload.update(self.get_extra_payload(user))
        return jwt.encode(
            payload, settings.PFX_SECRET_KEY, algorithm="HS256")

    def get_extra_payload(self, user):
        return {}

    def get_user_information(self, user):
        return {
            'username': user.get_username(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email}

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/set-password", public=True, method="post")
    def set_password(self, *args, **kwargs):
        data = self.deserialize_body()
        assert 'uidb64' in data and 'token' in data

        user = self.get_user(data['uidb64'])

        if (user is not None and
                self.token_generator.check_token(user, data['token'])):
            user.set_password(data['password'])
            user.is_active = True
            user.save()
            return JsonResponse({
                'message': _('password updated successfully')
            })
        raise AuthenticationError()

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist,
                ValidationError):
            user = None
        return user


class SendMessageTokenMixin:
    email_template_name = None
    subject_template_name = None
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None

    def send_token_message(self, user):
        token = self.token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        data = {
            'target_user': user,
            'token': token,
            'uid': uid,
            'reset_url': settings.PFX_RESET_PASSWORD_URL.format(
                token=token,
                uid=uid,
            ),
            'site_name': settings.PFX_SITE_NAME,
            'user': user,
            **(self.extra_email_context or {})
        }
        subject = loader.render_to_string(self.subject_template_name, data)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(self.email_template_name, data)
        email_message = EmailMultiAlternatives(subject, body, self.from_email,
                                               [user.email])
        if self.html_email_template_name is not None:
            html_email = loader.render_to_string(self.html_email_template_name,
                                                 data)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()


@rest_view("/auth/signup")
class SignupView(SendMessageTokenMixin, CreateRestViewMixin, BaseRestView):
    email_template_name = 'registration/welcome_email.txt'
    subject_template_name = 'registration/welcome_subject.txt'
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    default_public = True

    queryset = UserModel._default_manager
    fields = ['first_name', 'last_name', 'username', 'email']

    def validate(self, resolver, **kwargs):
        resolver.object.set_unusable_password()
        super().validate(resolver, **kwargs)

    def is_valid(self, resolver, created=True):
        r = super().is_valid(resolver, created)
        self.send_token_message(resolver.object)
        return r


@rest_view("/auth")
class ForgotenPasswordView(SendMessageTokenMixin, BodyMixin, BaseRestView):
    email_template_name = 'registration/welcome_email.txt'
    subject_template_name = 'registration/welcome_subject.txt'
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None

    fields = ['first_name', 'last_name', 'username', 'email']

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api("/forgotten-password", public=True, method="post")
    def forgotten_password(self, *args, **kwargs):
        data = self.deserialize_body()
        try:
            user = UserModel._default_manager.get(email=data['email'])
        except UserModel.DoesNotExist:
            user = None
        if user is not None:
            self.send_token_message(user)
            return JsonResponse({
                'message': _('A message has been sent')
            })
        raise ModelNotFoundAPIError(UserModel)
