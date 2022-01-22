# -*- coding: utf-8 -*-


from django.contrib import admin
from django.db.models import Q
from django.contrib.admin import SimpleListFilter

from jalali_date import datetime2jalali
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from import_export.admin import ExportActionMixin

from aparnik.settings import aparnik_settings
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields

from .models import Counter

from import_export import resources, fields
# Register your models here.

class CounterResource(resources.ModelResource):
    model = fields.Field()

    class Meta:
        model = Counter
        fields = [
            'id',
            'user_obj__username',
            'model',
            'model_obj__id',
            'update_at',
        ]

    def dehydrate_model(self, counter):
        return counter.model_obj.get_real_instance().get_title()



class ModelFilter(SimpleListFilter):
    title = 'model' # or use _('country') for translated title
    parameter_name = 'model'

    def lookups(self, request, model_admin):
        models = set(['CourseFile', 'Course'])
        return [(c, c) for c in models]

    def queryset(self, request, queryset):
        from aparnik.packages.educations.courses.models import Course, CourseFile
        from aparnik.contrib.basemodels.models import BaseModel
        if self.value() == 'CourseFile':
            return queryset.filter(model_obj_id__in=BaseModel.objects.filter(Q(instance_of=CourseFile)))
        if self.value() == 'Course':
            return queryset.filter(model_obj_id__in=BaseModel.objects.filter(Q(instance_of=Course)))
        return queryset

def get_title(obj):
    return obj.model_obj.get_real_instance().get_title()

get_title.short_description = 'عنوان'

# def get_update_at(obj):
#     return datetime2jalali(obj.update_at).strftime(aparnik_settings.JALALI_FORMAT)

#
# get_update_at.admin_order_field = 'update_at'
# get_update_at.short_description = 'بروز شده'


class CounterAdmin(ExportActionMixin, BaseModelAdmin):
    resource_class = CounterResource
    fields = ['user_obj', 'model_obj', 'action']
    list_display = ['user_obj', 'model_obj', get_title, 'action', 'update_at']
    list_filter = ['action', ('update_at', DateTimeRangeFilter), ModelFilter,]
    search_fields = get_user_search_fields('user_obj') + ['model_obj__id',]
    exclude = []
    raw_id_fields = ['user_obj', 'model_obj']
    dynamic_raw_id_fields = []
    readonly_fields = ['update_at']

    def __init__(self, *args, **kwargs):
        Klass = CounterAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Counter


admin.site.register(Counter, CounterAdmin)
