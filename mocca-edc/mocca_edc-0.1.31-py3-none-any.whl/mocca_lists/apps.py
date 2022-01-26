from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "mocca_lists"
    verbose_name = "MOCCA: Lists"
    include_in_administration_section = True
    has_exportable_data = True
