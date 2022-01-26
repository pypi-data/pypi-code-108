from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "mocca_subject"
    verbose_name = "MOCCA: Subject (CRFs)"
    include_in_administration_section = True
    has_exportable_data = True
