# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Tests ysnetconf/views/task.py."""
from __future__ import unicode_literals
import json
import os.path
import os
import tempfile
import shutil

from django.urls import reverse
from django.contrib.auth.models import User
from django_webtest import WebTest
from yangsuite.paths import set_base_path, get_path
from .. import TaskHandler, reset_replay_path
from .utilities import (
    canned_input_data,
    canned_output_data,
    canned_input_str,
    clone_test_data
)
from .test_views import LoginRequiredTest


class TestSaveTask(WebTest):
    """Tests save_task function."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('yangtree:gettask')
        self.url_save = reverse('yangtree:savetask')
        self.url_save_yaml_replay = reverse('yangtree:saveyamlreplay')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html."""
        resp = self.app.get(self.url_save)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url_save)

    def test_exception_missing_args(self):
        """Missing username/category -> JSON response with error."""
        resp = self.app.post(self.url_save,
                             user='test',
                             params=json.dumps({'name': 'foobar'}),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         '400 Missing mandatory parameter')

    def test_exception_no_rpc(self):
        """No RPC's -> get JSON response with error."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_save,
                             user='test',
                             params=json.dumps(
                                 dict(name='getMgmt',
                                      category='ietf',
                                      description="get management task")),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         "500 No RPCs for getMgmt task.")
        data = resp.json
        self.assertEqual({}, data)

    def test_save_as_existing_task(self):
        """Try and save as existing task -> raise Task Exception."""
        clone_test_data(self.temp_path)
        resp = self.app.post(
            self.url_save_yaml_replay,
            user='test',
            params=json.dumps(
                {'name': 'IETF get interface',
                 'category': 'IETF',
                 'description': "get management task",
                 'segments': [canned_input_data('get_config_ietf_if.json')]}
            ),
            expect_errors=True)
        self.assertEqual(resp.status,
                         "500 IETF get interface already exists.")
        data = resp.json
        self.assertEqual({}, data)

    def test_save_as_new_task(self):
        """Try and save a new task -> Task saved."""
        clone_test_data(self.temp_path)
        resp = self.app.post(
            self.url_save_yaml_replay,
            user='test',
            params=json.dumps(dict(
                name='getconfig-interfaces',
                description="get interface configuration",
                category='default',
                segments=[canned_input_data('get_config_if.basic.json')])),
            expect_errors=False)
        self.assertEqual(resp.status,
                         "200 OK")
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual("getconfig-interfaces saved.", data['reply'])

        # Make sure it was saved correctly
        # TODO check task file contents too?
        self.assertEqual(
            canned_output_data('get_config_if.retrieved_task.yaml'),
            TaskHandler('getconfig-interfaces',
                        get_path('replays_dir', user='test'),
                        {'category': 'default'}).retrieve_replay())

    def test_save_custom_taskdata(self):
        """Save a task containing custom RPCs successfully."""
        clone_test_data(self.temp_path)

        resp = self.app.post(
            self.url_save_yaml_replay,
            user='test',
            params=json.dumps(
                    dict(name='CustomRPC',
                         description='task with custom RPCs',
                         category='default',
                         segments=canned_output_data('custom.json')[
                                                     'segments'])),
            expect_errors=False)

        self.assertEqual(resp.status, "200 OK")
        data = resp.json
        self.assertIn('reply', data)
        self.assertEqual("CustomRPC saved.", data['reply'])

        # Make sure it was saved correctly
        # TODO check task file contents too?
        self.assertEqual(
            canned_output_data('custom.retrieved_task.yaml'),
            TaskHandler('CustomRPC', get_path('replays_dir', user='test'),
                        {'category': 'default'}).retrieve_replay())

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestGetCategoryList(WebTest):
    """Test the get_category_list function."""

    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        self.url_get = reverse('yangtree:getcategories')
        set_base_path(self.testdir)

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html."""
        resp = self.app.get(self.url_get)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url_get)

    def test_get_category_list(self):
        """Get category listing."""
        resp = self.app.get(self.url_get, user='test')
        data = resp.json
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['categories'], [
            'IETF',
            'Openconfig',
            'Variables',
        ])

        resp = self.app.get(self.url_get, user='test',
                            params={'generated_only': 'true'})
        data = resp.json
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['categories'], [
            'Openconfig',
        ])


class TestGetTask(WebTest):
    """Tests get_task function."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('yangtree:gettask')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html."""
        resp = self.app.get(self.url_get)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url_get)

    def test_no_existing_task(self):
        """Task does not exist -> TaskException."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_get,
                             user='test',
                             params=dict(name='getall', category="default"),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         '500 Task "getall" does not exist')
        data = resp.json
        self.assertEqual({}, data)

    def test_get_task_list(self):
        """Get all tasks with categories files."""
        resp = self.app.post(self.url_get,
                             user='test',
                             expect_errors=False)
        data = resp.json
        self.assertEqual(resp.status_code, 200)
        comp = canned_output_data('getTaskList.json')
        for key in sorted(data):
            self.assertEqual(sorted(data[key]), sorted(comp.get(key, [])))
        thdata = TaskHandler.get_task_list(self.testdir)
        self.assertEqual(sorted(data), sorted(dict(thdata)))

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestGetReplayVariables(WebTest, LoginRequiredTest):
    """Test the get_replay_variables view function."""

    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url = reverse('yangtree:getvariables')
        set_base_path(self.testdir)

    def test_success(self):
        """Successful retrieval of variables."""
        resp = self.app.get(self.url, user='test', params={
            'category': 'variables',
            'name': 'custom-variables',
        })
        self.assertEqual(resp.json['variables'],
                         ['interface_id_1', 'interface_type'])

    def test_negative_missing_arguments(self):
        """Missing mandatory arguments."""
        resp = self.app.get(self.url, user='test', expect_errors=True)
        self.assertEqual('400 Missing mandatory arg', resp.status)


class TestEditTask(WebTest, LoginRequiredTest):
    """Test the edit_task view function."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('yangtree:gettask')
        self.url = reverse('yangtree:edittask')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def tearDown(self):
        """Burn it all to the ground"""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_success(self):
        """Successful editing of a test."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url, user='test', params=json.dumps({
            'name': 'IETF Get 2 Interfaces',
            'category': 'ietf',
            'newName': 'new name',
            'newCat': 'new category',
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual({'reply': 'IETF Get 2 Interfaces modified.'},
                         resp.json)

        path = get_path('replays_dir', user='test')
        self.assertFalse(os.path.exists(os.path.join(
            path, 'ietf', 'ietf-get-2-interfaces.json')))
        self.assertTrue(os.path.exists(os.path.join(
            path, 'new-category', 'new-name.tsk')))

    def test_negative_no_overwrite(self):
        """Fail if target destination already exists."""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url, user='test', params=json.dumps({
            'name': 'IETF Get 2 Interfaces',
            'category': 'ietf',
            'newName': 'IETF Get Interface',
            'newCat': 'ietf',
        }), expect_errors=True)
        self.assertEqual(500, resp.status_code)
        self.assertEqual('500 IETF Get 2 Interfaces already exists.',
                         resp.status)


class TestSaveTaskData(WebTest):
    """Tests save_task_data function"""
    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')
    url_get = reverse('yangtree:gettask')
    url_save = reverse('yangtree:savetaskdata')

    def setUp(self):
        """Function that will be called before the start of each test"""
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html"""
        resp = self.app.get(self.url_save)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url_save)

    def test_no_name_exception(self):
        """No task name specified -> TaskNotFoundException"""
        clone_test_data(self.temp_path)
        resp = self.app.post(self.url_save,
                             user='test',
                             params=dict(name=''),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         '400 Missing mandatory arg')
        data = resp.json
        self.assertEqual({}, data)

    def test_no_task_exception(self):
        """No task specified -> TaskNotFoundException"""
        resp = self.app.post(self.url_save,
                             user='test',
                             params=dict(name='Test'),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         "400 Missing mandatory arg")
        data = resp.json
        self.assertEqual({}, data)

    def test_save_task_data(self):
        """Specify a task to save -> Success JSON response"""
        clone_test_data(self.temp_path)
        get_resp = self.app.post(self.url_get,
                                 user='test',
                                 params=dict(name='ietf-get-interface',
                                             category='ietf'))
        resp = self.app.post(
            self.url_save,
            user='test',
            params=dict(name='ietf-get-interface',
                        category='ietf',
                        task=json.dumps(get_resp.json['task'])),
            expect_errors=False)
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn('result', data)
        self.assertEqual('ietf-get-interface data saved', data['result'])
        # Make sure output file ordering of data is self-constant.
        self.assertEqual(
            open(os.path.join(self.testdir, 'users', 'test', 'testing',
                              'replays', 'ietf',
                              'ietf-get-interface.tsk')).read(),
            open(get_path('replay_file', user='test', category='IETF',
                          replay='IETF get interface')).read())

    def tearDown(self):
        """Burn it all to the ground"""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestDeleteTask(WebTest):
    """Tests del_task_data function."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_del = reverse('yangtree:deltask')
        self.url_save = reverse('yangtree:savetask')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()

    def test_access_restriction(self):
        """No user --> login page; logged in --> results.html."""
        resp = self.app.get(self.url_del)
        self.assertRedirects(resp, "/accounts/login/?next=" + self.url_del)

    def test_no_name_exception(self):
        """Incorrect task name specified -> TaskNotFoundException."""
        resp = self.app.post(self.url_del,
                             user='test',
                             params=dict(name='Blah'),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         '400 No category specified')

        resp = self.app.post(self.url_del,
                             user='test',
                             params=dict(name='Blah', category='null'),
                             expect_errors=True)
        self.assertEqual(resp.status,
                         '500 Task "Blah" does not exist')
        data = resp.json
        self.assertEqual({}, data)

    def test_delete_task(self):
        """Specify a task to delete -> Success JSON response."""
        set_base_path(self.temp_path)
        # First create a task
        resp = self.app.post(
            self.url_save,
            user='test',
            params=canned_input_str('get_config_ietf_if.json'),
            expect_errors=False)

        self.assertEqual(resp.status, "200 OK")
        data = resp.json
        self.assertEqual('IETF get interface saved.', data['reply'])
        # Now delete the task
        resp = self.app.post(self.url_del,
                             user='test',
                             params={'name': 'IETF get interface',
                                     'category': 'IETF'},
                             expect_errors=False)
        self.assertEqual(resp.status, "200 OK")
        data = resp.json
        self.assertEqual('Deleted replay "IETF get interface"', data['reply'])

    def test_delete_multiple(self):
        """Successfully delete multiple replays in one pass."""
        clone_test_data(self.temp_path)
        cat_path = os.path.join(get_path('replays_dir', user='test'), 'ietf')
        self.assertTrue(os.path.exists(cat_path))
        resp = self.app.post(self.url_del, user='test', params={
            'names[]': ['ietf-get-interface', 'ietf-get-2-interfaces'],
            'category': 'IETF',
        })
        self.assertEqual(200, resp.status_code)
        self.assertEqual({'reply': '2 replays deleted successfully'},
                         resp.json)
        # Entire category was deleted since no remaining tests
        self.assertFalse(os.path.exists(cat_path))

    def tearDown(self):
        """Burn it all to the ground."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)


class TestDeleteCategory(WebTest, LoginRequiredTest):
    """Test the delete_category view function."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        self.url = reverse('yangtree:delcategory')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def tearDown(self):
        """Burn it all to the ground"""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_negative_nonexistent(self):
        """Fail if no such category exists."""
        resp = self.app.post(self.url, user='test',
                             params={'category': 'nonesuch'},
                             expect_errors=True)
        self.assertEqual(500, resp.status_code)
        self.assertEqual('500 No such category', resp.status)

    def test_success(self):
        """Successful deletion of a category."""
        clone_test_data(self.temp_path)
        cat_path = os.path.join(get_path('replays_dir', user='test'), 'ietf')
        self.assertTrue(os.path.exists(cat_path))
        resp = self.app.post(self.url, user='test', params={
            'category': 'IETF',
        })
        self.assertEqual(200, resp.status_code)
        self.assertFalse(os.path.exists(cat_path))


class TestChangeCategory(WebTest, LoginRequiredTest):
    """Test the change_category view function."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        self.url = reverse('yangtree:changecategory')
        set_base_path(self.testdir)
        self.temp_path = tempfile.mkdtemp()
        self.maxDiff = None

    def tearDown(self):
        """Burn it all to the ground"""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_success(self):
        """Successfully recategorize multiple replays in one pass."""
        clone_test_data(self.temp_path)
        cat_path = os.path.join(get_path('replays_dir', user='test'), 'ietf')
        self.assertTrue(os.path.exists(cat_path))
        resp = self.app.post(self.url, user='test', params={
            'replays[]': ['ietf-get-interface', 'ietf-get-2-interfaces'],
            'old_category': 'IETF',
            'new_category': 'ietf-new',
        })
        self.assertEqual(200, resp.status_code)
        self.assertEqual({'result': 'Replays successfully moved',
                          'errors': []},
                         resp.json)
        self.assertTrue(os.path.exists(cat_path))
        self.assertTrue(os.path.exists(os.path.join(
            get_path('replays_dir', user='test'), 'ietf-new',
            'ietf-get-interface.tsk')))
        self.assertTrue(os.path.exists(os.path.join(
            get_path('replays_dir', user='test'), 'ietf-new',
            'ietf-get-2-interfaces.tsk')))


class TestReplayDir(WebTest):
    """Tests for get/set/reset_top_replay_dir views."""

    csrf_checks = False
    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def setUp(self):
        """Function that will be called before the start of each test."""
        self.url_get = reverse('yangtree:getreplaydir')
        self.url_set = reverse('yangtree:setreplaydir')
        self.url_reset = reverse('yangtree:resetreplaydir')
        User.objects.create_superuser(username='test',
                                      email='admin@localhost',
                                      password='superadmin')
        set_base_path(self.testdir)

    def tearDown(self):
        """Make sure the replay path is reset, regardless."""
        reset_replay_path('test')

    def test_get_set_reset_top_replay_dir(self):
        """Test the view function success paths."""
        default_replay_dir = os.path.join(self.testdir,
                                          'users', 'test',
                                          'testing', 'replays')

        # Default replay path should be where we expect
        resp = self.app.get(self.url_get, user='test')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(default_replay_dir, resp.json['replaydir'])

        # Changing replay path should work
        resp = self.app.post(self.url_set, user='test',
                             params={'replay_dir': self.testdir,
                                     'createDirectory': str(False)})
        self.assertEqual(200, resp.status_code)
        try:
            new_dir_path = os.path.join(self.testdir, 'newdirectory')
            resp = self.app.post(self.url_set, user='test',
                                 params={'replay_dir': new_dir_path,
                                         'createDirectory': str(True)})
            self.assertEqual(200, resp.status_code)
            new_dir_path = os.path.join(self.testdir, 'newdirectory',
                                        'replays')
            self.assertEqual(new_dir_path, resp.json['replay_dir_path'])
        finally:
            shutil.rmtree(new_dir_path)

        # Resetting replay path should work
        resp = self.app.post(self.url_reset, user='test')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(default_replay_dir, resp.json['replaydir'])
        resp = self.app.get(self.url_get, user='test')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(default_replay_dir, resp.json['replaydir'])
