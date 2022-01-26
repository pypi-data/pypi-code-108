from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from edc_constants.constants import NO, YES


class ScreenedListFilter(admin.SimpleListFilter):
    title = _("Screened")

    parameter_name = "screened"

    def lookups(self, request, model_admin):
        return (
            (YES, _("Yes")),
            (NO, _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == YES:
            return queryset.filter(screening_identifier__isnull=False)
        if self.value() == NO:
            return queryset.filter(screening_identifier__isnull=True)


class CallListFilter(admin.SimpleListFilter):
    title = _("Call")

    parameter_name = "call_patient"

    def lookups(self, request, model_admin):
        return (
            (YES, _("Yes")),
            (NO, _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == YES:
            return queryset.filter(screening_identifier__isnull=True, call=YES)
        if self.value() == NO:
            return queryset.filter(call=NO)


class ContactAttemptsListFilter(admin.SimpleListFilter):
    title = _("Contact")

    parameter_name = "contact"

    def lookups(self, request, model_admin):
        return (
            (0, _("0 attempts")),
            (1, _("1 attempt")),
            (2, _("2 attempts")),
            (3, _("3 attempts")),
            (4, _("4+ attempts")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            if int(self.value()) == 0:
                return queryset.filter(contact_attempts=0)
            if 0 < int(self.value()) <= 3:
                return queryset.filter(contact_attempts=int(self.value()))
            if int(self.value()) > 3:
                return queryset.filter(contact_attempts__gte=int(self.value()))
