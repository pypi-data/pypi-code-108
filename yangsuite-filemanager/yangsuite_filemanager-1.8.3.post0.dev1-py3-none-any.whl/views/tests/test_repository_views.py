"""Testing of Django view functions for ysfilemanager.views.repository."""
import json
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


class RepoRequiredTest(object):
    """Mixin adding common test steps for views that require a repository."""

    def test_negative_no_reponame(self):
        """Invalid request - no repo specified."""
        if self.method == "POST":
            response = self.app.post(self.url, user='test', expect_errors=True)
        else:
            response = self.app.get(self.url, user='test', expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 No repository specified", response.status)

    def test_negative_bad_reponame(self):
        """Invalid request - repo specified is not a valid string."""
        if self.method == "POST":
            response = self.app.post(self.url, user='test',
                                     params={'repository': 'foo'},
                                     expect_errors=True)
        else:
            response = self.app.get(self.url, user='test',
                                    params={'repository': 'foo'},
                                    expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid repository string", response.status)

    def test_negative_no_such_repo(self):
        """Invalid request - no such repository."""
        if self.method == "POST":
            response = self.app.post(
                self.url, user='test',
                params={'repository': 'test+someotherrepo'},
                expect_errors=True)
        else:
            response = self.app.get(
                self.url, user='test',
                params={'repository': 'test+someotherrepo'},
                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such repository?", response.status)


class TestManageRepos(WebTest, LoginRequiredTest):
    """Tests for the manage_repos view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'manage_repos')

    def test_success(self):
        """If logged in, the page should be rendered successfully."""
        # Send a GET request logged in as 'test'
        response = self.app.get(self.url, user='test')
        # Should get a success response rendering the main page template
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "ysfilemanager/repository.html")


class TestGetRepos(WebTest, LoginRequiredTest):
    """Tests for the get_repos view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'get_repos')
        set_base_path(base_dir)

    def test_get_repos_ordinary_user(self):
        """Test that an ordinary user only gets that user's repositories."""
        resp = self.app.get(self.url, user='test')
        self.assertEqual(200, resp.status_code)
        data = resp.json
        self.assertEqual({'repositories': {'test': [
            {'name': 'testrepo', 'slug': 'test+testrepo'},
        ]}}, data)

    # TODO test that superuser gets all repositories listed


class TestGetRepoContents(WebTest, LoginRequiredTest, RepoRequiredTest):
    """Tests for the get_repo_contents view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'get_repo_contents')
        self.method = 'GET'
        set_base_path(base_dir)

    def test_negative_repo_not_owner(self):
        """Invalid request - user trying to inspect a repo it doesn't own."""
        response = self.app.get(self.url, user='badfiles',
                                params={'repository': 'test+testrepo'},
                                expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual("403 Only superusers may access the contents "
                         "of another user's repository", response.status)

    # TODO: test that superuser *can* inspect other user's repo

    def test_success(self):
        """Successful retrieval of the contents of a permitted repository."""
        response = self.app.get(self.url, user='test',
                                params={'repository': 'test+testrepo'})
        self.assertEqual(200, response.status_code)
        data = response.json
        self.maxDiff = None
        self.assertEqual({'modules': [
            {'name': 'Cisco-IOS-XR-ipv4-bgp-datatypes',
             'revision': '2015-08-27'},
            {'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper',
             'revision': '2015-11-09'},
            {'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1',
             'revision': '2015-11-09'},
            {'name': 'Cisco-IOS-XR-lib-keychain-act',
             'revision': '2017-04-17'},
            {'name': 'Cisco-IOS-XR-lib-keychain-cfg',
             'revision': '2015-07-30'},
            {'name': 'Cisco-IOS-XR-types', 'revision': '2015-06-29'},
            {'name': 'iana-if-type', 'revision': '2015-06-12'},
            {'name': 'ietf-inet-types', 'revision': '2010-09-24'},
            {'name': 'ietf-inet-types', 'revision': '2013-07-15'},
            {'name': 'ietf-interfaces', 'revision': '2014-05-08'},
            {'name': 'ietf-yang-types', 'revision': '2010-09-24'},
            {'name': 'ietf-yang-types', 'revision': '2013-07-15'},
            {'name': 'openconfig-if-ethernet',
             'revision': '2015-11-20'},
            {'name': 'openconfig-interfaces', 'revision': '2015-11-20'},
        ]}, data)


class TestCreateRepo(WebTest, LoginRequiredTest):
    """Tests for the create_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'create_repo')
        self.method = 'POST'

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_no_name(self):
        """Negative test - no repository name specified."""
        response = self.app.post(self.url, user='test',
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('400 No repository name given', response.status)

    def test_negative_already_exists(self):
        """Negative test - repository already exists."""
        response = self.app.post(self.url, user='test',
                                 params={'reponame': 'testrepo'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual('403 A repository by that name already exists',
                         response.status)

    def test_negative_invalid_source(self):
        """Negative test - cloning from mis-specified source repository."""
        response = self.app.post(self.url, user='test',
                                 params={'reponame': 'newrepo',
                                         'source': 'foobar'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('400 Invalid source repository string',
                         response.status)
        # Make sure repo wasn't created
        self.assertRaises(OSError, YSYangRepository, 'test', 'newrepo')

    def test_negative_nonexistent_source(self):
        """Negative test - cloning from nonexistent source repository."""
        response = self.app.post(self.url, user='test',
                                 params={'reponame': 'newrepo',
                                         'source': 'test+nosuchrepo'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual('404 No such source repository', response.status)
        # Make sure repo wasn't created
        self.assertRaises(OSError, YSYangRepository, 'test', 'newrepo')

    def test_success(self):
        """Basic success path."""
        response = self.app.post(self.url, user='test',
                                 params={'reponame': 'newrepo'})
        self.assertEqual(200, response.status_code)
        repo = YSYangRepository('test', 'newrepo')
        self.assertEqual([], repo.modules)

    def test_successful_clone(self):
        """Successfully create a repo based on another one."""
        response = self.app.post(self.url, user='test',
                                 params={'reponame': 'newrepo',
                                         'source': 'test+testrepo'})
        self.assertEqual(200, response.status_code)
        srcrepo = YSYangRepository('test', 'testrepo')
        newrepo = YSYangRepository('test', 'newrepo')
        # Module names and revisions should match, module file paths will not
        self.assertEqual([m[:2] for m in srcrepo.modules],
                         [m[:2] for m in newrepo.modules])


class TestDeleteRepo(WebTest, LoginRequiredTest, RepoRequiredTest):
    """Tests for the delete_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'delete_repo')
        self.method = 'POST'

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_repo_not_owner(self):
        """Invalid request - user trying to delete a repo it doesn't own."""
        response = self.app.post(self.url, user='badfiles',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual("403 Only superusers may delete "
                         "another user's repository", response.status)

    # TODO success test case for superuser deleting other user repo

    def test_negative_repo_in_use(self):
        """Request failure - deleing a repository with dependent yang sets."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertRegexpMatches(response.status,
                                 "^403 Unable to delete repository 'testrepo' "
                                 "because the following YANG sets.*")

    def test_success(self):
        """Basic success path."""
        # Can only delete a repo after deleting all yangsets using it
        YSYangSet.delete('test', 'xrbgpv4')
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo'})
        self.assertEqual(200, response.status_code)
        self.assertRaises(OSError, YSYangRepository, 'test', 'testrepo')


class TestDeleteModulesFromRepo(WebTest, LoginRequiredTest, RepoRequiredTest):
    """Tests for the delete_modules_from_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'delete_modules_from_repo')
        self.method = 'POST'

        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_repo_not_owner(self):
        """Invalid request - user trying to delete from repo it doesn't own."""
        response = self.app.post(self.url, user='badfiles',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual("403 Only superusers may modify "
                         "another user's repository", response.status)

    # TODO success test case for superuser deleting from other user repo

    def test_negative_modules_not_specified(self):
        """Invalid request - missing parameter."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 No modules specified", response.status)

    def test_negative_modules_malformed(self):
        """Invalid request - modules parameter is not valid JSON."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'modules': 'foo[bar'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('400 Invalid modules argument', response.status)

    def test_success(self):
        """Basic success test case."""
        self.assertIn('iana-if-type',
                      [m[0] for m in YSYangRepository('test',
                                                      'testrepo').modules])
        response = self.app.post(
            self.url, user='test',
            params={'repository': 'test+testrepo',
                    'modules': json.dumps([("iana-if-type", '2015-06-12')])})
        self.assertEqual(200, response.status_code)
        self.assertNotIn('iana-if-type',
                         [m[0] for m in YSYangRepository('test',
                                                         'testrepo').modules])


class TestCheckRepo(WebTest, LoginRequiredTest, RepoRequiredTest):
    """Tests for the check_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'check_repo')
        self.method = 'POST'
        set_base_path(base_dir)

    def test_negative_repo_not_owner(self):
        """Invalid request - user trying to check repo it doesn't own."""
        response = self.app.post(self.url, user='badfiles',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual("403 Only superusers may validate "
                         "another user's repository", response.status)

    # TODO success test case for superuser checking other user repo

    def test_success(self):
        """Basic success path test."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo'})
        self.assertEqual(200, response.status_code)


class TestShowRepoModule(WebTest, LoginRequiredTest):
    """Tests for the show_repo_module view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Get the URL this view is invoked from
        self.url = reverse(urlprefix + 'show_repo_module',
                           kwargs={'repository': 'test+testrepo',
                                   'module': 'iana-if-type'})
        set_base_path(base_dir)

    def test_negative_invalid_repo(self):
        """Invalid repository."""
        response = self.app.get(reverse(urlprefix + 'show_repo_module',
                                        kwargs={'repository': 'foobar',
                                                'module': 'iana-if-type'}),
                                user='test',
                                expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('400 Invalid repository string', response.status)

    def test_negative_no_such_repo(self):
        """Missing repository."""
        response = self.app.get(reverse(urlprefix + 'show_repo_module',
                                        kwargs={'repository': 'test+no-such',
                                                'module': 'iana-if-type'}),
                                user='test',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual('404 YANG repository not found', response.status)

    def test_negative_no_such_module(self):
        """Missing module."""
        response = self.app.get(reverse(urlprefix + 'show_repo_module',
                                        kwargs={'repository': 'test+testrepo',
                                                'module': 'no-such-module'}),
                                user='test',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual('404 Module not found', response.status)

    def test_negative_repo_not_owner(self):
        """Invalid request - user trying to inspect a repo it doesn't own."""
        response = self.app.get(self.url, user='badfiles',
                                expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual("403 Only superusers may access the contents "
                         "of another user's repository", response.status)

    # TODO: test that superuser *can* inspect other user's repo

    def test_success(self):
        """If logged in, the page should be rendered successfully."""
        # Send a GET request logged in as 'test'
        response = self.app.get(self.url, user='test')
        # Should get a success response rendering the main page template
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "ysfilemanager/module.html")
