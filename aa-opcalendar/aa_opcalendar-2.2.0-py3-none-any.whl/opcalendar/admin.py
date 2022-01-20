from django.contrib import admin
from django.utils.safestring import mark_safe
from opcalendar.models import (
    Event,
    EventCategory,
    WebHook,
    EventHost,
    EventImport,
    Owner,
    IngameEvents,
    EventVisibility,
)
from .forms import EventVisibilityAdminForm, EventCategoryAdminForm


def custom_filter(title):
    """
    custom filter for model properties
    :param title:
    :return:
    """

    class Wrapper(admin.FieldListFilter):
        """
        custom_filter :: wrapper
        """

        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title

            return instance

    return Wrapper


class WebHookAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled")


admin.site.register(WebHook, WebHookAdmin)


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    form = EventCategoryAdminForm
    list_display = (
        "name",
        "ticker",
        "_color",
    )

    def _color(self, obj):
        html = (
            f'<input type="color" value="{obj.color}" disabled>' if obj.color else "-"
        )
        return mark_safe(html)


class EventHostAdmin(admin.ModelAdmin):
    model = EventHost

    list_display = (
        "community",
        "is_default",
        "external",
    )


admin.site.register(EventHost, EventHostAdmin)


@admin.register(EventImport)
class EventImportAdmin(admin.ModelAdmin):
    model = EventImport

    list_display = (
        "source",
        "host",
        "event_visibility",
        "operation_type",
    )


@admin.register(EventVisibility)
class EventVisibilityAdmin(admin.ModelAdmin):
    form = EventVisibilityAdminForm

    list_display = (
        "name",
        "_restricted_to_group",
        "_restricted_to_state",
        "_color",
        "is_default",
        "is_visible",
        "is_active",
    )
    filter_horizontal = ("restricted_to_group",)
    ordering = ("name",)

    list_filter = (
        ("is_active", custom_filter(title="active")),
        ("restricted_to_group", custom_filter(title="restriction")),
    )

    def _color(self, obj):
        html = (
            f'<input type="color" value="{obj.color}" disabled>' if obj.color else "-"
        )
        return mark_safe(html)

    @classmethod
    def _name(cls, obj):
        return obj.name

    _name.short_description = "Visibility"
    _name.admin_order_field = "name"

    @classmethod
    def _restricted_to_group(cls, obj):
        names = [x.name for x in obj.restricted_to_group.all().order_by("name")]

        if names:
            return ", ".join(names)
        else:
            return None

    _restricted_to_group.short_description = "Restricted to"
    _restricted_to_group.admin_order_field = "restricted_to_group__name"

    @classmethod
    def _restricted_to_state(cls, obj):
        names = [x.name for x in obj.restricted_to_state.all().order_by("name")]

        if names:
            return ", ".join(names)
        else:
            return None

    _restricted_to_state.short_description = "Restricted to"
    _restricted_to_state.admin_order_field = "restricted_to_state__name"


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    model = Owner

    list_display = (
        "character",
        "event_visibility",
        "operation_type",
        "is_active",
    )


@admin.register(IngameEvents)
class IngameEventsAdmin(admin.ModelAdmin):
    model = IngameEvents

    list_display = (
        "title",
        "owner_type",
        "owner_name",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    model = Event

    list_display = (
        "title",
        "host",
        "operation_type",
        "event_visibility",
        "external",
    )
