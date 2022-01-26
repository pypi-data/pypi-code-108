from django.contrib import admin
from edc_model_admin import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    SimpleHistoryAdmin,
    TemplatesModelAdminMixin,
)

from ..admin_site import mocca_screening_admin
from ..forms import MoccaRegisterContactForm
from ..models import MoccaRegisterContact


@admin.register(MoccaRegisterContact, site=mocca_screening_admin)
class MoccaRegisterContactAdmin(
    TemplatesModelAdminMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    SimpleHistoryAdmin,
):
    form = MoccaRegisterContactForm
    show_object_tools = False
