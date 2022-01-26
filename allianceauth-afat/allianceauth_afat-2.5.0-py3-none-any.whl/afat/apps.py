"""
App config
"""

# Django
from django.apps import AppConfig

# Alliance Auth AFAT
from afat import __version__


class AfatConfig(AppConfig):
    """
    General config
    """

    name = "afat"
    label = "afat"
    verbose_name = f"AFAT - Another Fleet Activity Tracker v{__version__}"
