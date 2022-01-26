"""
Constants used in this module
"""

# Django
from django.utils.text import slugify

# Alliance Auth AFAT
from afat import __version__

VERBOSE_NAME = "AFAT Fleet Activity Tracking for Alliance Auth"

verbose_name_slugified: str = slugify(VERBOSE_NAME, allow_unicode=True)
github_url: str = "https://github.com/ppfeufer/allianceauth-afat"

USER_AGENT = f"{verbose_name_slugified} v{__version__} {github_url}"
