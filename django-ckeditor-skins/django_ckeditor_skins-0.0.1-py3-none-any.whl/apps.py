"""
app config
"""

# Django
from django.apps import AppConfig

# AA SRP
from ckeditor_skins import __version__


class CkeditorSkinsConfig(AppConfig):
    """
    application config
    """

    name = "ckeditor_skins"
    label = "ckeditor_skins"
    verbose_name = f"Django CKeditor Skins v{__version__}"
