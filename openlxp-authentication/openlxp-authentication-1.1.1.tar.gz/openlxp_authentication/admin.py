from django.contrib import admin

from .models import SAMLConfiguration


@admin.register(SAMLConfiguration)
class SAMLConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_id',)
