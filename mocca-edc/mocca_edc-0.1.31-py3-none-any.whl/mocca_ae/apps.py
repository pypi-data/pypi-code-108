from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "mocca_ae"
    verbose_name = "MOCCA: Adverse Events"
    include_in_administration_section = True
    has_exportable_data = True
