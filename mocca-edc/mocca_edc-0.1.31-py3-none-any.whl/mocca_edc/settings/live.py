from multisite import SiteID

from .defaults import *  # noqa

print(f"Settings file {__file__}")  # noqa

SITE_ID = SiteID(default=1)
EDC_SITES_UAT_DOMAIN = False
AUTO_CREATE_KEYS = False
ALLOWED_HOSTS = [
    "amana.tz.mocca.clinicedc.org",
    "bunju.tz.mocca.clinicedc.org",
    "hindu-mandal.tz.mocca.clinicedc.org",
    "kisugu.ug.mocca.clinicedc.org",
    "kiswa.ug.mocca.clinicedc.org",
    "mkuranga.tz.mocca.clinicedc.org",
    "mulago.ug.mocca.clinicedc.org",
    "mwananyamala.tz.mocca.clinicedc.org",
    "ndejje.ug.mocca.clinicedc.org",
    "wakiso.ug.mocca.clinicedc.org",
    "localhost",
]
AUTO_CREATE_KEYS = False
