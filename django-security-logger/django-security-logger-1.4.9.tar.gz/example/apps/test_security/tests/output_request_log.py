import json
import responses

from requests.exceptions import ConnectionError

from django.test import override_settings

from germanium.decorators import data_consumer
from germanium.test_cases.client import ClientTestCase
from germanium.tools import (
    assert_equal, assert_raises, assert_not_in, assert_in, assert_equal_model_fields, assert_is_not_none,
    assert_length_equal, all_eq_obj, not_none_eq_obj
)

from security import requests
from security.backends.signals import (
    output_request_started, output_request_finished, output_request_error
)
from security.decorators import log_with_data
from security.enums import RequestLogState
from security.backends.sql.models import OutputRequestLog as SQLOutputRequestLog
from security.backends.elasticsearch.models import OutputRequestLog as ElasticsearchOutputRequestLog
from security.backends.testing import capture_security_logs

from .base import BaseTestCaseMixin, TRUNCATION_CHAR


@override_settings(SECURITY_BACKEND_WRITERS={})
class OutputRequestLogTestCase(BaseTestCaseMixin, ClientTestCase):

    @responses.activate
    @data_consumer('create_user')
    def test_output_request_should_be_logged(self, user):
        responses.add(responses.POST, 'https://localhost/test', body='test')
        expected_output_request_started_data = {
            'request_headers': {
                'User-Agent': not_none_eq_obj,
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Content-Length': '16'
            },
            'request_body': '{"test": "test"}',
            'method': 'POST',
            'host': 'localhost',
            'path': '/test',
            'queries': {},
            'is_secure': True,
            'start': all_eq_obj,
        }
        expected_output_request_finished_data = {
            **expected_output_request_started_data,
            'stop': all_eq_obj,
            'response_code': 200,
            'response_headers': {'Content-Type': 'text/plain'},
            'response_body': 'test',
        }
        with capture_security_logs() as logged_data:
            requests.post(
                'https://localhost/test',
                data=json.dumps({'test': 'test'}),
                slug='test',
                related_objects=[user]
            )
            assert_length_equal(logged_data.output_request_started, 1)
            assert_length_equal(logged_data.output_request_finished, 1)
            assert_length_equal(logged_data.output_request_error, 0)
            assert_equal(logged_data.output_request_started[0].data, expected_output_request_started_data)
            assert_equal(logged_data.output_request_finished[0].data, expected_output_request_finished_data)
            assert_equal(logged_data.output_request_started[0].slug, 'test')
            assert_equal(logged_data.output_request_finished[0].related_objects, [user])

    @responses.activate
    def test_output_request_error_should_be_logged(self):
        expected_output_request_started_data = {
            'request_headers': {
                'User-Agent': not_none_eq_obj,
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Content-Length': '16'
            },
            'request_body': '{"test": "test"}',
            'method': 'POST',
            'host': 'localhost',
            'path': '/test',
            'queries': {},
            'is_secure': True,
            'start': all_eq_obj,
        }
        expected_output_request_error_data = {
            **expected_output_request_started_data,
            'stop': all_eq_obj,
            'error_message': all_eq_obj
        }
        with capture_security_logs() as logged_data:
            with assert_raises(ConnectionError):
                requests.post(
                    'https://localhost/test',
                    data=json.dumps({'test': 'test'}),
                )
            assert_length_equal(logged_data.output_request_started, 1)
            assert_length_equal(logged_data.output_request_finished, 0)
            assert_length_equal(logged_data.output_request_error, 1)
            assert_equal(logged_data.output_request_started[0].data, expected_output_request_started_data)
            assert_equal(logged_data.output_request_error[0].data, expected_output_request_error_data)

    @responses.activate
    def test_response_sensitive_data_body_in_json_should_be_hidden(self):
        responses.add(responses.POST, 'http://localhost', body='test')

        with capture_security_logs() as logged_data:
            requests.post('http://localhost', data=json.dumps({'password': 'secret-password'}))
            assert_in('"password": "[Filtered]"', logged_data.output_request[0].data['request_body'])
            assert_not_in('"password": "secret-password"', logged_data.output_request[0].data['request_body'])
            assert_in('"password": "secret-password"', responses.calls[0].request.body)
            assert_not_in('"password": "[Filtered]"', responses.calls[0].request.body)

    @responses.activate
    def test_response_sensitive_headers_should_be_hidden(self):
        responses.add(responses.POST, 'http://localhost', body='test')
        with capture_security_logs() as logged_data:
            requests.post('http://localhost', headers={'token': 'secret'})
            assert_equal(logged_data.output_request[0].data['request_headers']['token'], '[Filtered]')
            assert_equal(responses.calls[0].request.headers['token'], 'secret')

    @responses.activate
    def test_response_sensitive_params_data_should_be_hidden(self):
        responses.add(responses.POST, 'http://localhost', body='test')
        with capture_security_logs() as logged_data:
            requests.post('http://localhost', params={'token': 'secret'})
            assert_equal(logged_data.output_request[0].data['queries']['token'], '[Filtered]')
            assert_equal(responses.calls[0].request.url, 'http://localhost/?token=secret')

    @responses.activate
    def test_response_more_sensitive_params_data_should_be_hidden(self):
        responses.add(responses.POST, 'http://localhost', body='test')
        with capture_security_logs() as logged_data:
            requests.post('http://localhost', params={'token': ['secret', 'secret2']})
            assert_equal(logged_data.output_request[0].data['queries']['token'], ['[Filtered]', '[Filtered]'])
            assert_equal(responses.calls[0].request.url, 'http://localhost/?token=secret&token=secret2')

    @responses.activate
    def test_response_sensitive_params_and_url_query_together_data_should_be_logged(self):
        responses.add(responses.POST, 'http://localhost', body='test')
        with capture_security_logs() as logged_data:
            requests.post('http://localhost?a=1&a=2', params={'b': '6', 'a': '3', 'c': ['5']})
            assert_equal(logged_data.output_request[0].data['queries'], {'b': '6', 'a': ['1', '2', '3'], 'c': '5'})

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    @data_consumer('create_user')
    def test_output_request_should_be_logged_in_sql_backend(self, user):
        responses.add(responses.POST, 'https://localhost/test', body='test')
        requests.post(
            'https://localhost/test',
            data=json.dumps({'test': 'test'}),
            slug='test',
            related_objects=[user]
        )
        assert_equal(SQLOutputRequestLog.objects.count(), 1)
        sql_output_request_log = SQLOutputRequestLog.objects.get()
        assert_equal_model_fields(
            sql_output_request_log,
            request_headers={
                'User-Agent': not_none_eq_obj,
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Content-Length': '16'
            },
            request_body='{"test": "test"}',
            method='POST',
            host='localhost',
            path='/test',
            queries={},
            is_secure=True,
            slug='test',
            time=(sql_output_request_log.stop - sql_output_request_log.start).total_seconds(),
            extra_data={},
            error_message=None,
            response_code=200,
            response_headers={'Content-Type': 'text/plain'},
            response_body='test',
            state=RequestLogState.INFO,
        )
        assert_equal([rel_obj.object for rel_obj in sql_output_request_log.related_objects.all()], [user])

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    @data_consumer('create_user')
    def test_output_request_should_be_logged_in_elasticsearch_backend(self, user):
        responses.add(responses.POST, 'https://localhost/test', body='test')
        with capture_security_logs() as logged_data:
            requests.post(
                'https://localhost/test',
                data=json.dumps({'test': 'test'}),
                slug='test',
                related_objects=[user]
            )
            elasticsearch_output_request_log = ElasticsearchOutputRequestLog.get(
                id=logged_data.output_request[0].id
            )
            assert_equal_model_fields(
                elasticsearch_output_request_log,
                request_headers=not_none_eq_obj,
                request_body='{"test": "test"}',
                method='POST',
                host='localhost',
                path='/test',
                queries='{}',
                is_secure=True,
                slug='test',
                time=(elasticsearch_output_request_log.stop - elasticsearch_output_request_log.start).total_seconds(),
                extra_data={},
                error_message=None,
                response_code=200,
                response_headers='{"Content-Type": "text/plain"}',
                response_body='test',
                state=RequestLogState.INFO,
            )
            assert_equal(
                [rel_obj for rel_obj in elasticsearch_output_request_log.related_objects],
                ['default|3|{}'.format(user.id)]
            )

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    @data_consumer('create_user')
    def test_output_request_should_be_logged_in_logging_backend(self, user):
        responses.add(responses.POST, 'https://localhost/test', body='test')
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.output_request', level='INFO') as cm:
                requests.post(
                    'https://localhost/test',
                    data=json.dumps({'test': 'test'}),
                    slug='test',
                    related_objects=[user]
                )
                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.output_request:'
                        f'Output request "{logged_data.output_request[0].id}" '
                        f'to "localhost" with path "/test" was started',
                        f'INFO:security.output_request:'
                        f'Output request "{logged_data.output_request[0].id}" '
                        f'to "localhost" with path "/test" was successful'
                    ]
                )

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'sql'})
    def test_error_output_request_should_be_logged_in_sql_backend(self,):
        with assert_raises(ConnectionError):
            requests.post(
                'https://localhost/test',
                data=json.dumps({'test': 'test'}),
                slug='test',
            )
        assert_equal(SQLOutputRequestLog.objects.count(), 1)
        sql_output_request_log = SQLOutputRequestLog.objects.get()
        assert_equal_model_fields(
            sql_output_request_log,
            request_headers={
                'User-Agent': not_none_eq_obj,
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Content-Length': '16'
            },
            request_body='{"test": "test"}',
            method='POST',
            host='localhost',
            path='/test',
            queries={},
            is_secure=True,
            slug='test',
            time=(sql_output_request_log.stop - sql_output_request_log.start).total_seconds(),
            extra_data={},
            response_code=None,
            response_headers=None,
            response_body=None,
            state=RequestLogState.ERROR,
        )
        assert_is_not_none(sql_output_request_log.error_message)

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'elasticsearch'})
    def test_error_output_request_should_be_logged_in_elasticsearch_backend(self):
        with capture_security_logs() as logged_data:
            with assert_raises(ConnectionError):
                requests.post(
                    'https://localhost/test',
                    data=json.dumps({'test': 'test'}),
                    slug='test',
                )
            elasticsearch_input_request_log = ElasticsearchOutputRequestLog.get(
                id=logged_data.output_request[0].id
            )
            assert_equal_model_fields(
                elasticsearch_input_request_log,
                request_headers=not_none_eq_obj,
                request_body='{"test": "test"}',
                method='POST',
                host='localhost',
                path='/test',
                queries='{}',
                is_secure=True,
                slug='test',
                time=(elasticsearch_input_request_log.stop - elasticsearch_input_request_log.start).total_seconds(),
                extra_data={},
                response_code=None,
                response_headers=None,
                response_body=None,
                state=RequestLogState.ERROR,
            )
            assert_is_not_none(elasticsearch_input_request_log.error_message)

    @responses.activate
    @override_settings(SECURITY_BACKEND_WRITERS={'logging'})
    def test_error_output_request_should_be_logged_in_logging_backend(self):
        with capture_security_logs() as logged_data:
            with self.assertLogs('security.output_request', level='INFO') as cm:
                with assert_raises(ConnectionError):
                    requests.post(
                        'https://localhost/test',
                        data=json.dumps({'test': 'test'}),
                        slug='test',
                    )
                assert_equal(
                    cm.output,
                    [
                        f'INFO:security.output_request:'
                        f'Output request "{logged_data.output_request[0].id}" '
                        f'to "localhost" with path "/test" was started',
                        f'ERROR:security.output_request:'
                        f'Output request "{logged_data.output_request[0].id}" '
                        f'to "localhost" with path "/test" failed'
                    ]
                )

    @responses.activate
    @data_consumer('create_user')
    def test_slug_and_related_data_should_be_send_to_output_request_logger(self, user):
        responses.add(responses.POST, 'https://localhost/test', body='test')
        with log_with_data(related_objects=[user], slug='TEST'):
            with capture_security_logs() as logged_data:
                requests.post(
                    'https://localhost/test',
                    data=json.dumps({'test': 'test'}),
                )
                assert_equal(logged_data.output_request[0].related_objects, {user})
                assert_equal(logged_data.output_request[0].slug, 'TEST')
