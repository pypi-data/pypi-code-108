from django.contrib import admin

from masterful_gui.backend.apps.api import models


class PolicySearchTaskAdmin(admin.ModelAdmin):
  list_display = ['policy_name']


admin.site.register(models.PolicySearchTask, PolicySearchTaskAdmin)
