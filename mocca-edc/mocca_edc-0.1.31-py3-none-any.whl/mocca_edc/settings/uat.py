from multisite import SiteID

from .defaults import *  # noqa

print(f"Settings file {__file__}")  # noqa

SITE_ID = SiteID(default=1)
EDC_SITES_UAT_DOMAIN = True
ALLOWED_HOSTS = [
    "amana.uat.tz.mocca.clinicedc.org",
    "bunju.uat.tz.mocca.clinicedc.org",
    "hindu-mandal.uat.tz.mocca.clinicedc.org",
    "kisugu.uat.ug.mocca.clinicedc.org",
    "kiswa.uat.ug.mocca.clinicedc.org",
    "mkuranga.uat.tz.mocca.clinicedc.org",
    "mulago.uat.ug.mocca.clinicedc.org",
    "mwananyamala.uat.tz.mocca.clinicedc.org",
    "ndejje.uat.ug.mocca.clinicedc.org",
    "wakiso.uat.ug.mocca.clinicedc.org",
    "localhost",
]
