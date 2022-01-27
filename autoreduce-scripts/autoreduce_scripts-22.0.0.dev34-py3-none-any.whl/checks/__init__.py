# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

import django
from django.conf import settings
from autoreduce_scripts.autoreduce_django.settings import DATABASES, INSTALLED_APPS


def setup_django():
    """
    Sets up django if not configured already. This allows accessing the models through the ORM
    """

    if not settings.configured:
        settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS, USE_TZ=True)
        django.setup()


setup_django()
