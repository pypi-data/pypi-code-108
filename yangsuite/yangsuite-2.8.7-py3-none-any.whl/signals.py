# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

import os.path
import shutil
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.db.models.signals import post_delete
from yangsuite.paths import get_path
from django_registration.signals import user_activated


@receiver(user_logged_in)
def login_user_path_check(sender, **kwargs):
    """When a user logs in, ensure their user directory exists or create it."""
    user = kwargs.get('user')
    if user is not None and user.is_active:
        get_path('user', user=user.username, create=True)


@receiver(post_delete, sender=get_user_model())
def delete_user_path(sender, **kwargs):
    """After deleting a user, delete their user directory too."""
    user = kwargs.get('instance')
    if user is not None:
        path = get_path('user', user=user.username)
        if os.path.isdir(path):
            shutil.rmtree(path)


@receiver(user_activated)
def post_activation_tasks(sender, **kwargs):
    """List of tasks to execute on user activation"""
    user = kwargs.get('user')
    request = kwargs.get('request')

    # Add the user to groups as indicated by settings.py
    for g in getattr(settings, 'REGISTRATION_USER_GROUPS', []):
        group = Group.objects.filter(name=g)
        if group:
            user.groups.add(group.first())

    # Does YangSuite admin need to know about activation ?
    inform_admin = getattr(settings, 'REGISTRATION_INFORM_ADMIN', False)
    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if inform_admin and admin_email:
        subject = "YangSuite account creation notification"
        context = {
            'server': request.get_host(),
            'username': user.username,
            'email': user.email
        }
        message = render_to_string(
            template_name="django_registration/inform_admin_email_body.txt",
            context=context,
            request=request
        )

        from_email = "YangSuite <no-reply@{0}>".format(request.get_host())
        to_email = admin_email

        send_mail(subject, message, from_email, [to_email], fail_silently=True)
