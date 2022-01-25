# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import csv

from django import forms
from django.http import HttpResponse
from django.contrib import admin

from .common import read_settings


SUNSHINE_ENV = read_settings('SUNSHINE_ENV', 'DEV')
admin.site.site_header = read_settings('ADMIN_SITE_HEADER', f'{SUNSHINE_ENV} Sunshine Admin Portal')
admin.site.site_title = read_settings('ADMIN_SITE_TITLE', f'Sunshine-{SUNSHINE_ENV}')
admin.site.index_title = read_settings('ADMIN_SITE_INDEX_TITLE', 'Sunshine Portal administrator site')


class ExportCsvMixin:

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export selected"


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
