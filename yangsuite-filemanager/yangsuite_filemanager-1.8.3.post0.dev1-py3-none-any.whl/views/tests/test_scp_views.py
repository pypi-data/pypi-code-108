"""Testing of Django view functions for ysfilemanager.views.scp_views."""
import os
import shutil
import tempfile
import mock

from io import BytesIO

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


class TestSCPFilesToRepo(WebTest, LoginRequiredTest, TargetRepoRequiredTest):
    """Test cases for the scp_files_to_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function automatically called before each test."""
        self.url = reverse(urlprefix + 'scp_files_to_repo')
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
        self.assertEqual("404 No copy in progress", response.status)

    def test_negative_missing_params(self):
        """Many parameters are mandatory."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Missing mandatory parameters", response.status)

    def test_negative_bad_SSH(self):
        """SSH failure."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'host': '127.0.0.1',
                                         'ssh_username': 'not_a_real_user',
                                         'ssh_password': 'not_a_real_password',
                                         'remote_path': '/home/not_really'},
                                 expect_errors=True)
        # Could be a 401 Authentication Failed or a 500 misc SSH exception
        self.assertTrue(response.status_code == 401 or
                        response.status_code == 500)

    @mock.patch('ysfilemanager.scp_importer.paramiko.SSHClient')
    def test_negative_no_files(self, mock_sshc):
        """Successful copy of files."""
        mock_ssh = mock.MagicMock()
        mock_sshc.return_value = mock_ssh
        mock_sshc.return_value.__enter__.return_value = mock_ssh
        # returns stdin, stdout, stderr
        mock_ssh.exec_command.return_value = (BytesIO(b''),
                                              BytesIO(b''),
                                              BytesIO(b''))

        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'host': '127.0.0.1',
                                         'ssh_username': 'not_a_real_user',
                                         'ssh_password': 'not_a_real_password',
                                         'remote_path': '/home/not_really'},
                                 expect_errors=True)
        self.assertEqual("404 No files to copy", response.status)

    @mock.patch('ysfilemanager.scp_importer.scp.SCPClient')
    @mock.patch('ysfilemanager.scp_importer.paramiko.SSHClient')
    def test_success(self, mock_sshc, mock_scpc):
        """Successful copy of files."""
        mock_ssh = mock.MagicMock()
        mock_sshc.return_value = mock_ssh
        mock_sshc.return_value.__enter__.return_value = mock_ssh
        # returns stdin, stdout, stderr
        mock_ssh.exec_command.return_value = (
            BytesIO(b''),
            BytesIO(b'/home/not_really/parent@2018-06-13.yang\n'),
            BytesIO(b''))

        mock_scp = mock.MagicMock()
        mock_scpc.return_value = mock_scp
        mock_scpc.return_value.__enter__.return_value = mock_scp

        def mock_get(remote_path, local_path):
            shutil.copy(os.path.join(base_dir, 'users', 'badfiles',
                                     'repositories', 'prefixcollision',
                                     os.path.basename(remote_path)),
                        local_path)

        mock_scp.get = mock_get

        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+testrepo',
                                         'host': '127.0.0.1',
                                         'ssh_username': 'not_a_real_user',
                                         'ssh_password': 'not_a_real_password',
                                         'remote_path': '/home/not_really'},
                                 expect_errors=True)
        self.assertEqual("200 OK", response.status)
        self.assertEqual({'reply': {
            'added': [['parent', '2018-06-13']],
            'errors': [],
            'unchanged': [],
            'updated': [],
        }}, response.json)
