import responses

from django import get_version
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.test import override_settings

from germanium.decorators import data_consumer
from germanium.test_cases.client import ClientTestCase
from germanium.tools import (
    assert_equal, assert_false, assert_http_not_found, assert_http_ok, assert_http_redirect,
    assert_http_too_many_requests, assert_in, assert_is_none, assert_is_not_none, assert_not_in,
    assert_raises, assert_true, assert_equal_model_fields, assert_length_equal, all_eq_obj, not_none_eq_obj
)

from security.config import settings
from security.decorators import log_with_data
from security.enums import CommandState, LoggerName
from security.backends.sql.models import CommandLog as SQLCommandLog
from security.backends.elasticsearch.models import CommandLog as ElasticsearchCommandLog
from security.backends.signals import (
    command_started, command_error, command_finished, command_output_updated, output_request_finished
)
from security.backends.reader import get_logs_related_with_object
from security.backends.testing import capture_security_logs

from .base import BaseTestCaseMixin, TRUNCATION_CHAR, test_call_command


@override_settings(SECURITY_BACKEND_WRITERS={})
class CommandLogTestCase(BaseTestCaseMixin, ClientTestCase):

    def test_command_should_be_logged(self):
        expected_command_started_data = {
            'name': 'test_command',
            'input': 'verbosity=0',
            'is_executed_from_command_line': False,
            'start': all_eq_obj,
        }
        expected_command_finished_data = {
            **expected_command_started_data,
            'stop': all_eq_obj,
        }
        with capture_security_logs() as logged_data:
            test_call_command('test_command', verbosity=0)
            assert_length_equal(logged_data.command_started, 1)
            assert_length_equal(logged_data.command_finished, 1)
            assert_length_equal(logged_data.command_output_updated, 1)
            assert_length_equal(logged_data.command_error, 0)
            assert_equal(logged_data.command_started[0].data, expected_command_started_data)
            assert_equal(logged_data.command_finished[0].data, expected_command_finished_data)

    @override_settings(SECURITY_LOG_STRING_IO_FLUSH_TIMEOUT=0)
    def test_command_log_string_io_flush_timeout_should_changed(self):
        with capture_security_logs() as logged_data:
            test_call_command('test_command')
            assert_length_equal(logged_data.command_output_updated, 21)

    def test_error_command_should_be_logged(self):
        expected_command_started_data = {
            'name': 'test_error_command',
            'input': '',
            'is_executed_from_command_line': False,
            'start': all_eq_obj,
        }
        expected_command_error_data = {
            **expected_command_started_data,
            'error_message': not_none_eq_obj,
            'stop': all_eq_obj,
        }
        with capture_security_logs() as logged_data:
            with assert_raises(RuntimeError):
                test_call_command('test_error_command')
            assert_length_equal(logged_data.command_started, 1)
            assert_length_equal(logged_data.command_finished, 0)
            assert_length_equal(logged_data.command_error, 1)
            assert_equal(logged_data.command_started[0].data, expected_command_started_data)
            assert_equal(logged_data.command_error[0].data, expected_command_error_data)

    @responses.activate
    @data_consumer('create_user')
    def test_command_with_response_should_be_logged_with_parent_data(self, user):
        responses.add(responses.POST, 'http://localhost/test', body='test')
        with log_with_data(related_objects=[user], slug='TEST', extra_data={'test': 'test'}):
            with capture_security_logs() as logged_data:
                test_call_command('test_command_with_response')
                command_logger = logged_data.command[0]
                output_request_logger = logged_data.output_request[0]
                assert_equal(output_request_logger.parent_with_id, command_logger)
                assert_equal(command_logger.slug, 'TEST')
                assert_equal(command_logger.related_objects, {user})
                assert_equal(command_logger.extra_data, {'test': 'test'})
                assert_equal(output_request_logger.slug, 'TEST')
                assert_equal(output_request_logger.related_objects, {user})
                assert_equal(output_request_logger.extra_data, {'test': 'test'})

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'}, SECURITY_BACKEND_READER='sql')
    @data_consumer('create_user')
    def test_command_should_be_logged_in_sql_backend(self, user):
        with log_with_data(related_objects=[user]):
            test_call_command('test_command', verbosity=0)
            assert_equal(SQLCommandLog.objects.count(), 1)
            sql_command_log = SQLCommandLog.objects.get()
            assert_equal_model_fields(
                sql_command_log,
                name='test_command',
                input='verbosity=0',
                is_executed_from_command_line=False,
                time=(sql_command_log.stop - sql_command_log.start).total_seconds(),
                state=CommandState.SUCCEEDED,
                error_message=None,
            )
            assert_is_not_none(sql_command_log.output)
            assert_equal([rel_obj.object for rel_obj in sql_command_log.related_objects.all()], [user])
            assert_equal(get_logs_related_with_object(LoggerName.COMMAND, user), [sql_command_log])

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'}, SECURITY_BACKEND_READER='elasticsearch',
                       SECURITY_ELASTICSEARCH_AUTO_REFRESH=True)
    @data_consumer('create_user')
    def test_command_should_be_logged_in_elasticsearch_backend(self, user):
        with capture_security_logs() as logged_data:
            with log_with_data(related_objects=[user]):
                test_call_command('test_command', verbosity=0)
                elasticsearch_command_log = ElasticsearchCommandLog.get(
                    id=logged_data.command[0].id
                )
                assert_equal_model_fields(
                    elasticsearch_command_log,
                    name='test_command',
                    input='verbosity=0',
                    is_executed_from_command_line=False,
                    time=(elasticsearch_command_log.stop - elasticsearch_command_log.start).total_seconds(),
                    state=CommandState.SUCCEEDED,
                    error_message=None,
                )
                assert_is_not_none(elasticsearch_command_log.output)
                assert_equal(
                    [rel_obj for rel_obj in elasticsearch_command_log.related_objects],
                    ['default|3|{}'.format(user.id)]
                )
                assert_equal(get_logs_related_with_object(LoggerName.COMMAND, user), [elasticsearch_command_log])

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    @data_consumer('create_user')
    def test_command_should_be_logged_in_logging_backend(self, user):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.command', level='INFO') as cm:
                test_call_command('test_command', verbosity=0)
                command_log = logged_data.command[0]
                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.command:'
                        f'Command "{command_log.id}" '
                        f'with name "test_command" was started',
                        f'INFO:security.command:'
                        f'Command "{command_log.id}" '
                        f'with name "test_command" was successful',
                    ]
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    @data_consumer('create_user')
    def test_error_command_should_be_logged_in_sql_backend(self, user):
        with log_with_data(related_objects=[user]):
            with assert_raises(RuntimeError):
                test_call_command('test_error_command')
            assert_equal(SQLCommandLog.objects.count(), 1)
            sql_command_log = SQLCommandLog.objects.get()
            assert_equal_model_fields(
                sql_command_log,
                name='test_error_command',
                input='',
                is_executed_from_command_line=False,
                time=(sql_command_log.stop - sql_command_log.start).total_seconds(),
                state=CommandState.FAILED,
                output='',
            )
            assert_is_not_none(sql_command_log.error_message)
            assert_equal([rel_obj.object for rel_obj in sql_command_log.related_objects.all()], [user])

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    @data_consumer('create_user')
    def test_error_command_should_be_logged_in_elasticsearch_backend(self, user):
        with capture_security_logs() as logged_data:
            with log_with_data(related_objects=[user]):
                with assert_raises(RuntimeError):
                    test_call_command('test_error_command')
                elasticsearch_command_log = ElasticsearchCommandLog.get(
                    id=logged_data.command[0].id
                )
                assert_equal_model_fields(
                    elasticsearch_command_log,
                    name='test_error_command',
                    input='',
                    is_executed_from_command_line=False,
                    time=(elasticsearch_command_log.stop - elasticsearch_command_log.start).total_seconds(),
                    state=CommandState.FAILED,
                    output='',
                )
                assert_is_not_none(elasticsearch_command_log.error_message)
                assert_equal(
                    [rel_obj for rel_obj in elasticsearch_command_log.related_objects],
                    ['default|3|{}'.format(user.id)]
                )

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    @data_consumer('create_user')
    def test_error_command_should_be_logged_in_logging_backend(self, user):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.command', level='INFO') as cm:
                with assert_raises(RuntimeError):
                    test_call_command('test_error_command')
                command_log = logged_data.command[0]
                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.command:'
                        f'Command "{command_log.id}" '
                        f'with name "test_error_command" was started',
                        f'ERROR:security.command:'
                        f'Command "{command_log.id}" '
                        f'with name "test_error_command" failed',
                    ]
                )

    def test_data_change_should_be_connected_with_command_log(self):
        with capture_security_logs() as logged_data:
            test_call_command('create_user')
            assert_equal(
                logged_data.command[0].extra_data,
                {'reversion': {'revisions': [{'id': not_none_eq_obj}], 'total_count': 1}}
            )

    def test_only_20_data_changes_should_be_connected_with_command_log(self):
        with capture_security_logs() as logged_data:
            test_call_command('create_users')
            assert_equal(
                logged_data.command[0].extra_data,
                {
                    'reversion': {
                        'revisions': [{'id': not_none_eq_obj} for _ in range(20)],
                        'total_count': 100
                    }
                }
            )

    @override_settings(SECURITY_COMMAND_LOG_EXCLUDED_COMMANDS=('test_command',))
    def test_excluded_command_should_not_be_logged(self):
        with capture_security_logs() as logged_data:
            test_call_command('test_command')
            assert_length_equal(logged_data.command_started, 0)
            assert_length_equal(logged_data.command_finished, 0)
            assert_length_equal(logged_data.command_output_updated, 0)
            assert_length_equal(logged_data.command_error, 0)
