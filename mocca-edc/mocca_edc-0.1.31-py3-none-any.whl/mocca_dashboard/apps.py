from datetime import datetime

from dateutil.tz.tz import gettz
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = "mocca_dashboard"
    admin_site_name = "inte_test_admin"
    include_in_administration_section = False


if settings.APP_NAME == "mocca_dashboard":
    from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_identifier.apps import AppConfig as BaseEdcIdentifierAppConfig
    from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig
    from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig

    class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
        protocol = "EDC093"
        protocol_name = "INTE"
        protocol_number = "093"
        protocol_title = ""
        study_open_datetime = datetime(2019, 7, 31, 0, 0, 0, tzinfo=gettz("UTC"))
        study_close_datetime = datetime(2022, 12, 31, 23, 59, 59, tzinfo=gettz("UTC"))

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = "uganda"
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]),
        }

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {"mocca_subject": ("subject_visit", "mocca_subject.subjectvisit")}

    class EdcIdentifierAppConfig(BaseEdcIdentifierAppConfig):
        identifier_prefix = "093"

    class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):
        reason_field = {"mocca_subject.subjectvisit": "reason"}
