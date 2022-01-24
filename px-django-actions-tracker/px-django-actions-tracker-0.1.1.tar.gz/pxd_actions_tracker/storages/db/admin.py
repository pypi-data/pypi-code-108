from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = 'id', 'domain', 'message', 'tracking', 'created_at',
    list_display_links = 'id', 'message',
    list_filter = (
        # 'domain',
        'created_at',
    )
    search_fields = 'id', 'domain', 'tracking', 'message', 'detail',
    readonly_fields = 'id', 'domain', 'tracking', 'message', 'created_at',
    date_hierarchy = 'created_at'

    formfield_overrides = {models.JSONField: {'widget': JSONEditorWidget}}
