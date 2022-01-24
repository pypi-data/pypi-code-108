from django.utils.translation import ugettext_lazy as _

from pyston.utils.decorators import filter_class, order_by

from is_core.utils.decorators import short_description
from is_core.contrib.elasticsearch.cores import ElasticsearchUiRestCore
from is_core.contrib.elasticsearch.views import ElasticsearchInlineTableView

from security.backends.common.is_core import (
    LogCoreMixin, ChildLogTableViewMixin, InputRequestLogCoreMixin, OutputRequestLogCoreMixin,
    CommandLogCoreMixin, CeleryTaskInvocationLogInlineTableViewMixin, CeleryTaskRunLogInlineTableViewMixin,
    CeleryTaskRunLogCoreMixin, CeleryTaskInvocationLogCoreMixin, BaseRelatedLogsView, RelatedLogInlineTableViewMixin
)
from security.backends.elasticsearch.models import (
    CeleryTaskInvocationLog, CeleryTaskRunLog, CommandLog, InputRequestLog, OutputRequestLog, get_log_from_key,
    get_log_key, get_object_from_key
)

from .filters import UsernameUserFilter, SecurityElasticsearchFilterManager, RelatedObjectsFilter


class ChildLogInlineTableView(ChildLogTableViewMixin, ElasticsearchInlineTableView):

    def _get_log_key(self, log):
        return get_log_key(log)


class OutputRequestLogInlineTableView(ChildLogInlineTableView):

    model = OutputRequestLog


class CommandLogInlineTableView(ChildLogInlineTableView):

    model = CommandLog


class CeleryTaskInvocationLogInlineTableView(ChildLogInlineTableView):

    model = CeleryTaskInvocationLog


class LogCore(LogCoreMixin, ElasticsearchUiRestCore):

    abstract = True
    rest_filter_manager = SecurityElasticsearchFilterManager()

    output_request_inline_table_view = OutputRequestLogInlineTableView
    command_inline_table_view = CommandLogInlineTableView
    celery_task_invocation_inline_table_view = CeleryTaskInvocationLogInlineTableView

    display_related_objects_filter = RelatedObjectsFilter

    def _get_parent_log_obj(self, obj):
        return get_log_from_key(obj.parent_log) if obj.parent_log else None

    def _get_related_objects(self, obj):
        return filter(None, [
            get_object_from_key(related_object_key) for related_object_key in obj.related_objects or ()
        ])


class InputRequestLogCore(InputRequestLogCoreMixin, LogCore):

    abstract = True
    model = InputRequestLog

    @short_description(_('user'))
    @filter_class(UsernameUserFilter)
    @order_by('user_id')
    def user(self, obj):
        return obj.user


class OutputRequestLogCore(OutputRequestLogCoreMixin, LogCore):

    abstract = True
    model = OutputRequestLog


class CommandLogCore(CommandLogCoreMixin, LogCore):

    abstract = True
    model = CommandLog


class CeleryRunCeleryTaskInvocationLogInlineTableView(CeleryTaskInvocationLogInlineTableViewMixin,
                                                      ElasticsearchInlineTableView):

    model = CeleryTaskInvocationLog


class CeleryTaskRunLogCore(CeleryTaskRunLogCoreMixin, LogCore):

    abstract = True
    model = CeleryTaskRunLog

    celery_task_invocation_inline_table_view = CeleryRunCeleryTaskInvocationLogInlineTableView


class CeleryTaskRunLogInlineTableView(CeleryTaskRunLogInlineTableViewMixin, ElasticsearchInlineTableView):

    model = CeleryTaskRunLog


class CeleryTaskInvocationLogCore(CeleryTaskInvocationLogCoreMixin, LogCore):

    abstract = True
    model = CeleryTaskInvocationLog

    celery_task_run_inline_table_view = CeleryTaskRunLogInlineTableView


class RelatedInputRequestLogInlineTableView(RelatedLogInlineTableViewMixin, ElasticsearchInlineTableView):

    model = InputRequestLog


class RelatedOutputRequestLogInlineTableView(RelatedLogInlineTableViewMixin, ElasticsearchInlineTableView):

    model = OutputRequestLog


class RelatedCommandLogInlineTableView(RelatedLogInlineTableViewMixin, ElasticsearchInlineTableView):

    model = CommandLog


class RelatedCeleryTaskInvocationLogInlineTableView(RelatedLogInlineTableViewMixin, ElasticsearchInlineTableView):

    model = CeleryTaskInvocationLog


class RelatedCeleryTaskRunLogInlineTableView(RelatedLogInlineTableViewMixin, ElasticsearchInlineTableView):

    model = CeleryTaskRunLog


class RelatedLogsView(BaseRelatedLogsView):

    input_request_inline_view = RelatedInputRequestLogInlineTableView
    output_request_inline_view = RelatedOutputRequestLogInlineTableView
    command_inline_view = RelatedCommandLogInlineTableView
    celery_task_run_inline_view = RelatedCeleryTaskInvocationLogInlineTableView
    celery_task_invocation_inline_view = RelatedCeleryTaskRunLogInlineTableView
