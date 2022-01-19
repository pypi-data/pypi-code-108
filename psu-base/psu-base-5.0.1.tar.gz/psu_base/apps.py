from django.apps import AppConfig
from psu_base.classes.Log import Log
from django.conf import settings

log = Log()


class PsuTemplateConfig(AppConfig):
    name = "psu_base"
    verbose_name = "PSU Base Plugin"

    def ready(self):
        # Use psu_base middleware
        request_middleware = "crequest.middleware.CrequestMiddleware"
        base_middleware = (
            "psu_base.interceptors.psu_base_interceptor_middleware.PsuBaseMiddleware"
        )
        xss_middleware = (
            "psu_base.interceptors.security_interceptor_middleware.xss_prevention"
        )
        for mm in [request_middleware, base_middleware, xss_middleware]:
            if mm not in settings.MIDDLEWARE:
                settings.MIDDLEWARE.append(mm)
