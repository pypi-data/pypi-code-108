from django.contrib import admin
from django.urls import path

from admin_sso import settings
from admin_sso.models import Assignment


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "weight"]
    raw_id_fields = ["user"]

    def get_urls(self):
        from admin_sso.views import end, start

        info = (self.model._meta.app_label, self.model._meta.model_name)
        return [
            path("start/", start, name="%s_%s_start" % info),
            path("end/", end, name="%s_%s_end" % info),
        ] + super().get_urls()


admin.site.register(Assignment, AssignmentAdmin)


if settings.DJANGO_ADMIN_SSO_ADD_LOGIN_BUTTON:
    admin.site.login_template = "admin_sso/login.html"
