from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "mocca_consent"
    verbose_name = "MOCCA: Consent"
    include_in_administration_section = True
    has_exportable_data = True
