"""Testing of Django view functions for yangsuite-gnmi."""
import json
import os

from django_webtest import WebTest
from django.contrib.auth.models import User
try:
    # Django 2.x
    from django.urls import reverse
except ImportError:
    # Django 1.x
    from django.core.urlresolvers import reverse

from yangsuite.paths import set_base_path


TESTDIR = os.path.join(os.path.dirname(__file__), 'data')


class TestRenderMainPage(WebTest):
    """Tests for the render_main_page view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Create a fake user account
        User.objects.create_user('user', 'user@localhost', 'ordinaryuser')
        # Get the URL this view is invoked from
        self.url = reverse('gnmi:main')

    def test_login_required(self):
        """If not logged in, YANG Suite should redirect to login page."""
        # Send a GET request with no associated login
        response = self.app.get(self.url)
        # We should be redirected to the login page
        self.assertRedirects(response, "/accounts/login/?next=" + self.url)

    def test_success(self):
        """If logged in, the page should be rendered successfully."""
        # Send a GET request logged in as 'user'
        response = self.app.get(self.url, user='user')
        # Should get a success response rendering the main page template
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "ysgnmi/gnmi.html")


class TestGetJsonTree(WebTest):
    """Tests for the get_json_tree view function."""

    url = reverse('gnmi:get_json_tree')
    csrf_checks = False

    def setUp(self):
        set_base_path(TESTDIR)

    def test_negative_missing_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True)
        self.assertEqual(response.status, "400 No model name(s) specified")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params={'names[]': ['hello']})
        self.assertEqual(response.status, "400 No yangset specified")

    def test_negative_invalid_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params={'names[]': ['hello'],
                                         'yangset': 'foobar?'})
        self.assertEqual(response.status, "400 Invalid yangset string")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params={'names[]': ['hello'],
                                         'yangset': 'unknown+nonexistent'})
        self.assertEqual(response.status, "404 No such yangset owner")

    # TODO: positive test cases


class TestBuildGetRequest(WebTest):
    """Tests for the build_get_request view function."""

    url = reverse('gnmi:build_get_request')
    csrf_checks = False

    def setUp(self):
        set_base_path(TESTDIR)

    def test_negative_missing_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True)
        self.assertEqual(response.status, "400 Invalid JSON")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params=json.dumps({}))
        self.assertEqual(response.status, "400 No device specified")

    def test_negative_invalid_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params="{hello world?")
        self.assertEqual(response.status, "400 Invalid JSON")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params=json.dumps({'device': 'foo'}))
        self.assertEqual(response.status, "404 No such device found")

    def test_success_empty(self):
        response = self.app.post(self.url, user='user',
                                 params=json.dumps({'device': 'mydevice'}))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json, {'gnmiMsgs': ''})

    """
    def test_success_with_content(self):
        response = self.app.post(
            self.url, user='user',
            params=json.dumps({
                'device': 'mydevice',
                'origin': 'openconfig',
                'modules': {
                    'openconfig-interfaces': {
                        'namespace_modules': {
                            'oc-if': 'openconfig-interfaces',
                        },
                        'entries': [
                            {'xpath': '/oc-if:interfaces/oc-if:interface'},
                        ],
                    },
                },
            }))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json, {
            'action': 'get_request',
            'encoding': 'JSON_IETF',
            'prefix': {
                'elem': [{'name': 'interfaces'}],
                'origin': 'openconfig',
            },
            'path': [{
                'elem': [{'name': 'interface'}],
                'origin': 'openconfig',
            }],
        })
    """


class TestBuildSetRequest(WebTest):
    """Tests for the build_set_request view function."""

    url = reverse('gnmi:build_set_request')
    csrf_checks = False

    def setUp(self):
        set_base_path(TESTDIR)

    def test_negative_missing_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True)
        self.assertEqual(response.status, "400 Invalid JSON")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params=json.dumps({}))
        self.assertEqual(response.status, "400 No device specified")

    def test_negative_invalid_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params="{hello world?")
        self.assertEqual(response.status, "400 Invalid JSON")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params=json.dumps({'device': 'foo'}))
        self.assertEqual(response.status, "404 No such device found")

    def test_success_empty(self):
        response = self.app.post(self.url, user='user',
                                 params=json.dumps({'device': 'mydevice'}))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(
            response.json,
            {'gnmiMsgs': {'error': 'No data requested from model.'}}
        )


class TestRunRequest(WebTest):
    """Tests for the run_request view function."""

    url = reverse('gnmi:run_request', args=['mydevice'])
    csrf_checks = False

    def setUp(self):
        set_base_path(TESTDIR)

    def test_negative_missing_params(self):
        response = self.app.post(self.url, user='user', expect_errors=True)
        self.assertEqual(response.status, "400 Invalid JSON")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params=json.dumps({}))
        self.assertEqual(response.status, "400 No action specified")

    def test_negative_invalid_params(self):
        url = reverse('gnmi:run_request', args=['foobar'])
        response = self.app.post(url, user='user', expect_errors=True)
        self.assertEqual(response.status, "404 No such device found")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params="hello? {")
        self.assertEqual(response.status, "400 Invalid JSON")

        response = self.app.post(self.url, user='user', expect_errors=True,
                                 params=json.dumps({'action': 'foobar'}))
        self.assertEqual(response.status, "400 Unknown action")

    # TODO positive test cases
