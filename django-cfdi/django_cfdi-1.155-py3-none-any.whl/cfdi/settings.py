from django.conf import settings
import os
if not settings.configured:
    settings.configure()

_DEFAULT_PAC_AUTH = {
    "ntlink": {
        "dev": {"usuario": "", "password": ""},
        "prod": {"usuario": "", "password": ""},
    },
    "dfacture": {
        "dev": {"usuario": "", "password": ""},
        "prod": {"usuario": "", "password": ""},
    },
    "prodigia": {
        "dev": {"contrato": "", "usuario": "", "password": ""},
        "prod": {"contrato": "", "usuario": "", "password": ""},
    },

    "sto": {
        "dev": {"contrato": "", "usuario": "", "password": ""},
        "prod": {"contrato": "", "usuario": "", "password": ""},
    },
}


TMP_DIR = getattr(settings, "CFDI_TMP_DIR", "/tmp/")

DFACTURE_AUTH = getattr(
    settings, "CFDI_DFACTURE_AUTH", _DEFAULT_PAC_AUTH.get("dfacture")
)

PRODIGIA_AUTH = getattr(
    settings, "CFDI_PRODIGIA_AUTH", _DEFAULT_PAC_AUTH.get("prodigia")
)

NTLINK_AUTH = getattr(
    settings, "CFDI_NTLINK_AUTH", _DEFAULT_PAC_AUTH.get("ntlink")
)

STO_AUTH = getattr(
    settings, "CFDI_STO_AUTH", _DEFAULT_PAC_AUTH.get("sto")
)

CFDI_DB_TABLE = getattr(settings, "CFDI_DB_TABLE", "cfdi_cfdi")
XML_DIR = getattr(settings, "XML_DIR", "/srv/www/cfd")
XSLT_PATH_CFDI = "{}/xslt/cadenaoriginal_3_3.xslt".format(os.path.dirname(__file__))
XSLT_PATH_TFD = "{}/xslt/cadenaoriginal_3_3.xslt".format(os.path.dirname(__file__))



ERROR_CALLBACK = getattr(settings, "CFDI_ERROR_CALLBACK", None)
POST_TIMBRADO_CALLBACK = getattr(settings, "CFDI_POST_TIMBRADO_CALLBACK", None)