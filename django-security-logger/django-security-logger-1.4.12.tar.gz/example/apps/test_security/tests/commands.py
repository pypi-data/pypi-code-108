import os, shutil

import responses
from datetime import timedelta

from freezegun import freeze_time

from django.conf import settings as django_settings
from django.test import override_settings
from django.utils.timezone import now

from germanium.test_cases.client import ClientTestCase
from germanium.tools import (
    assert_equal, assert_false, assert_http_not_found, assert_http_ok, assert_http_redirect,
    assert_http_too_many_requests, assert_in, assert_is_none, assert_is_not_none, assert_not_in,
    assert_raises, assert_true, assert_equal_model_fields
)

from security import requests
from security.config import settings
from security.backends.sql.models import CommandLog as SQLCommandLog
from security.backends.elasticsearch.models import CommandLog as ElasticsearchCommandLog
from security.backends.sql.models import CeleryTaskRunLog as SQLCeleryTaskRunLog
from security.backends.sql.models import CeleryTaskInvocationLog as SQLCeleryTaskInvocationLog
from security.backends.elasticsearch.models import CeleryTaskRunLog as ElasticsearchCeleryTaskRunLog
from security.backends.elasticsearch.models import CeleryTaskInvocationLog as ElasticsearchCeleryTaskInvocationLog
from security.backends.sql.models import InputRequestLog as SQLInputRequestLog
from security.backends.elasticsearch.models import InputRequestLog as ElasticsearchInputRequestLog
from security.backends.sql.models import OutputRequestLog as SQLOutputRequestLog
from security.backends.elasticsearch.models import OutputRequestLog as ElasticsearchOutputRequestLog

from security.backends.testing import capture_security_logs

from apps.test_security.tasks import sum_task

from .base import BaseTestCaseMixin, test_call_command


@override_settings(SECURITY_BACKEND_WRITERS={})
class CommandTestCase(BaseTestCaseMixin, ClientTestCase):

    SQL_LOG_MODELS = {
        'input-request': SQLInputRequestLog,
        'output-request': SQLOutputRequestLog,
        'command': SQLCommandLog,
        'celery-invocation': SQLCeleryTaskInvocationLog,
        'celery-run': SQLCeleryTaskRunLog,
    }

    @responses.activate
    @override_settings(
        SECURITY_BACKEND_WRITERS={'sql'},
        SECURITY_COMMAND_LOG_EXCLUDED_COMMANDS={'purge_logs'},
        SECURITY_BACKUP_STORAGE_PATH=os.path.join(django_settings.PROJECT_DIR, 'var', 'backup_sql')
    )
    def test_sql_purge_logs_should_remove_logged_data(self):
        responses.add(responses.GET, 'https://localhost/test', body='test')

        test_call_command('test_command')
        sum_task.apply(args=(5, 8))
        assert_http_ok(self.get('/home/'))
        requests.get('https://localhost/test')

        sql_type_model = {
            ('input-request', SQLInputRequestLog),
            ('output-request', SQLOutputRequestLog),
            ('command', SQLCommandLog),
            ('celery-task-invocation', SQLCeleryTaskInvocationLog),
            ('celery-task-run', SQLCeleryTaskRunLog),
        }

        for log_type, log_model in sql_type_model:
            log_directory = os.path.join(settings.BACKUP_STORAGE_PATH, log_type)
            os.makedirs(log_directory)
            test_call_command('purge_logs', type=log_type, interactive=False, expiration='1d', backup=log_type)
            assert_equal(log_model.objects.count(), 1)

            with freeze_time(now() + timedelta(days=1, minutes=1)):
                test_call_command('purge_logs', type=log_type, interactive=False, expiration='1d', backup=log_type)
                assert_equal(log_model.objects.count(), 0)
            assert_equal(len(os.listdir(log_directory)), 1)
        shutil.rmtree(settings.BACKUP_STORAGE_PATH)

    @responses.activate
    @override_settings(
        SECURITY_BACKEND_WRITERS={'elasticsearch'},
        SECURITY_COMMAND_LOG_EXCLUDED_COMMANDS={'purge_logs'},
        SECURITY_BACKUP_STORAGE_PATH=os.path.join(django_settings.PROJECT_DIR, 'var', 'backup_elastic')
    )
    def test_elasticsearch_purge_logs_should_remove_logged_data(self):
        responses.add(responses.GET, 'https://localhost/test', body='test')
        with capture_security_logs() as logged_data:
            test_call_command('test_command')
            sum_task.apply(args=(5, 8))
            assert_http_ok(self.get('/home/'))
            requests.get('https://localhost/test')

            elasticsearch_type_model_receivers = (
                ('input-request', ElasticsearchInputRequestLog, 'input_request'),
                ('output-request', ElasticsearchOutputRequestLog, 'output_request'),
                ('command', ElasticsearchCommandLog, 'command'),
                ('celery-task-invocation', ElasticsearchCeleryTaskInvocationLog, 'celery_task_invocation'),
                ('celery-task-run', ElasticsearchCeleryTaskRunLog, 'celery_task_run'),
            )

            for log_type, log_model, log_data_name in elasticsearch_type_model_receivers:
                log_directory = os.path.join(settings.BACKUP_STORAGE_PATH, log_type)
                os.makedirs(log_directory)
                test_call_command('purge_logs', type=log_type, interactive=False, expiration='1d', backup=log_type)
                log_model._index.refresh()
                assert_equal(log_model.search().filter(
                    'ids', values=[logged_data[log_data_name][0].id]
                ).count(), 1)

                with freeze_time(now() + timedelta(days=1, minutes=1)):
                    test_call_command('purge_logs', type=log_type, interactive=False, expiration='1d', backup=log_type)
                    log_model._index.refresh()
                    assert_equal(log_model.search().filter(
                        'ids', values=[logged_data[log_data_name][0].id]
                    ).count(), 0)
                assert_equal(len(os.listdir(log_directory)), 1)
        shutil.rmtree(settings.BACKUP_STORAGE_PATH)
