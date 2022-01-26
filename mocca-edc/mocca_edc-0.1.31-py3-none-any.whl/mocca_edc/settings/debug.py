import os  # noqa

from multisite import SiteID

from .defaults import *  # noqa

print(f"Settings file {__file__}")  # noqa

SITE_ID = SiteID(default=122)
EDC_SITES_UAT_DOMAIN = False
DEBUG = True
ALLOWED_HOSTS = [
    # "amana.tz.mocca.clinicedc.org",  # 220
    # "bunju.tz.mocca.clinicedc.org",  # 250
    # "kisugu.ug.mocca.clinicedc.org",  # 119
    # "kiswa.ug.mocca.clinicedc.org",  # 120
    "localhost",
    "127.0.0.1",
]
# comment: comment out if using runserver and folders read from .env
# ETC_DIR = os.path.join(BASE_DIR, "tests", "etc")  # noqa
# KEY_PATH = os.path.join(ETC_DIR, "crypto_fields")  # noqa
# end comment
AUTO_CREATE_KEYS = False
if os.path.exists(BASE_DIR) and not os.path.exists(KEY_PATH):  # noqa
    os.makedirs(KEY_PATH)  # noqa
    AUTO_CREATE_KEYS = True
