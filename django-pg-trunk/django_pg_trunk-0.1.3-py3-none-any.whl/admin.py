from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ValidationError

from django_pg_trunk.models import QueryStatistic
from django_pg_trunk.utils import get_current_database_id


class DbidListFilter(admin.SimpleListFilter):
    parameter_name = "dbid"

    def __init__(self, request, params, model, model_admin):
        self.title = "Database OID"
        super().__init__(request, params, model, model_admin)

    def expected_parameters(self):
        return ["dbid"]

    def lookups(self, request, model_admin):
        values = model_admin.model.objects.distinct("dbid").order_by("dbid").values_list("dbid", flat=True)
        lookups = []
        for value in values:
            verbose_name = str(value)
            if value == get_current_database_id():
                verbose_name += " (Current Database)"

            lookups.append((value, verbose_name))
        return lookups

    def queryset(self, request, queryset):
        try:
            return queryset.filter(**self.used_parameters)
        except (ValueError, ValidationError) as e:
            # Fields may raise a ValueError or ValidationError when converting
            # the parameters to the correct type.
            raise IncorrectLookupParameters(e)


class QueryStatisticAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Statement", {
            "fields": ("userid", "dbid", "query", "rows", "calls",)
        }),
        ("Exec Time", {
            "fields": ("total_exec_time", "min_exec_time", "max_exec_time", "mean_exec_time", "stddev_exec_time",)
        }),
        ("Plans", {
            "fields": ("plans", "total_plan_time", "min_plan_time", "max_plan_time", "mean_plan_time", "stddev_plan_time",)
        }),
        ("Shared Blocks", {
            "fields": ("shared_blks_hit", "shared_blks_read", "shared_blks_dirtied", "shared_blks_written",)
        }),
        ("Local Blocks", {
            "fields": ("local_blks_hit", "local_blks_read", "local_blks_dirtied", "local_blks_written",)
        }),
        ("Temp Blocks", {
            "fields": ("temp_blks_read", "temp_blks_written",)
        }),
        ("Block Read/Write", {
            "fields": ("blk_read_time", "blk_write_time",)
        }),
        ("WAL", {
            "fields": ("wal_records", "wal_fpi", "wal_bytes",)
        }),
    )
    list_display = ("queryid", "dbid", "userid", "query", "mean_exec_time", "rows", "calls",)
    search_fields = ("query",)
    list_filter = (DbidListFilter,)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_changelist(self, request, **kwargs):
        class QueryStatisticChangeList(ChangeList):
            def url_for_result(self, result):
                url = super().url_for_result(result)
                return url.replace(str(result.queryid), f"{result.queryid}_{result.dbid}_{result.userid}")

        return QueryStatisticChangeList

    def get_object(self, request, object_id, from_field=None):
        queryset = self.get_queryset(request)
        queryid, dbid, userid = object_id.split("_")
        try:
            return queryset.get(queryid=queryid, dbid=dbid, userid=userid)
        except (queryset.model.DoesNotExist, ValidationError, ValueError):
            return None


admin.site.register(QueryStatistic, QueryStatisticAdmin)
