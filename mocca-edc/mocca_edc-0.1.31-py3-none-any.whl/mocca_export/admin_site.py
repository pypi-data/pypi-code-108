from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):

    site_title = "MOCCA Export"
    site_header = "MOCCA Export"
    index_title = "MOCCA Export"
    site_url = "/administration/"
    enable_nav_sidebar = False  # DJ 3.1


mocca_export_admin = AdminSite(name="mocca_export_admin")
