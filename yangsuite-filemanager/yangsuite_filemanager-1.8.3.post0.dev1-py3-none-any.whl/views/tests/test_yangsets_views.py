"""Testing of Django view functions for ysfilemanager.views.repository."""
import os
import shutil
import tempfile

from django_webtest import WebTest
try:
    # Django 2.x
    from django.urls import reverse
    urlprefix = 'filemanager:'
except ImportError:
    # Django 1.x
    from django.core.urlresolvers import reverse
    urlprefix = 'ysfilemanager:'

from yangsuite.paths import set_base_path
from ysfilemanager import YSYangSet, YSYangRepository
from .utilities import LoginRequiredTest

base_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'tests', 'data')


class YangsetRequiredTest(object):
    """Mixin adding common test steps for views that require a yangset."""

    def test_negative_no_yangset(self):
        """Invalid request - no setname specified."""
        if self.method == "POST":
            response = self.app.post(self.url, user='test', expect_errors=True)
        else:
            response = self.app.get(self.url, user='test', expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 No yangset specified", response.status)

    def test_negative_invalid_yangset(self):
        """Invalid request - malformed yangset string."""
        if self.method == "POST":
            response = self.app.post(self.url, user='test',
                                     params={'yangset': 'foobar'},
                                     expect_errors=True)
        else:
            response = self.app.get(self.url, user='test',
                                    params={'yangset': 'foobar'},
                                    expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid yangset string", response.status)


class TestManageYangsets(WebTest, LoginRequiredTest):
    """Tests for the manage_yangsets view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'manage_yangsets')

    def test_success(self):
        """If logged in, the page should be rendered successfully."""
        # Send a GET request logged in as 'test'
        response = self.app.get(self.url, user='test')
        # Should get a success response rendering the main page template
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "ysfilemanager/yangsets.html")


class TestGetYangsets(WebTest, LoginRequiredTest):
    """Tests for the get_yangsets view function."""

    def setUp(self):
        self.url = reverse(urlprefix + "get_yangsets")
        set_base_path(base_dir)

    def test_success(self):
        """By default, list only yangsets belonging to the user."""
        response = self.app.get(self.url, user='test')
        self.assertEqual(200, response.status_code)
        data = response.json
        self.assertEqual({'yangsets': {
            'test': [{'name': 'xrbgpv4', 'slug': 'test+xrbgpv4'}],
        }}, data)

    def test_success_readonly(self):
        """With the readonly flag, list all yangsets of all users."""
        response = self.app.get(self.url, user='test',
                                params={'readonly': 'true'})
        self.assertEqual(200, response.status_code)
        data = response.json
        self.assertEqual({'yangsets': {
            'test': [{'name': 'xrbgpv4', 'slug': 'test+xrbgpv4'}],
            'badfiles': [{'name': 'badfiles', 'slug': 'badfiles+badfiles'}],
            'nobody': [],
        }}, data)


class TestGetYangsetContents(WebTest, LoginRequiredTest, YangsetRequiredTest):
    """Tests for the get_yangset_contents view function."""

    def setUp(self):
        self.url = reverse(urlprefix + "get_yangset_contents")
        self.method = 'GET'
        set_base_path(base_dir)

    def test_negative_no_such_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        response = self.app.get(self.url, user='test',
                                params={'yangset': 'test+foobar'},
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such yangset", response.status)

    def test_success(self):
        """Successfully retrieve the contents of a yangset."""
        response = self.app.get(self.url, user='test',
                                params={'yangset': 'test+xrbgpv4'})
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            'modules': [
                {'name': 'Cisco-IOS-XR-ipv4-bgp-datatypes',
                 'revision': '2015-08-27'},
                {'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper',
                 'revision': '2015-11-09'},
            ],
            'repository': 'test+testrepo',
        }, response.json)


class TestGetRelatedModules(WebTest, LoginRequiredTest, YangsetRequiredTest):
    """Tests for the get_related_modules view function."""

    def setUp(self):
        self.url = reverse(urlprefix + "get_related_modules")
        self.method = 'GET'
        set_base_path(base_dir)

    def test_negative_no_such_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        response = self.app.get(self.url, user='test',
                                params={'yangset': 'test+foobar'},
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such yangset", response.status)

    def test_success(self):
        """Successfully retrieve related-modules data."""
        response = self.app.get(self.url, user='test',
                                params={'yangset': 'test+xrbgpv4'})
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            'identity_deriving_modules': [],
            'augmenter_modules': [],
            'upstream_modules': [],
            'related_modules': [{'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1',
                                 'revision': '2015-11-09'}],
        }, response.json)


class TestCreateYangset(WebTest, LoginRequiredTest):
    """Tests for the create_yangset view function."""
    csrf_checks = False

    def setUp(self):
        self.url = reverse(urlprefix + "create_yangset")
        self.method = "POST"

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_no_setname(self):
        """Set name must be specified."""
        response = self.app.post(self.url, user='test',
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 YANG set name not specified", response.status)

    def test_negative_existing_setname(self):
        """Can't create a set that already exists!"""
        response = self.app.post(self.url, user='test',
                                 # Different name, but same resulting slug
                                 params={'setname': 'xrBGPv4'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "403 User test already has a YANG set named 'xrBGPv4'",
            response.status)

    def test_negative_no_repository(self):
        """Repository slug must be specified."""
        response = self.app.post(self.url, user='test',
                                 params={'setname': 'mynewset'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 No repository name given", response.status)

    def test_negative_nonexistent_repository(self):
        """Repository slug must exist."""
        response = self.app.post(self.url, user='test',
                                 params={'setname': 'mynewset',
                                         'repository': 'test+nosuchrepo'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 Repository not found", response.status)

    def test_negative_invalid_source(self):
        """If a source yangset is specified, it must be a valid slug."""
        response = self.app.post(self.url, user='test',
                                 params={'setname': 'mynewset',
                                         'repository': 'test+testrepo',
                                         'source': 'foobar'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid source yangset", response.status)

    def test_negative_nonexistent_source(self):
        """If a source yangset is specified, it must exist."""
        response = self.app.post(self.url, user='test',
                                 params={'setname': 'mynewset',
                                         'repository': 'test+testrepo',
                                         'source': 'test+bar'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such source yangset", response.status)

    def test_success_new_yangset(self):
        """Successfully create a new, empty yangset."""
        response = self.app.post(self.url, user='test',
                                 params={'setname': 'my new set',
                                         'repository': 'test+testrepo'})
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            'reply': 'YANG set "test:my new set" created successfully',
            'slug': 'test+my-new-set'
        }, response.json)

        self.assertEqual([], YSYangSet.load("test", "my new set").modules)

    def test_success_clone_yangset(self):
        """Successfully clone an existing yangset."""
        response = self.app.post(self.url, user='test',
                                 params={'setname': 'my clone',
                                         'repository': 'test+testrepo',
                                         'source': 'test+xrbgpv4'})
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            'reply': 'YANG set "test:my clone" created successfully',
            'slug': 'test+my-clone'
        }, response.json)

        self.assertEqual(YSYangSet.load('test', 'xrbgpv4').modules,
                         YSYangSet.load('test', 'my clone').modules)


class TestUpdateYangset(WebTest, LoginRequiredTest, YangsetRequiredTest):
    """Tests for the update_yangset view function."""
    csrf_checks = False

    def setUp(self):
        self.url = reverse(urlprefix + "update_yangset")
        self.method = "POST"

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_no_such_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+foobar'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such yangset", response.status)

    def test_negative_invalid_modules(self):
        """Modules parameter must be a JSON list."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+xrbgpv4',
                                         'modules': 'iana-if-type'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid modules argument - must be a JSON list",
                         response.status)

    def test_negative_invalid_operation(self):
        """Operation, if specified, must be either "replace" or "add"."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+xrbgpv4',
                                         'modules': '["iana-if-type"]',
                                         'operation': 'twister'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Unknown/invalid operation", response.status)

    def test_success_replace_modules(self):
        """Successfully replace the modules assigned to this YANG set."""
        response = self.app.post(self.url, user='test', params={
            'yangset': 'test+xrbgpv4',
            'modules': '[["iana-if-type", "2015-06-12"]]'})
        self.assertEqual(200, response.status_code)

        self.assertEqual([('iana-if-type', '2015-06-12')],
                         [m[:2] for m in YSYangSet.load('test',
                                                        'xrbgpv4').modules])

    def test_success_update_modules(self):
        """Successfully update the modules assigned to this YANG set."""
        response = self.app.post(self.url, user='test', params={
            'yangset': 'test+xrbgpv4',
            'modules': '[["iana-if-type", "2015-06-12"]]',
            'operation': 'add'})
        self.assertEqual(200, response.status_code)

        self.assertEqual([('Cisco-IOS-XR-ipv4-bgp-datatypes', '2015-08-27'),
                          ('Cisco-IOS-XR-ipv4-bgp-oc-oper', '2015-11-09'),
                          ('iana-if-type', '2015-06-12')],
                         [m[:2] for m in YSYangSet.load('test',
                                                        'xrbgpv4').modules])

    def test_success_update_repository(self):
        """Successfully update the repository this YANG set belongs to."""
        response = self.app.post(self.url, user='test', params={
            'yangset': 'test+xrbgpv4',
            'repository': 'badfiles+badrepo',
        })
        self.assertEqual(200, response.status_code)

        self.assertEqual(YSYangRepository('badfiles', 'badrepo'),
                         YSYangSet.load('test', 'xrbgpv4').repository)


class TestDeleteYangset(WebTest, LoginRequiredTest, YangsetRequiredTest):
    """Tests for the delete_yangset view function."""
    csrf_checks = False

    def setUp(self):
        self.url = reverse(urlprefix + "delete_yangset")
        self.method = "POST"

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_no_such_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+foobar'},
                                 expect_errors=True)
        # As currently implemented, this API always returns HTTP Success.
        self.assertEqual(200, response.status_code)
        self.assertEqual("foobar not found", response.json['reply'])

    def test_success(self):
        """Successful deletion of a yangset."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+xrbgpv4'})
        self.assertEqual(200, response.status_code)
        self.assertEqual("xrbgpv4 deleted", response.json['reply'])

        self.assertRaises(OSError, YSYangSet.load, 'test', 'xrbgpv4')


class TestValidateYangset(WebTest, LoginRequiredTest, YangsetRequiredTest):
    """Tests for the validate_yangset/validate_yangset_post view functions."""
    csrf_checks = False

    def setUp(self):
        self.url = reverse(urlprefix + "validate_yangset")
        self.method = "POST"

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_no_such_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+foobar'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such yangset", response.status)

    def test_success(self):
        """Successfully validate a yangset."""
        response = self.app.post(self.url, user='test',
                                 params={'yangset': 'test+xrbgpv4',
                                         'quick': 'true'})
        self.assertEqual(200, response.status_code)
        self.assertIn('reply', response.json)


class TestShowYangsetModule(WebTest, LoginRequiredTest):
    """Tests for the show_yangset_module view function."""

    def setUp(self):
        self.url = reverse(urlprefix + "show_yangset_module",
                           kwargs={'yangset': 'test+xrbgpv4',
                                   'module': 'Cisco-IOS-XR-ipv4-bgp-oc-oper'})
        self.method = 'GET'
        set_base_path(base_dir)

    def test_negative_invalid_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        self.url = reverse(urlprefix + "show_yangset_module",
                           kwargs={'yangset': 'foobar',
                                   'module': 'Cisco-IOS-XR-ipv4-bgp-oc-oper'})
        response = self.app.get(self.url, user='test',
                                expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid yangset parameter", response.status)

    def test_negative_no_such_yangset(self):
        """Negative test - requested yangset doesn't exist."""
        self.url = reverse(urlprefix + "show_yangset_module",
                           kwargs={'yangset': 'test+foobar',
                                   'module': 'Cisco-IOS-XR-ipv4-bgp-oc-oper'})
        response = self.app.get(self.url, user='test',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 YANG set not found", response.status)

    def test_negative_no_such_module(self):
        """Negative test - requested module doesn't exist."""
        self.url = reverse(urlprefix + "show_yangset_module",
                           kwargs={'yangset': 'test+xrbgpv4',
                                   'module': 'nonexistent'})
        response = self.app.get(self.url, user='test',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 Module not found", response.status)

    def test_success(self):
        response = self.app.get(self.url, user='test')
        self.assertTemplateUsed(response, "ysfilemanager/module.html")
