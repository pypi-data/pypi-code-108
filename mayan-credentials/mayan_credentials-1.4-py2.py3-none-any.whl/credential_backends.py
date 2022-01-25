from django.utils.translation import ugettext_lazy as _

from .classes import CredentialBackend


class OAuthAccessToken(CredentialBackend):
    class_fields = ('access_token',)
    field_order = ('access_token',)
    fields = {
        'access_token': {
            'label': _('Access token'),
            'class': 'django.forms.CharField', 'default': '',
            'help_text': _(
                'Generated access token used to make API calls '
                'without going through the OAuth authorization flow.'
            ), 'kwargs': {
                'max_length': 248
            }, 'required': True
        },
    }
    label = _('OAuth access token')
    widgets = {
        'access_token': {
            'class': 'django.forms.widgets.PasswordInput',
            'kwargs': {
                'render_value': True
            }
        }
    }


class GoogleServiceAccount(CredentialBackend):
    @classmethod
    def post_processing(cls, obj):
        for key, value in obj.items():
            obj[key] = value.replace('\\n', '\n')

        return obj

    field_order = (
        'project_id', 'private_key_id', 'private_key', 'client_email',
        'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url',
        'client_x509_cert_url'
    )
    fields = {
        'project_id': {
            'label': _('Project ID'),
            'class': 'django.forms.CharField', 'default': '',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'private_key_id': {
            'label': _('Private Key ID'),
            'class': 'django.forms.CharField', 'default': '',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'private_key': {
            'label': _('Private Key'),
            'class': 'django.forms.CharField', 'default': '',
        },
        'client_email': {
            'label': _('Client email'),
            'class': 'django.forms.CharField', 'default': '',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'client_id': {
            'label': _('Client ID'),
            'class': 'django.forms.CharField', 'default': '',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'auth_uri': {
            'label': _('Authentication URI'),
            'class': 'django.forms.CharField', 'default': 'https://accounts.google.com/o/oauth2/auth',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'token_uri': {
            'label': _('Token URI'),
            'class': 'django.forms.CharField', 'default': 'https://oauth2.googleapis.com/token',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'auth_provider_x509_cert_url': {
            'label': _('X509 certificate provider URL'),
            'class': 'django.forms.CharField', 'default': 'https://www.googleapis.com/oauth2/v1/certs',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
        'client_x509_cert_url': {
            'label': _('Client X509 certificate URL'),
            'class': 'django.forms.CharField', 'default': '',
            'kwargs': {
                'max_length': 254
            }, 'required': True
        },
    }
    label = _('Google Service Account')
    widgets = {
        'private_key': {
            'class': 'django.forms.widgets.Textarea',
        }
    }


class UsernamePassword(CredentialBackend):
    class_fields = ('username', 'password',)
    field_order = ('username', 'password',)
    fields = {
        'username': {
            'label': _('Username'),
            'class': 'django.forms.CharField', 'default': '',
            'help_text': _(
                'Pseudonym used to identify a user.'
            ), 'kwargs': {
                'max_length': 254
            }, 'required': False
        }, 'password': {
            'label': _('Password'),
            'class': 'django.forms.CharField', 'default': '',
            'help_text': _(
                'Character string used to authenticate the user.'
            ), 'kwargs': {
                'max_length': 192
            }, 'required': False
        },
    }
    label = _('Username and password')
    widgets = {
        'password': {
            'class': 'django.forms.widgets.PasswordInput',
            'kwargs': {
                'render_value': True
            }
        }
    }
