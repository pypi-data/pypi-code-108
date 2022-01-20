# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""
Yangsuite forms overriding base user account registration/login forms
"""
# Copyright 2016 Cisco Systems, Inc

from django.contrib.auth import get_user_model
from django.conf import settings
from django_registration.forms import RegistrationForm

User = get_user_model()


class YsUserRegistrationForm(RegistrationForm):
    """Custom user registration form handling. Default registration makes
    email mandatory but we need to support both options - explicit email id by
    the user or derived from the username@domain values from the settings
    """
    def __init__(self, *args, **kwargs):
        super(YsUserRegistrationForm, self).__init__(*args, **kwargs)
        email_field = User.get_email_field_name()
        if hasattr(settings, 'REGISTRATION_EMAIL_DOMAIN'):
            self.fields[email_field].required = False

    def save(self, commit=True):
        # Get a form instance without actually saving its backing model
        instance = super(YsUserRegistrationForm, self).save(commit=False)

        email_field = User.get_email_field_name()
        email = getattr(instance, email_field, None)
        username = getattr(instance, User.USERNAME_FIELD)

        if not email:
            # Currently no email means we derive that from the default email
            # domain setting.
            domain = settings.REGISTRATION_EMAIL_DOMAIN
            setattr(instance, email_field, "{0}@{1}".format(username, domain))

        if commit:
            instance.save()

        return instance
