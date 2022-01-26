from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from .admin_site import mocca_lists_admin
from .models import (
    ArvDrugs,
    ArvRegimens,
    CholTreatments,
    ClinicServices,
    Conditions,
    DmTreatments,
    DrugPaySources,
    HtnTreatments,
    MoccaOriginalSites,
    NonAdherenceReasons,
    OffstudyReasons,
    ReasonsForTesting,
    RefillConditions,
    RxModificationReasons,
    RxModifications,
    SubjectVisitMissedReasons,
    TransportChoices,
    VisitReasons,
)


@admin.register(MoccaOriginalSites, site=mocca_lists_admin)
class MoccaOriginalSitesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(TransportChoices, site=mocca_lists_admin)
class TransportChoicesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(DrugPaySources, site=mocca_lists_admin)
class DrugPaySourcesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SubjectVisitMissedReasons, site=mocca_lists_admin)
class SubjectVisitMissedReasonsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(RefillConditions, site=mocca_lists_admin)
class RefillConditionsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ReasonsForTesting, site=mocca_lists_admin)
class ReasonsForTestingAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(NonAdherenceReasons, site=mocca_lists_admin)
class NonAdherenceReasonsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Conditions, site=mocca_lists_admin)
class ConditionsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(OffstudyReasons, site=mocca_lists_admin)
class OffstudyReasonsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(HtnTreatments, site=mocca_lists_admin)
class HtnTreatmentsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(CholTreatments, site=mocca_lists_admin)
class CholTreatmentsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ArvRegimens, site=mocca_lists_admin)
class ArvRegimensAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(VisitReasons, site=mocca_lists_admin)
class VisitReasonsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(DmTreatments, site=mocca_lists_admin)
class DmTreatmentsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ClinicServices, site=mocca_lists_admin)
class ClinicServicesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ArvDrugs, site=mocca_lists_admin)
class ArvDrugsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(RxModifications, site=mocca_lists_admin)
class RxModificationsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(RxModificationReasons, site=mocca_lists_admin)
class RxModificationReasonsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
