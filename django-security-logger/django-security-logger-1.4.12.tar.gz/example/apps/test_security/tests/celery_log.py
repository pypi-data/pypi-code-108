from uuid import uuid4
from unittest import mock
import responses
from datetime import timedelta

from django import get_version
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import transaction
from django.test import override_settings
from django.utils.timezone import now

from freezegun import freeze_time

from celery.exceptions import TimeoutError

from germanium.decorators import data_consumer
from germanium.test_cases.client import ClientTestCase
from germanium.tools import (
    assert_equal, assert_false, assert_http_not_found, assert_http_ok, assert_http_redirect,
    assert_http_too_many_requests, assert_in, assert_is_none, assert_is_not_none, assert_not_in,
    assert_raises, assert_true, assert_equal_model_fields, capture_commit_callbacks, assert_length_equal,
    all_eq_obj, not_none_eq_obj
)

from chamber.shortcuts import change_and_save

from django_celery_extensions.task import get_django_command_task

from security.config import settings
from security.decorators import log_with_data
from security.enums import CeleryTaskInvocationLogState, CeleryTaskRunLogState, LoggerName
from security.backends.sql.models import CeleryTaskRunLog as SQLCeleryTaskRunLog
from security.backends.sql.models import CeleryTaskInvocationLog as SQLCeleryTaskInvocationLog
from security.backends.elasticsearch.models import CeleryTaskRunLog as ElasticsearchCeleryTaskRunLog
from security.backends.elasticsearch.models import CeleryTaskInvocationLog as ElasticsearchCeleryTaskInvocationLog

from security.backends.signals import (
    celery_task_invocation_started, celery_task_invocation_expired, celery_task_invocation_triggered,
    celery_task_invocation_ignored, celery_task_invocation_timeout, celery_task_run_started, celery_task_run_failed,
    celery_task_run_retried, celery_task_run_succeeded, celery_task_run_output_updated
)
from security.backends.testing import capture_security_logs
from security.backends.reader import get_logs_related_with_object

from apps.test_security.tasks import error_task, retry_task, sum_task, unique_task, ignored_after_success_task

from .base import BaseTestCaseMixin, TRUNCATION_CHAR, test_call_command


@override_settings(SECURITY_BACKEND_WRITERS={})
class CeleryLogTestCase(BaseTestCaseMixin, ClientTestCase):

    @data_consumer('create_user')
    @override_settings(SECURITY_BACKEND_READER='testing')
    def test_sum_celery_task_should_be_logged(self, user):
        expected_invocation_started_data = {
            'name': 'sum_task',
            'queue_name': 'default',
            'input': '5, 8',
            'task_args': [5, 8],
            'task_kwargs': {},
            'applied_at': not_none_eq_obj,
            'is_async': False,
            'is_unique': False,
            'is_on_commit': False,
            'start': not_none_eq_obj,
        }
        expected_invocation_triggered_data = {
            **expected_invocation_started_data,
            'triggered_at': not_none_eq_obj,
            'stale_at': None,
            'estimated_time_of_first_arrival': not_none_eq_obj,
            'expires_at': None,
            'celery_task_id': not_none_eq_obj,
            'is_duplicate': False,
        }

        expected_run_started_data = {
            'name': 'sum_task',
            'queue_name': None,
            'input': '5, 8',
            'task_args': [5, 8],
            'task_kwargs': {},
            'start': not_none_eq_obj,
            'retries': 0,
            'celery_task_id': not_none_eq_obj,
            'waiting_time': not_none_eq_obj,
        }
        expected_run_succeeded_data = {
            **expected_run_started_data,
            'stop': not_none_eq_obj,
            'result': 13
        }

        with capture_security_logs() as logged_data:
            sum_task.apply(args=(5, 8), related_objects=[user])
            assert_length_equal(logged_data.celery_task_invocation_started, 1)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 1)
            assert_length_equal(logged_data.celery_task_run_started, 1)
            assert_length_equal(logged_data.celery_task_run_succeeded, 1)
            assert_length_equal(logged_data.celery_task_run_output_updated, 1)
            assert_length_equal(logged_data.celery_task_run_failed, 0)
            assert_length_equal(logged_data.celery_task_run_retried, 0)
            assert_equal(logged_data.celery_task_invocation_started[0].data, expected_invocation_started_data)
            assert_equal(logged_data.celery_task_invocation_triggered[0].data, expected_invocation_triggered_data)
            assert_equal(logged_data.celery_task_run_started[0].data, expected_run_started_data)
            assert_equal(logged_data.celery_task_run_succeeded[0].data, expected_run_succeeded_data)
            assert_equal(logged_data.celery_task_invocation[0].related_objects, {user})
            assert_equal(
                get_logs_related_with_object(LoggerName.CELERY_TASK_INVOCATION, user),
                [logged_data.celery_task_invocation[0]]
            )

    def test_error_celery_task_should_be_logged(self):
        expected_invocation_started_data = {
            'name': 'error_task',
            'queue_name': 'default',
            'input': '',
            'task_args': [],
            'task_kwargs': {},
            'applied_at': not_none_eq_obj,
            'is_async': False,
            'is_unique': False,
            'is_on_commit': False,
            'start': not_none_eq_obj,
        }
        expected_invocation_triggered_data = {
            **expected_invocation_started_data,
            'triggered_at': not_none_eq_obj,
            'stale_at': not_none_eq_obj,
            'estimated_time_of_first_arrival': not_none_eq_obj,
            'expires_at': None,
            'celery_task_id': not_none_eq_obj,
            'is_duplicate': False,
        }

        expected_run_started_data = {
            'name': 'error_task',
            'queue_name': None,
            'input': '',
            'task_args': [],
            'task_kwargs': {},
            'start': not_none_eq_obj,
            'retries': 0,
            'celery_task_id': not_none_eq_obj,
            'waiting_time': not_none_eq_obj,
        }
        expected_run_failed_data = {
            **expected_run_started_data,
            'stop': not_none_eq_obj,
            'error_message': not_none_eq_obj,
        }
        with capture_security_logs() as logged_data:
            error_task.apply()
            assert_length_equal(logged_data.celery_task_invocation_started, 1)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 1)
            assert_length_equal(logged_data.celery_task_run_started, 1)
            assert_length_equal(logged_data.celery_task_run_succeeded, 0)
            assert_length_equal(logged_data.celery_task_run_output_updated, 1)
            assert_length_equal(logged_data.celery_task_run_failed, 1)
            assert_length_equal(logged_data.celery_task_run_retried, 0)
            assert_equal(logged_data.celery_task_invocation_started[0].data, expected_invocation_started_data)
            assert_equal(logged_data.celery_task_invocation_triggered[0].data, expected_invocation_triggered_data)
            assert_equal(logged_data.celery_task_run_started[0].data, expected_run_started_data)
            assert_equal(logged_data.celery_task_run_failed[0].data, expected_run_failed_data)

    def test_retry_celery_task_should_be_logged(self):
        expected_invocation_started_data = {
            'name': 'retry_task',
            'queue_name': 'default',
            'input': '',
            'task_args': [],
            'task_kwargs': {},
            'applied_at': not_none_eq_obj,
            'is_async': False,
            'is_unique': False,
            'is_on_commit': False,
            'start': not_none_eq_obj,
        }
        expected_invocation_triggered_data = {
            **expected_invocation_started_data,
            'triggered_at': not_none_eq_obj,
            'stale_at': None,
            'estimated_time_of_first_arrival': not_none_eq_obj,
            'expires_at': None,
            'celery_task_id': not_none_eq_obj,
            'is_duplicate': False,
        }

        expected_run_started_data = {
            'name': 'retry_task',
            'queue_name': None,
            'input': '',
            'task_args': [],
            'task_kwargs': {},
            'start': not_none_eq_obj,
            'retries': not_none_eq_obj,
            'celery_task_id': not_none_eq_obj,
            'waiting_time': not_none_eq_obj,
        }
        expected_run_retried_data = {
            **expected_run_started_data,
            'stop': not_none_eq_obj,
            'error_message': not_none_eq_obj,
            'estimated_time_of_next_retry': not_none_eq_obj,
        }

        with capture_security_logs() as logged_data:
            retry_task.apply()

            assert_length_equal(logged_data.celery_task_invocation_started, 1)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 1)
            assert_length_equal(logged_data.celery_task_run_started, 6)
            assert_length_equal(logged_data.celery_task_run_succeeded, 1)
            assert_length_equal(logged_data.celery_task_run_output_updated, 6)
            assert_length_equal(logged_data.celery_task_run_failed, 0)
            assert_length_equal(logged_data.celery_task_run_retried, 5)
            assert_equal(logged_data.celery_task_invocation_started[0].data, expected_invocation_started_data)
            assert_equal(logged_data.celery_task_invocation_triggered[0].data, expected_invocation_triggered_data)
            assert_equal(logged_data.celery_task_run_started[0].data, expected_run_started_data)
            assert_equal(logged_data.celery_task_run_retried[0].data, expected_run_retried_data)

    @override_settings(DJANGO_CELERY_EXTENSIONS_DEFAULT_TASK_STALE_TIME_LIMIT=30, SECURITY_TASK_USE_ON_SUCCESS=True)
    def test_ignored_after_success_celery_task_should_be_logged(self):
        with capture_security_logs() as logged_data:
            with capture_commit_callbacks(execute_on_commit=True):
                ignored_after_success_task.apply_async_on_commit()
                ignored_after_success_task.apply_async_on_commit()

            assert_length_equal(logged_data.celery_task_invocation_started, 2)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 1)
            assert_length_equal(logged_data.celery_task_invocation_ignored, 1)
            assert_length_equal(logged_data.celery_task_run_started, 1)

    @override_settings(DJANGO_CELERY_EXTENSIONS_DEFAULT_TASK_STALE_TIME_LIMIT=5)
    def test_apply_async_and_get_result_should_return_time_error_for_zero_timeout(self):
        with capture_security_logs() as logged_data:
            with assert_raises(TimeoutError):
                unique_task.apply_async_and_get_result(timeout=0)
            assert_length_equal(logged_data.celery_task_invocation_timeout, 1)

    @override_settings(SECURITY_TASK_USE_PRE_COMMIT=True)
    def test_task_should_be_logged_with_on_commit_signal(self):
        with capture_security_logs() as logged_data:
            with capture_commit_callbacks() as captured_commit_callbacks:
                sum_task.apply_async_on_commit(args=(5, 8))
            assert_length_equal(logged_data.celery_task_invocation_started, 0)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 0)
            captured_commit_callbacks.execute_pre_commit()
            assert_length_equal(logged_data.celery_task_invocation_started, 1)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 0)
            captured_commit_callbacks.execute_on_commit()
            assert_length_equal(logged_data.celery_task_invocation_started, 1)
            assert_length_equal(logged_data.celery_task_invocation_triggered, 1)

    @override_settings(SECURITY_TASK_USE_ON_SUCCESS=True)
    def test_unique_task_should_be_logged_as_duplicate_and_run_is_not_started(self):
        with mock.patch.object(unique_task, '_get_unique_task_id') as apply_method:
            unique_task_id = uuid4()
            apply_method.return_value = unique_task_id
            with capture_security_logs() as logged_data:
                unique_task.apply_async()
                assert_length_equal(logged_data.celery_task_invocation_triggered, 1)
                assert_length_equal(logged_data.celery_task_run_started, 0)
                assert_true(logged_data.celery_task_invocation_triggered[0].data['is_duplicate'])
                assert_equal(logged_data.celery_task_invocation_triggered[0].data['celery_task_id'], unique_task_id)

    def test_data_change_should_be_connected_with_celery_task_run_log(self):
        with capture_security_logs() as logged_data:
            get_django_command_task('create_user').apply_async()
            assert_equal(
                logged_data.celery_task_run[0].extra_data,
                {'reversion': {'revisions': [{'id': not_none_eq_obj}], 'total_count': 1}}
            )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    @data_consumer('create_user')
    def test_sum_celery_task_should_be_logged_in_sql_backend(self, user):
        with log_with_data(related_objects=[user]):
            sum_task.apply(args=(5, 8), related_objects=[user])
            assert_equal(SQLCeleryTaskInvocationLog.objects.count(), 1)
            assert_equal(SQLCeleryTaskRunLog.objects.count(), 1)
            sql_celery_task_invocation_log = SQLCeleryTaskInvocationLog.objects.get()
            sql_celery_task_run_log = SQLCeleryTaskRunLog.objects.get()

            assert_equal_model_fields(
                sql_celery_task_invocation_log,
                state=CeleryTaskInvocationLogState.SUCCEEDED,
                name='sum_task',
                time=(sql_celery_task_invocation_log.stop - sql_celery_task_invocation_log.start).total_seconds(),
                stale_at=None,
                expires_at=None,
                is_duplicate=False,
                input='5, 8',
                task_args=[5, 8],
                task_kwargs={},
                queue_name='default'
            )
            assert_is_not_none(sql_celery_task_invocation_log.celery_task_id)
            assert_equal([rel_obj.object for rel_obj in sql_celery_task_invocation_log.related_objects.all()], [user])
            assert_equal_model_fields(
                sql_celery_task_run_log,
                state=CeleryTaskRunLogState.SUCCEEDED,
                name='sum_task',
                time=(sql_celery_task_run_log.stop - sql_celery_task_run_log.start).total_seconds(),
                input='5, 8',
                task_args=[5, 8],
                task_kwargs={},
                queue_name=None,
                retries=0
            )

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    @data_consumer('create_user')
    def test_sum_celery_task_should_be_logged_in_elasticsearch_backend(self, user):
        with log_with_data(related_objects=[user]):
            with capture_security_logs() as logged_data:
                sum_task.apply(args=(5, 8), related_objects=[user])

                elasticsearch_celery_task_invocation_log = ElasticsearchCeleryTaskInvocationLog.get(
                    id=logged_data.celery_task_invocation[0].id
                )
                elasticsearch_celery_task_run_log = ElasticsearchCeleryTaskRunLog.get(
                    id=logged_data.celery_task_run[0].id
                )

                assert_equal_model_fields(
                    elasticsearch_celery_task_invocation_log,
                    state=CeleryTaskInvocationLogState.SUCCEEDED,
                    name='sum_task',
                    time=(
                        elasticsearch_celery_task_invocation_log.stop - elasticsearch_celery_task_invocation_log.start
                    ).total_seconds(),
                    stale_at=None,
                    expires_at=None,
                    is_duplicate=False,
                    input='5, 8',
                    task_args='[5, 8]',
                    task_kwargs='{}',
                    queue_name='default'
                )
                assert_is_not_none(elasticsearch_celery_task_invocation_log.celery_task_id)
                assert_equal(
                    [rel_obj for rel_obj in elasticsearch_celery_task_invocation_log.related_objects],
                    ['default|3|{}'.format(user.id)]
                )
                assert_equal_model_fields(
                    elasticsearch_celery_task_run_log,
                    state=CeleryTaskRunLogState.SUCCEEDED,
                    name='sum_task',
                    time=(
                        elasticsearch_celery_task_run_log.stop - elasticsearch_celery_task_run_log.start
                    ).total_seconds(),
                    input='5, 8',
                    task_args='[5, 8]',
                    task_kwargs='{}',
                    queue_name=None,
                    retries=0
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    def test_sum_celery_task_should_be_logged_in_logging_backend(self):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.celery', level='INFO') as cm:
                sum_task.apply(args=(5, 8))

                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.celery:'
                        f'Celery task invocation "{logged_data.celery_task_invocation[0].id}" '
                        f'with celery id "{logged_data.celery_task_invocation[0].data["celery_task_id"]}" '
                        f'and name "sum_task" was invoked',
                        f'INFO:security.celery:Celery task "{logged_data.celery_task_run[0].id}" with '
                        f'celery id "{logged_data.celery_task_run[0].data["celery_task_id"]}" and name "sum_task" '
                        f'was started',
                        f'INFO:security.celery:Celery task "{logged_data.celery_task_run[0].id}" with '
                        f'celery id "{logged_data.celery_task_run[0].data["celery_task_id"]}" and name "sum_task" '
                        f'was successful',
                    ]
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    def test_error_celery_task_should_be_logged_in_sql_backend(self):
        error_task.apply()
        assert_equal(SQLCeleryTaskInvocationLog.objects.count(), 1)
        assert_equal(SQLCeleryTaskRunLog.objects.count(), 1)
        sql_celery_task_invocation_log = SQLCeleryTaskInvocationLog.objects.get()
        sql_celery_task_run_log = SQLCeleryTaskRunLog.objects.get()

        assert_equal_model_fields(
            sql_celery_task_invocation_log,
            state=CeleryTaskInvocationLogState.FAILED,
            name='error_task',
            time=(sql_celery_task_invocation_log.stop - sql_celery_task_invocation_log.start).total_seconds(),
            expires_at=None,
            is_duplicate=False,
            input='',
            task_args=[],
            task_kwargs={},
            queue_name='default'
        )
        assert_is_not_none(sql_celery_task_invocation_log.celery_task_id)
        assert_equal_model_fields(
            sql_celery_task_run_log,
            state=CeleryTaskRunLogState.FAILED,
            name='error_task',
            time=(sql_celery_task_run_log.stop - sql_celery_task_run_log.start).total_seconds(),
            input='',
            task_args=[],
            task_kwargs={},
            queue_name=None,
            retries=0
        )
        assert_is_not_none(sql_celery_task_run_log.error_message)

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    def test_error_celery_task_should_be_logged_in_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            error_task.apply()
            elasticsearch_celery_task_invocation_log = ElasticsearchCeleryTaskInvocationLog.get(
                id=logged_data.celery_task_invocation[0].id
            )
            elasticsearch_celery_task_run_log = ElasticsearchCeleryTaskRunLog.get(
                id=logged_data.celery_task_run[0].id
            )

            assert_equal_model_fields(
                elasticsearch_celery_task_invocation_log,
                state=CeleryTaskInvocationLogState.FAILED,
                name='error_task',
                time=(
                    elasticsearch_celery_task_invocation_log.stop - elasticsearch_celery_task_invocation_log.start
                ).total_seconds(),
                expires_at=None,
                is_duplicate=False,
                input='',
                task_args='[]',
                task_kwargs='{}',
                queue_name='default'
            )
            assert_is_not_none(elasticsearch_celery_task_invocation_log.celery_task_id)
            assert_equal_model_fields(
                elasticsearch_celery_task_run_log,
                state=CeleryTaskRunLogState.FAILED,
                name='error_task',
                time=(elasticsearch_celery_task_run_log.stop - elasticsearch_celery_task_run_log.start).total_seconds(),
                input='',
                task_args='[]',
                task_kwargs='{}',
                queue_name=None,
                retries=0
            )
            assert_is_not_none(elasticsearch_celery_task_run_log.error_message)

    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    def test_error_celery_task_should_be_logged_in_logging_backend(self):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.celery', level='INFO') as cm:
                error_task.apply()

                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.celery:'
                        f'Celery task invocation "{logged_data.celery_task_invocation[0].id}" '
                        f'with celery id "{logged_data.celery_task_invocation[0].data["celery_task_id"]}" '
                        f'and name "error_task" was invoked',
                        f'INFO:security.celery:Celery task "{logged_data.celery_task_run[0].id}" with '
                        f'celery id "{logged_data.celery_task_run[0].data["celery_task_id"]}" and name "error_task" '
                        f'was started',
                        f'ERROR:security.celery:Celery task "{logged_data.celery_task_run[0].id}" with '
                        f'celery id "{logged_data.celery_task_run[0].data["celery_task_id"]}" and name "error_task" '
                        f'failed',
                    ]
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    def test_retry_celery_task_should_be_logged_in_sql_backend(self):
        with capture_security_logs() as logged_data:
            retry_task.apply()
            assert_equal(SQLCeleryTaskInvocationLog.objects.count(), 1)
            assert_equal(SQLCeleryTaskRunLog.objects.count(), 6)

            sql_celery_task_invocation_log = SQLCeleryTaskInvocationLog.objects.get()
            assert_equal_model_fields(
                sql_celery_task_invocation_log,
                state=CeleryTaskInvocationLogState.SUCCEEDED,
                name='retry_task',
                time=(sql_celery_task_invocation_log.stop - sql_celery_task_invocation_log.start).total_seconds(),
                expires_at=None,
                is_duplicate=False,
                input='',
                task_args=[],
                task_kwargs={},
                queue_name='default'
            )

            for i, logger in enumerate(logged_data.celery_task_run[0:5]):
                sql_celery_task_run_log = SQLCeleryTaskRunLog.objects.get(id=logger.id)
                assert_equal_model_fields(
                    sql_celery_task_run_log,
                    state=CeleryTaskRunLogState.RETRIED,
                    name='retry_task',
                    time=(sql_celery_task_run_log.stop - sql_celery_task_run_log.start).total_seconds(),
                    input='',
                    task_args=[],
                    task_kwargs={},
                    queue_name=None,
                    retries=i
                )
                assert_is_not_none(sql_celery_task_run_log.error_message)
            sql_celery_task_run_log = SQLCeleryTaskRunLog.objects.get(id=logged_data.celery_task_run[-1].id)
            assert_equal_model_fields(
                sql_celery_task_run_log,
                state=CeleryTaskRunLogState.SUCCEEDED,
                name='retry_task',
                time=(sql_celery_task_run_log.stop - sql_celery_task_run_log.start).total_seconds(),
                input='',
                task_args=[],
                task_kwargs={},
                queue_name=None,
                retries=5,
                error_message=None
            )
            assert_equal(sql_celery_task_invocation_log.last_run.id, sql_celery_task_run_log.id)

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    def test_retry_celery_task_should_be_logged_in_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            retry_task.apply()

            elasticsearch_celery_task_invocation_log = ElasticsearchCeleryTaskInvocationLog.get(
                id=logged_data.celery_task_invocation[0].id
            )
            assert_equal_model_fields(
                elasticsearch_celery_task_invocation_log,
                state=CeleryTaskInvocationLogState.SUCCEEDED,
                name='retry_task',
                time=(
                    elasticsearch_celery_task_invocation_log.stop - elasticsearch_celery_task_invocation_log.start
                ).total_seconds(),
                expires_at=None,
                is_duplicate=False,
                input='',
                task_args='[]',
                task_kwargs='{}',
                queue_name='default'
            )

            for i, logger in enumerate(logged_data.celery_task_run[0:5]):
                elasticsearch_celery_task_run_log = ElasticsearchCeleryTaskRunLog.get(
                    id=logger.id
                )
                assert_equal_model_fields(
                    elasticsearch_celery_task_run_log,
                    state=CeleryTaskRunLogState.RETRIED,
                    name='retry_task',
                    time=(
                        elasticsearch_celery_task_run_log.stop - elasticsearch_celery_task_run_log.start
                    ).total_seconds(),
                    input='',
                    task_args='[]',
                    task_kwargs='{}',
                    queue_name=None,
                    retries=i
                )
                assert_is_not_none(elasticsearch_celery_task_run_log.error_message)
            elasticsearch_celery_task_run_log = ElasticsearchCeleryTaskRunLog.get(
                id=logged_data.celery_task_run[-1].id
            )
            assert_equal_model_fields(
                elasticsearch_celery_task_run_log,
                state=CeleryTaskRunLogState.SUCCEEDED,
                name='retry_task',
                time=(elasticsearch_celery_task_run_log.stop - elasticsearch_celery_task_run_log.start).total_seconds(),
                input='',
                task_args='[]',
                task_kwargs='{}',
                queue_name=None,
                retries=5,
                error_message=None
            )
            ElasticsearchCeleryTaskRunLog._index.refresh()
            assert_equal(elasticsearch_celery_task_invocation_log.last_run.id, elasticsearch_celery_task_run_log.id)

    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    def test_retry_celery_task_should_be_logged_in_logging_backend(self):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.celery', level='INFO') as cm:
                retry_task.apply()
                expected_output = [
                    f'INFO:security.celery:'
                    f'Celery task invocation "{logged_data.celery_task_invocation[0].id}" '
                    f'with celery id "{logged_data.celery_task_invocation[0].data["celery_task_id"]}" '
                    f'and name "retry_task" was invoked',
                ]
                for logger in logged_data.celery_task_run[0:5]:
                    expected_output += [
                        f'INFO:security.celery:Celery task "{logger.id}" with '
                        f'celery id "{logger.data["celery_task_id"]}" and name "retry_task" '
                        f'was started',
                        f'WARNING:security.celery:Celery task "{logger.id}" with '
                        f'celery id "{logger.data["celery_task_id"]}" and name "retry_task" '
                        f'was repeated',
                    ]
                expected_output += [
                    f'INFO:security.celery:Celery task "{logged_data.celery_task_run[-1].id}" with '
                    f'celery id "{logged_data.celery_task_run[-1].data["celery_task_id"]}" and name "retry_task" '
                    f'was started',
                    f'INFO:security.celery:Celery task "{logged_data.celery_task_run[-1].id}" with '
                    f'celery id "{logged_data.celery_task_run[-1].data["celery_task_id"]}" and name "retry_task" was '
                    f'successful',
                ]
                assert_equal(cm.output, expected_output)

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'}, DJANGO_CELERY_EXTENSIONS_DEFAULT_TASK_STALE_TIME_LIMIT=30)
    def test_set_celery_task_log_state_should_set_task_to_failed_with_sql_backend(self):
        with mock.patch.object(unique_task, '_get_unique_task_id') as apply_method:
            unique_task_id = uuid4()
            apply_method.return_value = unique_task_id
            unique_task.apply_async()

            sql_celery_task_invocation_log = SQLCeleryTaskInvocationLog.objects.get()
            test_call_command('set_celery_task_log_state')
            sql_celery_task_invocation_log.refresh_from_db()
            assert_equal(
                sql_celery_task_invocation_log.state, CeleryTaskInvocationLogState.TRIGGERED
            )

            with freeze_time(now() + timedelta(seconds=30)):
                test_call_command('set_celery_task_log_state')
                sql_celery_task_invocation_log.refresh_from_db()
                assert_equal(sql_celery_task_invocation_log.state, CeleryTaskInvocationLogState.EXPIRED)

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'}, DJANGO_CELERY_EXTENSIONS_DEFAULT_TASK_STALE_TIME_LIMIT=30)
    def test_set_celery_task_log_state_should_set_task_to_failed_with_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            with mock.patch.object(unique_task, '_get_unique_task_id') as apply_method:
                unique_task_id = uuid4()
                apply_method.return_value = unique_task_id
                unique_task.apply_async()
                ElasticsearchCeleryTaskInvocationLog._index.refresh()

                test_call_command('set_celery_task_log_state')
                assert_equal(
                    ElasticsearchCeleryTaskInvocationLog.get(
                        id=logged_data.celery_task_invocation[0].id
                    ).state, CeleryTaskInvocationLogState.TRIGGERED
                )

                with freeze_time(now() + timedelta(seconds=30)):
                    test_call_command('set_celery_task_log_state')
                    assert_equal(
                        ElasticsearchCeleryTaskInvocationLog.get(
                            id=logged_data.celery_task_invocation[0].id
                        ).state,
                        CeleryTaskInvocationLogState.EXPIRED
                    )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'}, DJANGO_CELERY_EXTENSIONS_DEFAULT_TASK_STALE_TIME_LIMIT=30)
    def test_set_celery_task_log_state_should_set_task_to_succeeded_with_sql_backend(self):
        unique_task.apply_async()

        sql_celery_task_invocation_log = SQLCeleryTaskInvocationLog.objects.get()
        change_and_save(sql_celery_task_invocation_log, state=CeleryTaskInvocationLogState.TRIGGERED)

        test_call_command('set_celery_task_log_state')
        sql_celery_task_invocation_log.refresh_from_db()
        assert_equal(
            sql_celery_task_invocation_log.state, CeleryTaskInvocationLogState.TRIGGERED
        )

        with freeze_time(now() + timedelta(seconds=30)):
            test_call_command('set_celery_task_log_state')
            sql_celery_task_invocation_log.refresh_from_db()
            assert_equal(sql_celery_task_invocation_log.state, CeleryTaskInvocationLogState.SUCCEEDED)

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'}, DJANGO_CELERY_EXTENSIONS_DEFAULT_TASK_STALE_TIME_LIMIT=30)
    def test_set_celery_task_log_state_should_set_task_to_succeeded_with_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            unique_task.apply_async()
            ElasticsearchCeleryTaskInvocationLog.get(
                id=logged_data.celery_task_invocation[0].id
            ).update(state=CeleryTaskInvocationLogState.TRIGGERED)
            ElasticsearchCeleryTaskInvocationLog._index.refresh()
            ElasticsearchCeleryTaskRunLog._index.refresh()

            test_call_command('set_celery_task_log_state')
            assert_equal(
                ElasticsearchCeleryTaskInvocationLog.get(
                    id=logged_data.celery_task_invocation[0].id
                ).state, CeleryTaskInvocationLogState.TRIGGERED
            )

            with freeze_time(now() + timedelta(seconds=30)):
                test_call_command('set_celery_task_log_state')
                assert_equal(
                    ElasticsearchCeleryTaskInvocationLog.get(
                        id=logged_data.celery_task_invocation[0].id
                    ).state,
                    CeleryTaskInvocationLogState.SUCCEEDED
                )
