#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import gettext as _
from nobinobi_child.models import Period, Allergy, FoodRestriction, Language, Classroom, AgeGroup, Absence, AbsenceType, \
    AbsenceGroup, ClassroomDayOff, InformationOfTheDay, Contact, Address, ChildSpecificNeed, LogChangeClassroom, Child, \
    ChildToPeriod, ChildToContact, ReplacementClassroom
from nobinobi_staff.models import Staff


class DefaultListFilter(SimpleListFilter):
    all_value = '_all'

    def default_value(self):
        raise NotImplementedError()

    def queryset(self, request, queryset):
        if self.parameter_name in request.GET and request.GET[self.parameter_name] == self.all_value:
            return queryset

        if self.parameter_name in request.GET:
            return queryset.filter(**{self.parameter_name: request.GET[self.parameter_name]})

        return queryset.filter(**{self.parameter_name: self.default_value()})

    def choices(self, cl):
        yield {
            'selected': self.value() == self.all_value,
            'query_string': cl.get_query_string({self.parameter_name: self.all_value}, []),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup) or (
                    self.value() == None and force_text(self.default_value()) == force_text(lookup)),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


@register(Period)
class PeriodAdmin(admin.ModelAdmin):
    """
        Admin View for Period
    """
    list_display = ('name', 'weekday', 'order')
    list_filter = ('weekday',)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('name',)
    sortable_by = ("weekday", "order",)


@register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """
        Admin View for Classroom
    """
    list_display = ('name', 'capacity', 'order', 'mode')
    list_filter = ('mode',)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('allowed_login',)
    filter_horizontal = ('allowed_login', 'allowed_group_login')
    readonly_fields = ('slug',)
    search_fields = ('name', 'slug', 'capacity', 'mode')


@register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    """
        Admin View for AgeGroup
    """
    list_display = ('name',)
    readonly_fields = ('slug',)
    search_fields = ('name', 'slug')


@register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    """
        Admin View for Allergy
    """
    list_display = ('name',)
    search_fields = ('name',)


@register(FoodRestriction)
class FoodRestrictionAdmin(admin.ModelAdmin):
    """
        Admin View for FoodRestriction
    """
    list_display = ('name',)
    search_fields = ('name',)


@register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """
        Admin View for Language
    """
    list_display = ('name',)
    search_fields = ('name',)


@register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    """
        Admin View for Absence
    """
    list_display = ('child', 'start_date', 'end_date', 'type')
    list_filter = ('start_date', 'end_date', 'type')
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('child__first_name', 'child__last_name')


@register(AbsenceType)
class AbsenceTypeAdmin(admin.ModelAdmin):
    """
        Admin View for AbsenceType
    """
    list_display = ('name', 'group', 'order')
    list_filter = ('group',)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('name', 'group')


@register(AbsenceGroup)
class AbsenceGroupAdmin(admin.ModelAdmin):
    """
        Admin View for AbsenceGroup
    """
    list_display = ('name',)
    list_filter = ()
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('name',)


class ClassroomInline(admin.TabularInline):
    model = Classroom


@register(ClassroomDayOff)
class ClassroomDayOffAdmin(admin.ModelAdmin):
    """
        Admin View for ClassroomDayOff
    """
    list_display = ('weekday',)
    list_filter = ('weekday',)
    # inlines = [
    #     ClassroomInline,
    # ]
    search_fields = ('weekday',)


@register(InformationOfTheDay)
class InformationOfTheDayAdmin(admin.ModelAdmin):
    """
        Admin View for InformationOfTheDay
    """
    list_display = ('title', 'start_date', 'end_date',)
    list_filter = ('start_date', 'end_date',)
    # /    inlines = [
    #         ClassroomInline,
    #     ]
    search_fields = ('content',)


@register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
        Admin View for InformationOfTheDay
    """
    list_display = ('full_name', 'email', 'phone', 'organisation', 'function')
    list_filter = ('organisation', 'function')
    # /    inlines = [
    #         ClassroomInline,
    #     ]
    search_fields = (
        'first_name', 'last_name', 'phone', 'mobile_phone', 'professional_phone', 'organisation', 'function')


@register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
        Admin View for Address
    """
    list_display = ('street', 'zip', 'city', 'country')
    list_filter = ('zip', 'city', 'country',)
    search_fields = ('street', 'zip', 'city', 'country')


@register(ChildSpecificNeed)
class ChildSpecificNeedAdmin(admin.ModelAdmin):
    """
        Admin View for ChildSpecificNeed
    """
    list_display = ('child', 'ihp', 'attachment')
    list_filter = ('ihp', 'attachment',)
    search_fields = ('problem', 'measure_take', 'child')


@register(LogChangeClassroom)
class LogChangeClassroomAdmin(admin.ModelAdmin):
    """
        Admin View for LogChangeClassroom
    """
    list_display = ('child', 'classroom', 'next_classroom', 'date')
    list_filter = ('classroom', 'next_classroom', 'date')
    search_fields = ('child', 'classroom', 'next_classroom', 'date',)


@register(ReplacementClassroom)
class ReplacementClassroomAdmin(admin.ModelAdmin):
    """
        Admin View for RemplacementClassroom
    """
    list_display = ('from_date', 'end_date', 'child', 'classroom', 'archived')
    list_filter = ('from_date', 'end_date', 'classroom', 'archived')
    search_fields = ('from_date', 'end_date', 'classroom', 'child',)


class ChildToPeriodInline(admin.TabularInline):
    model = ChildToPeriod
    min_num = 0
    extra = 1
    sortable_by = "period__order"
    show_change_link = False
    can_delete = True


class ChildToContactInline(admin.TabularInline):
    model = ChildToContact
    min_num = 0
    extra = 1
    show_change_link = True
    can_delete = True


class ReplacementClassroomInline(admin.TabularInline):
    model = ReplacementClassroom
    min_num = 0
    extra = 1
    show_change_link = True
    can_delete = True


class ChildSpecificNeedInline(admin.TabularInline):
    model = ChildSpecificNeed
    min_num = 0
    max_num = 1
    extra = 0
    show_change_link = True
    can_delete = True


class StatusFilter(DefaultListFilter):
    title = _('Status')
    parameter_name = 'status__exact'

    def lookups(self, request, model_admin):
        return Child.STATUS

    def default_value(self):
        return "in_progress"


@register(Child)
class ChildAdmin(admin.ModelAdmin):
    """
        Admin View for Child
    """
    list_display = (
        'first_name', 'last_name', 'usual_name', 'gender', 'birth_date', 'classroom', 'age_group', 'staff')
    list_filter = (StatusFilter, 'gender', 'classroom', 'age_group', 'staff')

    fieldsets = [
        (_("Personal information"), {
            'fields': ['first_name', 'last_name', 'usual_name', 'gender', 'picture', 'birth_date', 'languages',
                       'nationality',
                       'red_list',
                       'food_restrictions',
                       'sibling_name', 'sibling_birth_date', 'sibling_institution',
                       'comment', 'renewal_date', ]
        }),
        (_('Health info'), {
            'fields': (
                "allergies", "pediatrician", "pediatrician_contact", "usage_paracetamol", "healthy_child",
                "good_development",
                "specific_problem",
                "vaccination",
                "health_insurance"
            )
        }),
        (_('Classroom'), {
            'fields': ('classroom', 'next_classroom', 'date_next_classroom', 'age_group')
        }),
        (_('Staff'), {
            'fields': ['staff']
        }),
        (_('Other'), {
            'fields': ['status', 'slug', 'created', 'modified']
        })]

    inlines = [
        ReplacementClassroomInline,
        ChildToPeriodInline,
        ChildToContactInline,
        ChildSpecificNeedInline,
    ]
    # raw_id_fields = ('',)
    readonly_fields = ('slug', "folder", "created", "modified")
    search_fields = (
        'first_name', 'last_name', 'usual_name', 'birth_date', 'classroom__name', 'next_classroom__name',
        'date_next_classroom',
        'age_group__name', 'staff__first_name', 'staff__last_name')
    actions = ["child_archived"]
    save_as = True
    save_as_continue = True
    save_on_top = True

    def folder(self, x):
        try:
            from nobinobi_sape_contract.models import Folder
        except ModuleNotFoundError as err:
            # Error handling
            pass
        else:
            return Folder.objects.get(child=x)

    folder.short_description = _('Folder')

    def child_archived(self, request, queryset):
        rows_updated = queryset.update(status=Child.STATUS.archived)
        if rows_updated == 1:
            message_bit = _("1 child was")
        else:
            message_bit = _("{} children were").format(rows_updated)
        self.message_user(request, "%s successfully marked as archived." % message_bit)

    child_archived.short_description = _('Put child in archive')

    def response_change(self, request, obj):
        if "_printhealcard" in request.POST:
            return HttpResponseRedirect(reverse("nobinobi_child:print_heal_card", kwargs={"pk": obj.pk}))
        return super().response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ChildAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['staff'].queryset = Staff.objects.filter(status__exact='active')
        return form
