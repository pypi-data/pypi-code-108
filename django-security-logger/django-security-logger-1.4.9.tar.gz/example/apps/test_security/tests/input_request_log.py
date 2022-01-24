import json

import responses

from django import get_version
from django.test import override_settings
from django.utils.encoding import force_text

from germanium.decorators import data_consumer
from germanium.test_cases.client import ClientTestCase
from germanium.tools import (
    assert_equal, assert_false, assert_http_not_found, assert_http_ok, assert_http_redirect,
    assert_http_too_many_requests, assert_in, assert_is_none, assert_is_not_none, assert_not_in,
    assert_raises, assert_true, assert_equal_model_fields, assert_length_equal, all_eq_obj
)

from security.enums import RequestLogState
from security.config import settings
from security.decorators import log_with_data
from security.backends.sql.models import InputRequestLog as SQLInputRequestLog
from security.backends.elasticsearch.models import InputRequestLog as ElasticsearchInputRequestLog

from security import requests
from security.backends.signals import (
    input_request_started, input_request_finished, input_request_error, output_request_started, output_request_finished
)
from security.backends.testing import capture_security_logs

from .base import BaseTestCaseMixin, TRUNCATION_CHAR


@override_settings(SECURITY_BACKEND_WRITERS={}, SECURITY_LOG_RESPONSE_BODY_CONTENT_TYPES=None)
class InputRequestLogTestCase(BaseTestCaseMixin, ClientTestCase):

    def test_input_request_to_homepage_should_be_logged(self):
        expected_input_request_started_data = {
            'request_headers': {'COOKIE': '[Filtered]'},
            'request_body': '',
            'user_id': None,
            'method': 'GET',
            'host': 'testserver',
            'path': '/home/',
            'queries': {'name': 'value'},
            'is_secure': False,
            'ip': '127.0.0.1',
            'start': all_eq_obj,
            'view_slug': 'home'
        }
        expected_input_request_finished_data = {
            **expected_input_request_started_data,
            'stop': all_eq_obj,
            'response_code': 200,
            'response_headers': {'Content-Type': 'text/html; charset=utf-8', 'X-Frame-Options': 'DENY'},
            'response_body': 'home page response',
        }
        with capture_security_logs() as logged_data:
            assert_http_ok(self.get('/home/?name=value'))
            assert_length_equal(logged_data.input_request_started, 1)
            assert_length_equal(logged_data.input_request_finished, 1)
            assert_length_equal(logged_data.input_request_error, 0)
            assert_equal(logged_data.input_request_started[0].data, expected_input_request_started_data)
            assert_equal(logged_data.input_request_finished[0].data, expected_input_request_finished_data)

    @data_consumer('create_user')
    def test_input_request_to_login_page_should_be_logged(self, user):
        expected_input_request_started_data = {
            'request_headers': {'COOKIE': '[Filtered]'},
            'request_body': (
                '--BoUnDaRyStRiNg\r\n'
                'Content-Disposition: form-data; name="username"\r\n'
                '\r\n'
                'test\r\n'
                '--BoUnDaRyStRiNg\r\n'
                '[Filtered]\n'
                '--BoUnDaRyStRiNg--\r\n'
            ),
            'user_id': None,
            'method': 'POST',
            'host': 'testserver',
            'path': '/admin/login/',
            'queries': {},
            'is_secure': False,
            'ip': '127.0.0.1',
            'start': all_eq_obj,
            'view_slug': 'admin:login'
        }
        expected_input_request_finished_data = {
            **expected_input_request_started_data,
            'stop': all_eq_obj,
            'response_code': 302,
            'response_headers': {
                'Cache-Control': 'max-age=0, no-cache, no-store, must-revalidate, private',
                'Content-Type': 'text/html; charset=utf-8',
                'Expires': all_eq_obj,
                'Location': '/accounts/profile/',
                'Vary': 'Cookie',
                'X-Frame-Options': 'DENY'
            },
            'response_body': '',
            'user_id': user.pk,
        }

        with capture_security_logs() as logged_data:
            assert_http_redirect(self.post('/admin/login/', data={'username': 'test', 'password': 'test'}))
            assert_length_equal(logged_data.input_request_started, 1)
            assert_length_equal(logged_data.input_request_finished, 1)
            assert_equal(logged_data.input_request_started[0].data, expected_input_request_started_data)
            assert_equal(logged_data.input_request_finished[0].data, expected_input_request_finished_data)

    def test_input_request_to_error_page_should_be_logged(self):
        expected_input_request_started_data = {
            'request_headers': {'COOKIE': '[Filtered]'},
            'request_body': '',
            'user_id': None,
            'method': 'GET',
            'host': 'testserver',
            'path': '/error/',
            'queries': {},
            'is_secure': False,
            'ip': '127.0.0.1',
            'start': all_eq_obj,
            'view_slug': 'apps.test_security.views.error_view'
        }
        expected_input_request_error_data = {
            **expected_input_request_started_data,
            'error_message': all_eq_obj,
        }
        expected_input_request_finished_data = {
            **expected_input_request_error_data,
            'stop': all_eq_obj,
            'response_code': 500,
            'response_headers': all_eq_obj,
            'response_body': all_eq_obj,
        }

        with capture_security_logs() as logged_data:
            with assert_raises(RuntimeError):
                assert_http_ok(self.get('/error/'))
            assert_length_equal(logged_data.input_request_started, 1)
            assert_length_equal(logged_data.input_request_finished, 1)
            assert_length_equal(logged_data.input_request_error, 1)
            assert_equal(logged_data.input_request_started[0].data, expected_input_request_started_data)
            assert_equal(logged_data.input_request_finished[0].data, expected_input_request_finished_data)
            assert_equal(logged_data.input_request_error[0].data, expected_input_request_error_data)

    @override_settings(SECURITY_LOG_REQUEST_IGNORE_IP=('127.0.0.1',))
    def test_ignored_client_ip_should_not_be_logged(self):
        with capture_security_logs() as logged_data:
            assert_http_ok(self.get('/home/'))
            assert_length_equal(logged_data.input_request, 0)

    @override_settings(SECURITY_LOG_REQUEST_IGNORE_URL_PATHS=('/home/',))
    def test_ignored_client_ip_should_not_be_logged(self):
        with capture_security_logs() as logged_data:
            assert_http_ok(self.get('/home/'))
            assert_length_equal(logged_data.input_request, 0)

    @override_settings(SECURITY_LOG_REQUEST_BODY_LENGTH=10)
    def test_request_body_should_be_truncated(self):
        with capture_security_logs() as logged_data:
            self.post('/admin/login/', data={'username': 20 * 'a', 'password': 20 * 'b'})
            assert_equal(len(logged_data.input_request[0].data['request_body']), 10)
            assert_true(logged_data.input_request[0].data['request_body'].endswith(TRUNCATION_CHAR))

    @override_settings(SECURITY_LOG_RESPONSE_BODY_LENGTH=10)
    def test_response_body_should_be_truncated(self):
        with capture_security_logs() as logged_data:
            self.post('/admin/login/', data={'username': 20 * 'a', 'password': 20 * 'b'})
            assert_equal(len(logged_data.input_request[0].data['response_body']), 10)
            assert_true(logged_data.input_request[0].data['response_body'].endswith(TRUNCATION_CHAR))

    @override_settings(SECURITY_LOG_REQUEST_BODY_LENGTH=None, SECURITY_HIDE_SENSITIVE_DATA=False)
    def test_request_body_truncation_should_be_turned_off(self):
        with capture_security_logs() as logged_data:
            self.post('/admin/login/', data={'username': 2000 * 'a', 'password': 2000 * 'b'})
            assert_equal(len(logged_data.input_request[0].data['request_body']), 4162)
            assert_false(logged_data.input_request[0].data['request_body'].endswith(TRUNCATION_CHAR))

    @override_settings(SECURITY_LOG_RESPONSE_BODY_LENGTH=None, SECURITY_HIDE_SENSITIVE_DATA=False)
    def test_response_body_truncation_should_be_turned_off(self):
        with capture_security_logs() as logged_data:
            response = self.post('/admin/login/', data={'username': 2000 * 'a', 'password': 2000 * 'b'})
            assert_equal(logged_data.input_request[0].data['response_body'], force_text(response.content))
            assert_false(logged_data.input_request[0].data['response_body'].endswith(TRUNCATION_CHAR))

    @override_settings(SECURITY_LOG_RESPONSE_BODY_CONTENT_TYPES=())
    def test_not_allowed_content_type_body_should_not_be_logged(self):
        with capture_security_logs() as logged_data:
            assert_http_ok(self.get('/home/'))
            assert_is_none(logged_data.input_request[0].data['response_body'])

    @override_settings(SECURITY_LOG_REQUEST_BODY_LENGTH=100, SECURITY_LOG_JSON_STRING_LENGTH=10)
    def test_json_request_data_should_be_truncated(self):
        with capture_security_logs() as logged_data:
            self.c.post('/admin/login/', data=json.dumps({'a': 50 * 'a', 'b': 50 * 'b'}),
                        content_type='application/json')
            assert_equal(
                json.loads(logged_data.input_request[0].data['request_body']),
                json.loads('{"a": "%s%s", "b": "%s%s"}' % (
                    9 * 'a', TRUNCATION_CHAR, 9 * 'b', TRUNCATION_CHAR
                ))
            )

    @override_settings(SECURITY_LOG_REQUEST_BODY_LENGTH=50, SECURITY_LOG_JSON_STRING_LENGTH=None)
    def test_json_request_data_should_not_be_truncated(self):
        with capture_security_logs() as logged_data:
            self.c.post('/admin/login/', data=json.dumps({'a': 50 * 'a'}),
                        content_type='application/json')
            assert_equal(logged_data.input_request[0].data['request_body'], '{"a": "' + 42 * 'a' + TRUNCATION_CHAR)
            assert_true(logged_data.input_request[0].data['request_body'].endswith(TRUNCATION_CHAR))

    @override_settings(SECURITY_LOG_REQUEST_BODY_LENGTH=100, SECURITY_LOG_JSON_STRING_LENGTH=10)
    def test_json_request_should_have_been_whole_truncated_values_and_inner_data_too(self):
        with capture_security_logs() as logged_data:
            self.c.post('/admin/login/', data=json.dumps({50 * 'a': 50 * 'a', 50 * 'b': 50 * 'b'}),
                        content_type='application/json')
            assert_equal(len(logged_data.input_request[0].data['request_body']), 100)
            assert_true(logged_data.input_request[0].data['request_body'].endswith(TRUNCATION_CHAR))

    @responses.activate
    def test_output_request_should_be_logged_with_input_request(self):
        with capture_security_logs() as logged_data:
            responses.add(responses.GET, 'http://localhost', body='test')
            assert_equal(self.get('/proxy/?url=http://localhost').content, b'test')
            assert_length_equal(logged_data.output_request_started, 1)
            assert_length_equal(logged_data.output_request_finished, 1)
            assert_equal(
                logged_data.output_request[0].parent_with_id,
                logged_data.input_request[0]
            )

    @responses.activate
    @data_consumer('create_user')
    def test_output_logged_request_should_be_related_with_object(self, user):
        with capture_security_logs() as logged_data:
            assert_http_redirect(self.post('/admin/login/', data={'username': 'test', 'password': 'test'}))
            responses.add(responses.GET, 'http://localhost', body='test')
            assert_equal(self.get('/proxy/?url=http://localhost').content, b'test')
            assert_equal(len(logged_data.output_request[0].related_objects), 1)
            assert_equal(list(logged_data.output_request[0].related_objects)[0], user)

    @responses.activate
    @data_consumer('create_user')
    def test_input_logged_request_should_have_set_data(self, user):
        with capture_security_logs() as logged_data:
            assert_http_redirect(self.post('/admin/login/', data={'username': 'test', 'password': 'test'}))
            assert_http_ok(self.get('/home/'))
            assert_equal(len(logged_data.input_request[1].related_objects), 1)
            assert_equal(list(logged_data.input_request[1].related_objects)[0], user)
            assert_equal(logged_data.input_request_finished[1].slug, 'user-home')

    @data_consumer('create_user')
    @override_settings(SECURITY_SENSITIVE_DATA_REPLACEMENT='(Filtered)')
    def test_sensitive_replacement_should_be_changed(self, user):
        with capture_security_logs() as logged_data:
            assert_http_redirect(self.post('/admin/login/', data={'username': 'test', 'password': 'test'}))
            assert_equal(logged_data.input_request[0].data['request_headers']['COOKIE'], '(Filtered)')

    def test_sensitive_queries_should_be_hidden(self):
        with capture_security_logs() as logged_data:
            assert_http_ok(self.get('/home/?token=test'))
            assert_equal(logged_data.input_request[0].data['queries']['token'], '[Filtered]')

    @data_consumer('create_user')
    def test_sensitive_headers_should_be_hidden(self, user):
        with capture_security_logs() as logged_data:
            assert_http_redirect(self.post('/admin/login/', data={'username': 'test', 'password': 'test'}))
            assert_equal(logged_data.input_request[0].data['request_headers']['COOKIE'], '[Filtered]')

    def test_sensitive_data_body_in_raw_form_should_be_hidden(self):
        with capture_security_logs() as logged_data:
            self.post('/admin/login/', data={'username': 'test', 'password': 'secret-password\nddd'})
            assert_in('[Filtered]', logged_data.input_request[0].data['request_body'])

    def test_sensitive_data_body_in_json_should_be_hidden(self):
        with capture_security_logs() as logged_data:
            self.c.post('/admin/login/', data=json.dumps({'username': 'test', 'password': 'secret-password'}),
                        content_type='application/json')
            assert_in('"password": "[Filtered]"', logged_data.input_request[0].data['request_body'])
            assert_not_in(
                '"password": "secret-password"', logged_data.input_request[0].data['request_body']
            )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    @data_consumer('create_user')
    def test_input_request_to_homepage_should_be_logged_in_sql_backend(self, user):
        with log_with_data(related_objects=[user]):
            assert_http_ok(self.get('/home/?name=value'))
            assert_equal(SQLInputRequestLog.objects.count(), 1)
            sql_input_request_log = SQLInputRequestLog.objects.get()
            assert_equal_model_fields(
                sql_input_request_log,
                request_headers={'COOKIE': '[Filtered]'},
                request_body='',
                user_id=None,
                method='GET',
                host='testserver',
                path='/home/',
                queries={'name': 'value'},
                is_secure=False,
                ip='127.0.0.1',
                view_slug='home',
                slug=None,
                time=(sql_input_request_log.stop - sql_input_request_log.start).total_seconds(),
                extra_data={},
                error_message=None,
                response_code=200,
                response_headers={'Content-Type': 'text/html; charset=utf-8', 'X-Frame-Options': 'DENY'},
                response_body='home page response',
                state=RequestLogState.INFO,
            )
            assert_equal([rel_obj.object for rel_obj in sql_input_request_log.related_objects.all()], [user])

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    @data_consumer('create_user')
    def test_input_request_to_homepage_should_be_logged_in_elasticsearch_backend(self, user):
        with log_with_data(related_objects=[user]):
            with capture_security_logs() as logged_data:
                assert_http_ok(self.get('/home/?name=value'))
                elasticsearch_input_request_log = ElasticsearchInputRequestLog.get(
                    id=logged_data.input_request[0].id
                )
                assert_equal_model_fields(
                    elasticsearch_input_request_log,
                    request_headers='{"COOKIE": "[Filtered]"}',
                    request_body='',
                    user_id=None,
                    method='GET',
                    host='testserver',
                    path='/home/',
                    queries='{"name": "value"}',
                    is_secure=False,
                    ip='127.0.0.1',
                    view_slug='home',
                    slug=None,
                    time=(elasticsearch_input_request_log.stop - elasticsearch_input_request_log.start).total_seconds(),
                    extra_data={},
                    error_message=None,
                    response_code=200,
                    response_headers='{"Content-Type": "text/html; charset=utf-8", "X-Frame-Options": "DENY"}',
                    response_body='home page response',
                    state=RequestLogState.INFO,
                )
                assert_equal(
                    [rel_obj for rel_obj in elasticsearch_input_request_log.related_objects],
                    ['default|3|{}'.format(user.id)]
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    def test_input_request_to_homepage_should_be_logged_in_logging_backend(self):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.input_request', level='INFO') as cm:
                assert_http_ok(self.get('/home/?name=value'))
                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.input_request:'
                        f'Input request "{logged_data.input_request[0].id}" '
                        f'to "testserver" with path "/home/" was started',
                        f'INFO:security.input_request:'
                        f'Input request "{logged_data.input_request[0].id}" '
                        f'to "testserver" with path "/home/" was finished'
                    ]
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    def test_input_request_to_error_page_should_be_logged_in_sql_backend(self):
        with assert_raises(RuntimeError):
            self.get('/error/')
        assert_equal(SQLInputRequestLog.objects.count(), 1)
        sql_input_request_log = SQLInputRequestLog.objects.get()
        assert_equal_model_fields(
            sql_input_request_log,
            method='GET',
            path='/error/',
            time=(sql_input_request_log.stop - sql_input_request_log.start).total_seconds(),
            response_code=500,
            state=RequestLogState.ERROR,
        )
        assert_is_not_none(sql_input_request_log.error_message)

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    def test_input_request_to_error_page_should_be_logged_in_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            with assert_raises(RuntimeError):
                self.get('/error/')
            elasticsearch_input_request_log = ElasticsearchInputRequestLog.get(
                id=logged_data.input_request[0].id
            )
            assert_equal_model_fields(
                elasticsearch_input_request_log,
                method='GET',
                path='/error/',
                time=(elasticsearch_input_request_log.stop - elasticsearch_input_request_log.start).total_seconds(),
                response_code=500,
                state=RequestLogState.ERROR,
            )
            assert_is_not_none(elasticsearch_input_request_log.error_message)

    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    def test_input_request_to_error_page_should_be_logged_in_logging_backend(self):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.input_request', level='INFO') as cm:
                with assert_raises(RuntimeError):
                    self.get('/error/')
                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.input_request:'
                        f'Input request "{logged_data.input_request[0].id}" '
                        f'to "testserver" with path "/error/" was started',
                        f'ERROR:security.input_request:'
                        f'Input request "{logged_data.input_request[0].id}" '
                        f'to "testserver" with path "/error/" failed',
                        f'INFO:security.input_request:'
                        f'Input request "{logged_data.input_request[0].id}" '
                        f'to "testserver" with path "/error/" was finished'
                    ]
                )

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    def test_input_request_to_404_page_should_be_logged_in_sql_backend(self):
        assert_http_not_found(self.get('/404/'))
        assert_equal(SQLInputRequestLog.objects.count(), 1)
        sql_input_request_log = SQLInputRequestLog.objects.get()
        assert_equal_model_fields(
            sql_input_request_log,
            response_code=404,
            state=RequestLogState.WARNING,
        )

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    def test_input_request_to_404_page_should_be_logged_in_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            assert_http_not_found(self.get('/404/'))
            elasticsearch_input_request_log = ElasticsearchInputRequestLog.get(
                id=logged_data.input_request[0].id
            )
            assert_equal_model_fields(
                elasticsearch_input_request_log,
                response_code=404,
                state=RequestLogState.WARNING,
            )

    def test_decorated_view_with_hide_request_body_should_not_log_request_body(self):
        with capture_security_logs() as logged_data:
            self.post('/hide-request-body/', data={'a': 20 * 'a', 'b': 20 * 'b'})
            assert_equal(logged_data.input_request[0].data['request_body'], '[Filtered]')

    def test_decorated_view_with_log_exempt_should_not_log_request(self):
        with capture_security_logs() as logged_data:
            self.get('/log-exempt/')
            assert_length_equal(logged_data.input_request, 0)

    def test_throttling_should_not_be_raised(self):
        for _ in range(100):
            assert_http_redirect(self.get('/admin/'))

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'}, SECURITY_BACKEND_READER='sql')
    @override_settings(SECURITY_DEFAULT_THROTTLING_VALIDATORS_PATH='apps.test_security.tests.throttling_validators')
    def test_throttling_configuration_with_sql_backend_should_return_429(self):
        for _ in range(2):
            assert_http_redirect(self.get('/admin/'))
        assert_http_too_many_requests(self.get('/admin/'))

    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'}, SECURITY_BACKEND_READER='elasticsearch')
    @override_settings(
        SECURITY_DEFAULT_THROTTLING_VALIDATORS_PATH='apps.test_security.tests.throttling_validators'
    )
    def test_throttling_configuration_with_elasticsearch_backend_should_return_429(self):
        for _ in range(2):
            assert_http_redirect(self.get('/admin/'))
            ElasticsearchInputRequestLog._index.refresh()
        assert_http_too_many_requests(self.get('/admin/'))

    @override_settings(SECURITY_BACKEND_WRITERS={'testing'}, SECURITY_BACKEND_READER='testing')
    @override_settings(
        SECURITY_DEFAULT_THROTTLING_VALIDATORS_PATH='apps.test_security.tests.throttling_validators'
    )
    @capture_security_logs()
    def test_throttling_configuration_with_testing_backends_should_return_429(self):
        for _ in range(2):
            assert_http_redirect(self.get('/admin/'))
            ElasticsearchInputRequestLog._index.refresh()
        assert_http_too_many_requests(self.get('/admin/'))

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'}, SECURITY_BACKEND_READER='sql')
    @override_settings(SECURITY_DEFAULT_THROTTLING_VALIDATORS_PATH='apps.test_security.tests.throttling_validators')
    def test_decorated_view_with_throttling_exempt_should_not_raise_throttling_exception(self):
        for _ in range(20):
            assert_http_ok(self.get('/throttling-exempt/'))
        assert_http_ok(self.get('/throttling-exempt/'))

    @override_settings(SECURITY_BACKEND_WRITERS={'sql'}, SECURITY_BACKEND_READER='sql')
    def test_decorated_view_with_throttling_should_raise_throttling_exception(self):
        assert_http_ok(self.get('/extra-throttling/'))
        assert_http_too_many_requests(self.get('/extra-throttling/'))

    @data_consumer('create_user')
    def test_slug_and_related_data_should_be_send_to_input_request_logger(self, user):
        with log_with_data(related_objects=[user], slug='TEST'):
            with capture_security_logs() as logged_data:
                assert_http_ok(self.get('/home/'))
                assert_equal(logged_data.input_request[0].related_objects, {user})
                assert_equal(logged_data.input_request[0].slug, 'TEST')
