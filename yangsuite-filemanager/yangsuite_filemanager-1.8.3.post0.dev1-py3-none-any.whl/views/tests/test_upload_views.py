"""Testing of Django view functions for ysfilemanager.views.upload."""
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
from .utilities import LoginRequiredTest, TargetRepoRequiredTest

base_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'tests', 'data')


class TestUploadFilesToRepo(WebTest,
                            LoginRequiredTest, TargetRepoRequiredTest):
    """Test cases for the upload_files_to_repo view function."""
    csrf_checks = False

    def setUp(self):
        """Function automatically called before each test."""
        self.url = reverse(urlprefix + 'upload_files_to_repo')
        # Give us a tempory scratch space to make changes to
        self.temp_path = tempfile.mkdtemp()
        shutil.rmtree(self.temp_path)
        shutil.copytree(base_dir, self.temp_path)
        set_base_path(self.temp_path)

    def tearDown(self):
        """Function automatically called after each test."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_success(self):
        """Successful upload of files to a repo."""
        response = self.app.post(
            self.url, user='test',
            params={'repository': 'test+testrepo'},
            upload_files=[('files', 'empty@2018-07-27.yang', b'')])
        self.assertEqual(200, response.status_code)
        self.assertEqual({'reply': {
            'added': [['empty', '2018-07-27']],
            'errors': [],
            'updated': [],
            'unchanged': [],
        }}, response.json)

    def test_error(self):
        """Upload with invalid files."""
        response = self.app.post(
            self.url, user='test',
            params={'repository': 'test+testrepo'},
            upload_files=[
                (
                    'files',
                    os.path.basename(__file__),
                    open(__file__, 'rb').read(),
                ), (
                    'files',
                    'binary.yang',
                    b'\x89',
                ),
            ])
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json['reply']['added'])
        self.assertEqual([], response.json['reply']['updated'])
        self.assertEqual([], response.json['reply']['unchanged'])
        self.assertEqual([os.path.basename(__file__),
                          "Does not appear to be a .yang file"],
                         response.json['reply']['errors'][0])
        self.assertEqual(['binary.yang',
                          "'utf-8' codec can't decode byte 0x89 in position 0:"
                          " invalid start byte"],
                         response.json['reply']['errors'][1])
        self.assertEqual('No YANG files found',
                         response.json['reply']['errors'][2][1])
