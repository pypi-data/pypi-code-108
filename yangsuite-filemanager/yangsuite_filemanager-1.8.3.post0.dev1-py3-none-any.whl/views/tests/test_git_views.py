"""Testing of Django view functions for ysfilemanager.views.git_views."""
import os
import shutil
import tempfile
import mock

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
from .utilities import LoginRequiredTest, TargetRepoRequiredTest

base_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'tests', 'data')


class TestGitFilesToRepo(WebTest, LoginRequiredTest, TargetRepoRequiredTest):
    """Test cases for the git_files_to_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function automatically called before each test."""
        self.url = reverse(urlprefix + 'git_files_to_repo')
        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_get_status_none_in_progress(self):
        """Status check when no operation is in progress."""
        response = self.app.get(self.url, user='test',
                                expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No git operation in progress", response.status)

    def test_negative_no_url(self):
        """The url parameter is mandatory"""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 No Git repository specified", response.status)

    def test_negative_invalid_subdirectory(self):
        """The subdirectory parameter can't escape the repository."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'url': 'ignored',
                                         'subdirectory': '../..'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid subdirectory", response.status)

    @staticmethod
    def clone_from(url=None, to_path=None, branch=None):
        """Fake a git clone, to avoid slow network operations."""
        subdir = os.path.join(to_path, "yangfiles")
        os.makedirs(subdir)
        shutil.copy(os.path.join(base_dir, 'users', 'badfiles',
                                 'repositories', 'prefixcollision',
                                 'parent@2018-06-13.yang'),
                    subdir)

    @mock.patch("ysfilemanager.views.git_views.git.Repo")
    def test_negative_no_git_subdirectory(self, mock_repo):
        """Subdirectory does not exist in git repository."""
        mock_repo.clone_from = self.clone_from
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'url': 'http://foo.bar',
                                         'subdirectory': '/foo/bar/'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such subdirectory", response.status)

    @mock.patch("ysfilemanager.views.git_views.git.Repo")
    def test_success(self, mock_repo):
        mock_repo.clone_from = self.clone_from
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'url': 'http://foo.bar',
                                         'subdirectory': '/yangfiles/'})
        self.assertEqual("200 OK", response.status)
        self.maxDiff = None
        self.assertEqual({'reply': {
            'added': [['parent', '2018-06-13']],
            'errors': [],
            'updated': [],
            'unchanged': [],
        }}, response.json)
