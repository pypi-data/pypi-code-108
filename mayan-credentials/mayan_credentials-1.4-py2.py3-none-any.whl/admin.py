from django.contrib import admin

from .models import StoredCredential


@admin.register(StoredCredential)
class StoredCredentialAdmin(admin.ModelAdmin):
    list_display = ('label', 'internal_name')
