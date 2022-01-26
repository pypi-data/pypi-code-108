from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from mocca_lists.models import ArvRegimens

from ..admin_site import mocca_subject_admin


@admin.register(ArvRegimens, site=mocca_subject_admin)
class ArvRegimensAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
