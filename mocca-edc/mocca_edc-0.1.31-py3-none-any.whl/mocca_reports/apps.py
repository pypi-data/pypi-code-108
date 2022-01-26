from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig


class AppConfig(DjangoAppConfig):
    name = "inte_reports"


if settings.APP_NAME == "inte_reports":
    from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = "uganda"
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]),
        }
