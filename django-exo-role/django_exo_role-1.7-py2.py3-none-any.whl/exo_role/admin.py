from django.contrib import admin

from .models import ExORole, CertificationRole, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'num_roles', 'created')


@admin.register(ExORole)
class ExORoleAdmin(admin.ModelAdmin):
    list_filter = ('categories', )
    list_display = ('name', 'code', 'description', 'created')


@admin.register(CertificationRole)
class CertificationRoleAdmin(admin.ModelAdmin):
    list_filter = ('level', )
    list_display = ('name', 'code', 'level', 'description', 'created')
