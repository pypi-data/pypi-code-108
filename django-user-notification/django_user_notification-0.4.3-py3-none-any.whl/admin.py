from django.contrib import admin
from . import models

from .models import Notification
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.


class NotificationAdmin(GenericTabularInline):
    model = models.Notification
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("to")


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "code", "title", "text", "kwargs")
    list_filter = ("name", "code")
    ordering = ("name",)


@admin.register(models.DingDingMessage)
class DingDingMessageAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "content",
        "at_mobiles",
        "is_at_all",
        "extra",
        "created_at",
    ]
    list_filter = ("title", "created_at")
    inlines = (NotificationAdmin,)
    ordering = ("-id",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("notify")


@admin.register(models.EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "sender",
        "receivers",
        "cc",
        "content_subtype",
        "content",
        "created_at",
    ]
    list_filter = ("subject", "content_subtype", "created_at")
    inlines = (NotificationAdmin,)
    ordering = ("-id",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("notify")


@admin.register(models.WebsocketMessage)
class WebsocketMessageAdmin(admin.ModelAdmin):
    list_display = ["title", "content", "msgtype", "groups", "created_at"]
    inlines = (NotificationAdmin,)
    ordering = ("-id",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("notify")
