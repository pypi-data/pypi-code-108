from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.shortcuts import redirect, render
from django.utils.html import format_html
from eveuniverse.models import EveType

from . import tasks
from .constants import EVE_CATEGORY_ID_SHIP
from .models import (
    Character,
    CharacterUpdateStatus,
    EveShipType,
    EveSkillType,
    Location,
    SkillSet,
    SkillSetGroup,
    SkillSetSkill,
)


class EveUniverseEntityModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    ordering = ["name"]
    search_fields = ["name"]


@admin.register(EveShipType)
class EveShipTypeAdmin(EveUniverseEntityModelAdmin):
    pass


@admin.register(EveSkillType)
class EveSkillTypeAdmin(EveUniverseEntityModelAdmin):
    pass


class UpdateStatusOkFilter(admin.SimpleListFilter):
    title = "Update Status OK"
    parameter_name = "update_status_ok"

    def lookups(self, request, model_admin):
        return (("Errors", "Has errors"),)

    def queryset(self, request, queryset):
        if self.value() == "Errors":
            return Character.objects.filter(
                update_status_set__is_success=False
            ).distinct()
        else:
            return Character.objects.all()


class SyncStatusAdminInline(admin.TabularInline):
    model = CharacterUpdateStatus
    fields = (
        "section",
        "is_success",
        "last_error_message",
        "started_at",
        "finished_at",
        "root_task_id",
    )
    ordering = ["section"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("authentication/css/admin.css",)}

    list_display = (
        "_character_pic",
        "_character",
        "_main",
        "_state",
        "_organization",
        "created_at",
        "_last_update_at",
        "_last_update_ok",
        "_missing_sections",
    )
    list_display_links = (
        "_character_pic",
        "_character",
    )
    list_filter = (
        UpdateStatusOkFilter,
        "created_at",
        "character_ownership__user__profile__state",
        "character_ownership__user__profile__main_character__corporation_name",
        "character_ownership__user__profile__main_character__alliance_name",
    )
    list_select_related = (
        "character_ownership__user",
        "character_ownership__user__profile__main_character",
        "character_ownership__user__profile__state",
        "character_ownership__character",
    )
    ordering = ["character_ownership__character__character_name"]
    search_fields = ["character_ownership__character__character_name"]
    exclude = ("mailing_lists",)

    def get_actions(self, request):
        """Remove the default delete action from the drop-down."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def _character_pic(self, obj):
        character = obj.character_ownership.character
        return format_html(
            '<img src="{}" class="img-circle">', character.portrait_url(size=32)
        )

    _character_pic.short_description = ""

    def _character(self, obj):
        return obj.character_ownership.character

    _character.admin_order_field = "character_ownership__character__character_name"

    def _main(self, obj):
        try:
            return obj.character_ownership.user.profile.main_character
        except AttributeError:
            return None

    _main.admin_order_field = "character_ownership__user__profile__main_character"

    def _state(self, obj):
        return obj.character_ownership.user.profile.state

    _main.admin_order_field = "character_ownership__user__profile__state__name"

    def _organization(self, obj):
        try:
            main = obj.character_ownership.user.profile.main_character
            return "{}{}".format(
                main.corporation_name,
                f" [{main.alliance_ticker}]" if main.alliance_ticker else "",
            )
        except AttributeError:
            return None

    _organization.admin_order_field = (
        "character_ownership__user__profile__main_character__corporation_name"
    )

    def _last_update_ok(self, obj):
        return obj.is_update_status_ok()

    def _last_update_at(self, obj):
        latest_obj = obj.update_status_set.latest("finished_at")
        return latest_obj.finished_at

    _last_update_ok.boolean = True

    def _missing_sections(self, obj):
        existing = set(obj.update_status_set.values_list("section", flat=True))
        all_sections = set(Character.UpdateSection.values)
        missing = all_sections.difference(existing)
        if missing:
            return sorted([Character.UpdateSection.display_name(x) for x in missing])

        return None

    actions = [
        "delete_characters",
        "update_characters",
        "update_assets",
        "update_location",
        "update_online_status",
    ]

    def delete_characters(self, request, queryset):
        if "apply" in request.POST:
            for obj in queryset:
                tasks.delete_character.delay(character_pk=obj.pk)
            self.message_user(
                request,
                f"Started deleting {queryset.count()} character(s). "
                "This can take a minute.",
            )
            return redirect(request.get_full_path())
        else:
            return render(
                request,
                "admin/confirm_character_deletion.html",
                {
                    "title": "Are you sure you want to delete these characters?",
                    "queryset": queryset.all(),
                },
            )

    delete_characters.short_description = "Delete selected characters"

    def update_characters(self, request, queryset):
        for obj in queryset:
            tasks.update_character.delay(character_pk=obj.pk, force_update=True)
            self.message_user(request, f"Started updating character: {obj}. ")

    update_characters.short_description = "Update selected characters from EVE server"

    def update_assets(self, request, queryset):
        for obj in queryset:
            tasks.update_character_assets.delay(character_pk=obj.pk, force_update=True)
            self.message_user(
                request, f"Started updating assets for character: {obj}. "
            )

    update_assets.short_description = (
        "Update assets for selected characters from EVE server"
    )

    def update_location(self, request, queryset):
        section = Character.UpdateSection.LOCATION
        for obj in queryset:
            tasks.update_character_section.delay(character_pk=obj.pk, section=section)
            self.message_user(
                request,
                f"Started updating {Character.UpdateSection.display_name(section)} for character: {obj}. ",
            )

    update_location.short_description = (
        f"Update {Character.UpdateSection.display_name(Character.UpdateSection.LOCATION)} "
        "for selected characters from EVE server"
    )

    def update_online_status(self, request, queryset):
        section = Character.UpdateSection.ONLINE_STATUS
        for obj in queryset:
            tasks.update_character_section.delay(character_pk=obj.pk, section=section)
            self.message_user(
                request,
                f"Started updating {Character.UpdateSection.display_name(section)} for character: {obj}. ",
            )

    update_online_status.short_description = (
        "Update "
        f"{Character.UpdateSection.display_name(Character.UpdateSection.ONLINE_STATUS)} "
        "for selected characters from EVE server"
    )

    inlines = (SyncStatusAdminInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("_name", "_type", "_group", "_solar_system", "updated_at")
    list_filter = (
        ("eve_type__eve_group", admin.RelatedOnlyFieldListFilter),
        ("eve_type", admin.RelatedOnlyFieldListFilter),
        (
            "eve_solar_system__eve_constellation__eve_region",
            admin.RelatedOnlyFieldListFilter,
        ),
        ("eve_solar_system", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ["name"]
    list_select_related = (
        "eve_type__eve_group",
        "eve_type",
        "eve_solar_system__eve_constellation__eve_region",
        "eve_solar_system",
    )
    ordering = ["name"]

    def _name(self, obj):
        return obj.name_plus

    _name.admin_order_field = "name"

    def _solar_system(self, obj):
        return obj.eve_solar_system.name if obj.eve_solar_system else None

    _solar_system.admin_order_field = "eve_solar_system__name"

    def _type(self, obj):
        return obj.eve_type.name if obj.eve_type else None

    _type.admin_order_field = "eve_type__name"

    def _group(self, obj):
        return obj.eve_type.eve_group.name if obj.eve_type else None

    _group.admin_order_field = "eve_type__eve_group__name"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SkillSetGroup)
class SkillSetGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "_skill_sets", "is_doctrine", "is_active")
    list_filter = (
        "is_doctrine",
        "is_active",
        ("skill_sets", admin.RelatedOnlyFieldListFilter),
    )
    ordering = ["name"]
    filter_horizontal = ("skill_sets",)

    def _skill_sets(self, obj):
        return [x.name for x in obj.skill_sets.all().order_by("name")]


class MinValidatedInlineMixIn:
    validate_min = True

    def get_formset(self, *args, **kwargs):
        return super().get_formset(validate_min=self.validate_min, *args, **kwargs)


class SkillSetSkillAdminFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            try:
                data = self.cleaned_data
            except AttributeError:
                pass
            else:
                for row in data:
                    if (
                        row
                        and row.get("DELETE") is False
                        and not row.get("required_level")
                        and not row.get("recommended_level")
                    ):
                        eve_type = row.get("eve_type")
                        raise ValidationError(
                            f"Skill '{eve_type.name}' must have a level."
                        )


class SkillSetSkillAdminInline(MinValidatedInlineMixIn, admin.TabularInline):
    model = SkillSetSkill
    verbose_name = "skill"
    verbose_name_plural = "skills"
    min_num = 1
    formset = SkillSetSkillAdminFormSet
    autocomplete_fields = ("eve_type",)


class SkillSetShipTypeFilter(admin.SimpleListFilter):
    title = "is ship type"
    parameter_name = "is_ship_type"

    def lookups(self, request, model_admin):
        return (
            ("yes", "yes"),
            ("no", "no"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return SkillSet.objects.filter(ship_type__isnull=False)
        if self.value() == "no":
            return SkillSet.objects.filter(ship_type__isnull=True)
        return SkillSet.objects.all()


@admin.register(SkillSet)
class SkillSetAdmin(admin.ModelAdmin):
    autocomplete_fields = ("ship_type",)
    list_display = (
        "name",
        "ship_type",
        "_skills",
        "_groups",
        "is_visible",
    )
    list_filter = (
        SkillSetShipTypeFilter,
        "is_visible",
        ("groups", admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ("ship_type",)
    ordering = ["name"]
    search_fields = ["name"]

    def _skills(self, obj):
        return [
            "{} {} {}".format(
                x.eve_type.name,
                x.required_level if x.required_level else "",
                f"[{x.recommended_level}]" if x.recommended_level else "",
            )
            for x in obj.skills.select_related("eve_type")
            .all()
            .order_by("eve_type__name")
        ]

    def _groups(self, obj) -> list:
        groups = [f"{x.name}" for x in obj.groups.all().order_by("name")]
        return groups if groups else None

    inlines = (SkillSetSkillAdminInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ship_type":
            kwargs["queryset"] = (
                EveType.objects.select_related("eve_group__eve_category")
                .filter(eve_group__eve_category=EVE_CATEGORY_ID_SHIP)
                .order_by("name")
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
        tasks.update_characters_skill_checks.delay(force_update=True)

    def delete_model(self, request, obj):
        obj.user = request.user
        super().delete_model(request, obj)
        tasks.update_characters_skill_checks.delay(force_update=True)
