# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

# pylint:disable=import-outside-toplevel


def setup_django():
    """Sets up the env to allow access to a django DB"""
    import django
    from django.conf import settings
    from autoreduce_scripts.autoreduce_django.settings import DATABASES, INSTALLED_APPS

    if not settings.configured:
        settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
        django.setup()


setup_django()
