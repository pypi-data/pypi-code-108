# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""
WSGI config for yangsuite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from yangsuite.settings.base import prefs

os.environ.setdefault("DJANGO_SETTINGS_MODULE", prefs.get('settings_module'))

application = get_wsgi_application()
