#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.contrib import admin

from nobinobi_daily_follow_up.models import Meal, Lotion, Presence, DailyFollowUp, Nap, DiaperChange, Reception, \
    GiveMedication, MealDailyFollowUp, Medication, TypeMedication, LotionDailyFollowUp, ActivityGroup, TypeActivity, \
    Activity, Troubleshooting, DailyFollowUpToMedication, EarlyTroubleshooting


class DiaperChangeInline(admin.TabularInline):
    model = DiaperChange
    fields = ("hour", "feces",)
    # define the sortable
    # sortable_field_name = "position"
    # define sortable_excludes
    # sortable_excludes = ("field_1", "field_2",)


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    """
        Admin View for Presence
    """
    list_display = ('child', 'classroom', 'date', 'arrival_time', 'departure_time')
    list_filter = ('date', 'classroom')
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('date', 'child__first_name', 'child__last_name', 'classroom__name')


@admin.register(DailyFollowUp)
class DailyFollowUpAdmin(admin.ModelAdmin):
    """
        Admin View for DailyFollowUp
    """
    list_display = ('presence', 'important')
    # list_filter = ('date', 'classroom')
    inlines = [
        DiaperChangeInline,
    ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    # search_fields = ('date', 'child', 'classroom')


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    """
        Admin View for Meal
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Lotion)
class LotionAdmin(admin.ModelAdmin):
    """
        Admin View for Lotion
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Nap)
class NapAdmin(admin.ModelAdmin):
    """
        Admin View for Nap
    """
    list_display = ('daily_follow_up', 'start_time', 'end_time')
    search_fields = ('daily_follow_up', 'start_time', 'end_time')


@admin.register(DiaperChange)
class DiaperChangeAdmin(admin.ModelAdmin):
    """
        Admin View for DiaperChange
    """
    list_display = ('daily_follow_up', 'hour', 'feces')
    search_fields = ('daily_follow_up', 'hour', 'feces')


@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    """
        Admin View for Reception
    """
    list_display = (
        'daily_follow_up', 'wake_up_time', 'sleep', 'breakfast', 'breakfast_time', 'condition', 'fever', 'sick')
    search_fields = ('daily_follow_up', 'sleep', 'breakfast', 'condition', 'fever', 'sick')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """
        Admin View for Activity
    """
    list_display = ('daily_follow_up', 'type_activity',)
    search_fields = ('daily_follow_up', 'type_activity', 'comment')


@admin.register(TypeActivity)
class TypeActivityAdmin(admin.ModelAdmin):
    """
        Admin View for TypeActivity
    """
    list_display = ('name', 'group', 'order')
    search_fields = ('name', 'group', 'order')


@admin.register(ActivityGroup)
class ActivityGroupAdmin(admin.ModelAdmin):
    """
        Admin View for ActivityGroup
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TypeMedication)
class TypeMedicationAdmin(admin.ModelAdmin):
    """
        Admin View for TypeMedication
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(GiveMedication)
class GiveMedicationAdmin(admin.ModelAdmin):
    """
        Admin View for GiveMedication
    """
    list_display = (
        'medication', 'staff', 'give_hour', 'given_hour')
    search_fields = (
        'medication', 'staff', 'give_hour', 'given_hour')


@admin.register(MealDailyFollowUp)
class MealDailyFollowUpAdmin(admin.ModelAdmin):
    """
        Admin View for MealDailyFollowUp
    """
    list_display = (
        'daily_follow_up', 'snack_time', 'snack_quality', 'lunch_time', 'lunch_quality', 'afternoon_snack_time',
        'afternoon_snack_quality')
    search_fields = (
        'daily_follow_up', 'snack_time', 'snack_quality', 'lunch_time', 'lunch_quality', 'afternoon_snack_time',
        'afternoon_snack_quality')


@admin.register(LotionDailyFollowUp)
class LotionDailyFollowUpAdmin(admin.ModelAdmin):
    """
        Admin View for LotionDailyFollowUp
    """
    list_display = (
        'daily_follow_up', 'lotion',)
    search_fields = (
        'daily_follow_up', 'lotion', 'comment')


@admin.register(DailyFollowUpToMedication)
class DailyFollowUpToMedicationAdmin(admin.ModelAdmin):
    """
        Admin View for DailyFollowUpToMedication
    """
    list_display = ('daily_follow_up', 'medication',)
    search_fields = ('daily_follow_up', 'medication',)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    """
        Admin View for Medicationé
    """
    list_display = (
        'child', 'from_date', 'end_date', 'type_medication', 'attachment',)
    search_fields = ('type_medication', 'comment',)


@admin.register(Troubleshooting)
class TroubleshootingAdmin(admin.ModelAdmin):
    """
        Admin View for Troubleshooting
    """
    list_display = (
        'daily_follow_up',)
    search_fields = (
        'daily_follow_up', "periods",)


@admin.register(EarlyTroubleshooting)
class EarlyTroubleshootingAdmin(admin.ModelAdmin):
    """
        Admin View for EarlyTroubleshooting
    """
    list_display = (
        'date', 'child')
    search_fields = (
        'daily_follow_up', "periods",)
