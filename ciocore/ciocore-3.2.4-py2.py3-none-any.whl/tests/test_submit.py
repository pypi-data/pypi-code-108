""" test data

   isort:skip_file
"""

import unittest
from mock import patch
from mock import MagicMock

def get_required_args():
    return {
        "instance_type": "inst",
        "project": "proj",
        "tasks_data": [{"command": "a", "frames": "1"}],
        "output_path": "/a/b",
    }


class InitTest(unittest.TestCase):
    def setUp(self):
        from ciocore.conductor_submit import Submit

        self.kSubmit = Submit
        self.required_args = get_required_args()

        getuser_patcher = patch("getpass.getuser", return_value="joe.bloggs@example.com")
        self.mock_getuser = getuser_patcher.start()
        self.addCleanup(getuser_patcher.stop)

    def test_init_store_required_args(self):
        payload = self.kSubmit(self.required_args).payload
        self.assertEqual(payload["instance_type"], "inst")
        self.assertEqual(payload["project"], "proj")
        self.assertEqual(payload["output_path"], "/a/b")
        self.assertIn("command", payload["tasks_data"][0])

    def test_init_raises_if_required_arg_missing(self):
        del self.required_args["instance_type"]
        with self.assertRaises(KeyError):
            self.kSubmit(self.required_args).payload

    def test_init_store_retry_policy(self):
        args = {"autoretry_policy": "foo"}
        args.update(self.required_args)
        payload = self.kSubmit(args).payload
        self.assertEqual(payload["autoretry_policy"], "foo")

    def test_init_store_environment(self):
        args = {"environment": {"a": "1", "b": "2"}}
        args.update(self.required_args)
        payload = self.kSubmit(args).payload
        self.assertIn("a", payload["environment"])
        self.assertIn("b", payload["environment"])
        self.assertEqual(payload["environment"]["b"], "2")

    def test_init_store_user(self):
        payload = self.kSubmit(self.required_args).payload
        self.assertEqual(payload["owner"], "joe.bloggs@example.com")


class SendTest(unittest.TestCase):
    def setUp(self):
        from ciocore.conductor_submit import Submit

        self.kSubmit = Submit
        self.required_args = get_required_args()

        getuser_patcher = patch("getpass.getuser", return_value="joe.bloggs@example.com")
        self.mock_getuser = getuser_patcher.start()
        self.addCleanup(getuser_patcher.stop)

        file_utils_process_patcher = patch(
            "ciocore.file_utils.process_upload_filepaths", 
            return_value=[]
        )
        self.mock_file_utils_process = file_utils_process_patcher.start()
        self.addCleanup(file_utils_process_patcher.stop)

        make_request_patcher = patch(
            "ciocore.api_client.ApiClient.make_request",
            return_value=('{}', 201),
        )
        self.mock_make_request = make_request_patcher.start()
        self.addCleanup(make_request_patcher.stop)


    def test_send_calls_handle_local_upload_by_default(self):
        args = self.required_args
        submission = self.kSubmit(args)
        submission._handle_local_upload = MagicMock()
        submission.main()
        submission._handle_local_upload.assert_called_with({})


    def test_send_calls_enforce_md5s_if_local_upload_off_and_enforced_md5s(self):
        args = {"local_upload": False, "enforced_md5s": {"a":"1"}}
        args.update(self.required_args)
        submission = self.kSubmit(args)
        submission._enforce_md5s = MagicMock()
        submission.main()
        submission._enforce_md5s.assert_called_with({})

    def test_send_doesnt_call_enforce_md5s_if_local_upload_off_and_no_enforced_md5s(self):
        args = {"local_upload": False}
        args.update(self.required_args)
        submission = self.kSubmit(args)
        submission._enforce_md5s = MagicMock()
        submission.main()
        self.assertEqual(submission._enforce_md5s.call_count, 0)


    def test_send_raise_if_bad_response_code(self):
        make_request_patcher = patch(
            "ciocore.api_client.ApiClient.make_request",
            return_value=('{}', 404),
        )
        self.mock_make_request = make_request_patcher.start()
 
        with self.assertRaises(Exception):
            submission = self.kSubmit(self.required_args)
            submission._handle_daemon_upload = MagicMock()
            submission._handle_local_upload = MagicMock()
            submission.main()
        make_request_patcher.stop()


class uploaderTest():

    def test_smoke(self):

        from ciocore import uploader
        uploader_args = {
            "location": "here",
            "database_filepath": "/path/to/db",
            "thread_count": 4,
            "md5_caching": True,
        }
        up = uploader.Uploader(uploader_args)
        manager = up.create_manager("some_project")
        filemap = {"/a/b1": None,"/a/b2": None}
        self.assertTrue(True)
