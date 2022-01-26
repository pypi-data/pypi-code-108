"""
Our app setting
"""

# Third Party
import unidecode

# Django
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

# Alliance Auth (External Libs)
from app_utils.django import clean_setting

# Set default expiry time in minutes
AFAT_DEFAULT_FATLINK_EXPIRY_TIME = clean_setting("AFAT_DEFAULT_FATLINK_EXPIRY_TIME", 60)

# Set the default time in minutes a FAT lnk can be re-opened after it is expired
AFAT_DEFAULT_FATLINK_REOPEN_GRACE_TIME = clean_setting(
    "AFAT_DEFAULT_FATLINK_REOPEN_GRACE_TIME", 60
)

# Set the default time in minutes a FAT link is re-opened for
AFAT_DEFAULT_FATLINK_REOPEN_DURATION = clean_setting(
    "AFAT_DEFAULT_FATLINK_REOPEN_DURATION", 60
)

AFAT_DEFAULT_LOG_DURATION = clean_setting("AFAT_DEFAULT_LOG_DURATION", 60)

# Name of this app, as shown in the Auth sidebar and page titles
AFAT_APP_NAME = clean_setting(
    "AFAT_APP_NAME", _("Fleet Activity Tracking"), required_type=str
)

AFAT_BASE_URL = slugify(unidecode.unidecode(AFAT_APP_NAME), allow_unicode=True)
