from .functions import load_func
from django.conf import settings
ERROR_CALLBACK = getattr(settings, "CFDI_ERROR_CALLBACK", None)
POST_TIMBRADO_CALLBACK = getattr(settings, "CFDI_POST_TIMBRADO_CALLBACK", None)

if ERROR_CALLBACK:
    ERROR_CALLBACK = load_func(ERROR_CALLBACK)

if POST_TIMBRADO_CALLBACK:
    POST_TIMBRADO_CALLBACK = load_func(POST_TIMBRADO_CALLBACK)