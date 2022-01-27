from unittest.mock import Mock, call, patch

from django.test import TestCase

from autoreduce_scripts.manual_operations.manual_batch_submit import main as submit_batch_main
from autoreduce_scripts.manual_operations.tests.test_manual_remove import create_experiment_and_instrument


# pylint:disable=no-self-use
class TestManualBatchSubmission(TestCase):
    """
    Test manual_submission.py
    """
    fixtures = ["status_fixture"]

    def setUp(self) -> None:
        self.experiment, self.instrument = create_experiment_and_instrument()

    @patch('autoreduce_scripts.manual_operations.manual_batch_submit.login_queue')
    @patch('autoreduce_scripts.manual_operations.manual_batch_submit.submit_run')
    @patch('autoreduce_scripts.manual_operations.manual_batch_submit.get_run_data',
           return_value=("test_location", "test_rb", "test_title"))
    def test_main(self, mock_get_run_data: Mock, mock_submit_run: Mock, mock_login_queue: Mock):
        """Tests the main function of the manual batch submission"""
        runs = [12345, 12346]
        mock_reduction_script = Mock()
        mock_reduction_arguments = Mock()
        mock_user_id = Mock()
        mock_description = Mock()
        mock_software = Mock()
        submit_batch_main(self.instrument.name, runs, mock_software, mock_reduction_script, mock_reduction_arguments,
                          mock_user_id, mock_description)
        mock_login_queue.assert_called_once()

        mock_get_run_data.assert_has_calls(
            [call(self.instrument.name, runs[0], "nxs"),
             call(self.instrument.name, runs[1], "nxs")])

        mock_submit_run.assert_called_once_with(mock_login_queue.return_value,
                                                "test_rb",
                                                self.instrument.name, ["test_location", "test_location"],
                                                runs,
                                                run_title=["test_title", "test_title"],
                                                software=mock_software,
                                                reduction_script=mock_reduction_script,
                                                reduction_arguments=mock_reduction_arguments,
                                                user_id=mock_user_id,
                                                description=mock_description)

    @patch('autoreduce_scripts.manual_operations.manual_batch_submit.login_queue')
    @patch('autoreduce_scripts.manual_operations.manual_batch_submit.submit_run')
    @patch('autoreduce_scripts.manual_operations.manual_batch_submit.get_run_data',
           side_effect=[("test_location", "test_rb", "test_title"), ("test_location_2", "test_rb_2", "test_title_2")])
    def test_main_bad_rb(self, mock_get_run_data: Mock, mock_submit_run: Mock, mock_login_queue: Mock):
        """Tests the main function of the manual batch submission"""
        runs = [12345, 12346]

        with self.assertRaises(RuntimeError):
            submit_batch_main(self.instrument.name,
                              runs,
                              software={},
                              reduction_script="",
                              reduction_arguments={},
                              user_id=-1,
                              description="")
        mock_login_queue.assert_called_once()

        mock_get_run_data.assert_has_calls(
            [call(self.instrument.name, runs[0], "nxs"),
             call(self.instrument.name, runs[1], "nxs")])

        mock_submit_run.assert_not_called()
