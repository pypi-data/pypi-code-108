# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Test cases for the manual job submission script
"""
import builtins
import socket
from typing import List, Union
from unittest import mock
from unittest.mock import DEFAULT, Mock, call, patch

from autoreduce_db.reduction_viewer.models import (Experiment, Instrument, ReductionArguments, ReductionScript, Status,
                                                   DataLocation, RunNumber, ReductionRun)
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from autoreduce_scripts.manual_operations.manual_remove import (ManualRemove, main, remove, user_input_check)

# pylint:disable=no-member,invalid-name


class FakeMessage:
    started_by = 0
    run_number = 1234567
    message = "I am a message"
    description = "This is a fake description"
    data = "/some/location"


def create_experiment_and_instrument():
    "Creates a test experiment and instrument"

    experiment, _ = Experiment.objects.get_or_create(reference_number=1231231)
    instrument, _ = Instrument.objects.get_or_create(name="ARMI", is_active=1, is_paused=0)
    return experiment, instrument


def _make_data_locations(reduction_run, message_data_loc: Union[str, List[str]]):
    """
    Create a new data location entry which has a foreign key linking it to the current
    reduction run. The file path itself will point to a datafile
    (e.g. "/isis/inst$/NDXWISH/Instrument/data/cycle_17_1/WISH00038774.nxs")
    """
    if isinstance(message_data_loc, str):
        DataLocation.objects.create(file_path=message_data_loc, reduction_run=reduction_run)
    else:
        DataLocation.objects.bulk_create(
            [DataLocation(file_path=data_loc, reduction_run=reduction_run) for data_loc in message_data_loc])


def _make_run_numbers(reduction_run, message_run_number: Union[int, List[int]]):
    """
    Creates the related RunNumber objects
    """
    if isinstance(message_run_number, int):
        RunNumber.objects.create(reduction_run=reduction_run, run_number=message_run_number)
    else:
        RunNumber.objects.bulk_create(
            [RunNumber(reduction_run=reduction_run, run_number=run_number) for run_number in message_run_number])


def create_reduction_run_record(experiment, instrument, message, run_version, script_text, status):
    """
    Creates an ORM record for the given reduction run and returns
    this record without saving it to the DB
    """

    time_now = timezone.now()
    script = ReductionScript.objects.create(text=script_text)
    arguments = ReductionArguments.objects.create(
        raw="""{"standard_vars":{"variable_str":"value1","variable_int":123,"variable_float":123.321,
        "variable_listint":[1,2,3],"variable_liststr":["a","b","c"],"variable_none":null,
        "variable_empty":"","variable_bool":true}}""",
        instrument=instrument)
    reduction_run = ReductionRun.objects.create(run_version=run_version,
                                                run_description=message.description,
                                                hidden_in_failviewer=0,
                                                admin_log='',
                                                reduction_log='',
                                                created=time_now,
                                                last_updated=time_now,
                                                experiment=experiment,
                                                instrument=instrument,
                                                status_id=status.id,
                                                started_by=message.started_by,
                                                reduction_host=socket.getfqdn(),
                                                batch_run=isinstance(message.run_number, list),
                                                script=script,
                                                arguments=arguments,
                                                run_title="Test title")
    _make_run_numbers(reduction_run, message.run_number)
    _make_data_locations(reduction_run, message.data)

    return reduction_run


def make_test_run(experiment, instrument, run_version: str):
    "Creates a test run and saves it to the database"
    status = Status.get_queued()
    fake_script_text = "scripttext"
    msg1 = FakeMessage()
    msg1.run_number = 101
    run = create_reduction_run_record(experiment, instrument, msg1, run_version, fake_script_text, status)
    run.save()
    run.data_location.create(file_path='test/file/path/2.raw')
    return run


def make_test_batch_run(experiment, instrument, run_version: str):
    "Creates a test run and saves it to the database"
    status = Status.get_queued()
    fake_script_text = "scripttext"
    msg1 = FakeMessage()
    msg1.run_number = [101, 102, 103]
    run = create_reduction_run_record(experiment, instrument, msg1, run_version, fake_script_text, status)
    run.save()
    run.data_location.create(file_path='test/file/path/2.raw')
    return run


class TestManualRemove(TestCase):
    """
    Test manual_remove.py
    """
    fixtures = ["status_fixture"]

    def setUp(self):
        self.manual_remove = ManualRemove(instrument="ARMI")
        # Setup database connection so it is possible to use
        # ReductionRun objects with valid meta data
        self.experiment, self.instrument = create_experiment_and_instrument()

        self.run1 = make_test_run(self.experiment, self.instrument, "1")
        self.run2 = make_test_run(self.experiment, self.instrument, "2")
        self.run3 = make_test_run(self.experiment, self.instrument, "3")

    def test_find_run(self):
        """
        Test: That the correct number of run versions are discovered
        When: find_run_versions_in_database is called
        """
        actual = self.manual_remove.find_run_versions_in_database(run_number=101)
        self.assertEqual(3, len(actual))

    def test_find_run_invalid(self):
        """
        Test: That no run versions are found for a run number that doesn't exist in the database
        When: find_run_versions_in_database is called
        """
        actual = self.manual_remove.find_run_versions_in_database(run_number="000")
        self.assertEqual(0, len(actual))

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.run_not_found")
    def test_process_results_not_found(self, mock_not_found):
        """
        Test: run_not_found is called
        When: No matching records are found in the database
        """
        self.manual_remove.to_delete["101"] = []
        self.manual_remove.process_results(delete_all_versions=True)
        mock_not_found.assert_called_once()
        mock_not_found.reset_mock()
        self.manual_remove.process_results(delete_all_versions=True)
        mock_not_found.assert_called_once()

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.run_not_found")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.multiple_versions_found")
    def test_process_results_single(self, mock_multi, mock_not_found):
        """
        Test: That the code does not call multiple_versions_found
        When: The results only contain single runs (not multiple versions)
        """
        self.manual_remove.to_delete["101"] = ["test"]
        self.manual_remove.process_results(delete_all_versions=False)
        mock_multi.assert_not_called()
        mock_not_found.assert_not_called()

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.multiple_versions_found")
    def test_process_results_multi(self, mock_multi_version):
        """
        Test: process_results function routes to correct function if the run has multiple versions
        When: Multiple runs / versions are found in the database

        Note: For this test the content of results[key] list does not have to be Run objects
        """
        self.manual_remove.to_delete["101"] = ["test", "test2"]
        self.manual_remove.process_results(delete_all_versions=False)
        mock_multi_version.assert_called_once()

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.multiple_versions_found")
    def test_process_results_multi_with_delete_all(self, mock_multi_version):
        """
        Test: process_results function doesn't ask for user input with delete_all_versions=True
        When: Multiple runs / versions are found in the database

        Note: For this test the content of results[key] list does not have to be Run objects
        """
        self.manual_remove.to_delete["101"] = ["test", "test2"]
        self.manual_remove.process_results(delete_all_versions=True)
        mock_multi_version.assert_not_called()

    def test_run_not_found(self):
        """
        Test: That the correct corresponding run is deleted
        When: The value of a to_delete key is empty
        """
        self.manual_remove.to_delete["101"] = []
        self.manual_remove.run_not_found("101")
        self.assertEqual(0, len(self.manual_remove.to_delete))

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input")
    @patch.object(builtins, "input")
    def test_multiple_versions_found_single_input(self, mock_input, mock_validate_csv):
        """
        Test: That the user is not asked more than once for input
        When: The input is valid
        """
        self.manual_remove.to_delete["101"] = [self.run1, self.run2, self.run3]
        mock_input.return_value = "2"
        mock_validate_csv.return_value = (True, ["2"])
        self.manual_remove.multiple_versions_found("101")

        self.assertEqual(1, mock_validate_csv.call_count)
        mock_validate_csv.assert_has_calls([call("2")])

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input")
    @patch.object(builtins, "input")
    def test_multiple_versions_retry_user_input(self, mock_input, mock_validate_csv):
        """
        Test: Input is re-validated
        When: The user initially gives incorrect input
        """
        self.manual_remove.to_delete["101"] = [self.run1, self.run2, self.run3]
        mock_input.side_effect = ["invalid", "2"]
        mock_validate_csv.side_effect = [(False, []), (True, ["2"])]
        self.manual_remove.multiple_versions_found("101")

        self.assertEqual(2, mock_validate_csv.call_count)
        mock_validate_csv.assert_has_calls([call("invalid"), call("2")])

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input")
    @patch.object(builtins, "input")
    def test_multiple_versions_remove_one(self, mock_input, mock_validate_csv):
        """
        Test: That manual_remove will remove one run version
        When: Multiple versions are found for a run and one version is inputted
        """
        self.manual_remove.to_delete["101"] = [self.run1, self.run2, self.run3]
        mock_input.return_value = "2"
        mock_validate_csv.return_value = (True, ["2"])
        self.manual_remove.multiple_versions_found("101")

        # We said to delete version 2 so it should be the only entry for that run number
        self.assertEqual(1, len(self.manual_remove.to_delete["101"]))
        self.assertEqual("2", self.manual_remove.to_delete["101"][0].run_version)

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input")
    @patch.object(builtins, "input")
    def test_multiple_versions_found_list_input(self, mock_input, mock_validate_csv):
        """
        Test: The correct versions are deleted
        When: The user asks to delete two run versions as an inputted list
        """
        self.manual_remove.to_delete["101"] = [self.run1, self.run2, self.run3]
        mock_input.return_value = "1,3"
        mock_validate_csv.return_value = (True, ["1", "3"])
        self.manual_remove.multiple_versions_found("101")

        # We said to delete versions 1 and 3 so there should be those entries to delete for that run
        self.assertEqual(2, len(self.manual_remove.to_delete["101"]))
        self.assertEqual("1", self.manual_remove.to_delete["101"][0].run_version)
        self.assertEqual("3", self.manual_remove.to_delete["101"][1].run_version)

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input")
    @patch.object(builtins, "input")
    def test_multiple_versions_found_range_input(self, mock_input, mock_validate_csv):
        """
        Test: That the correct versions are deleted
        When: The user asks to delete a range of versions
        """
        self.manual_remove.to_delete["101"] = [self.run1, self.run2, self.run3]
        mock_input.return_value = "1-3"
        mock_validate_csv.return_value = (True, ["1", "2", "3"])
        self.manual_remove.multiple_versions_found("101")

        # We said to delete versions 1, 2 and 3 so there should 3 entries to delete for that run
        self.assertEqual(3, len(self.manual_remove.to_delete["101"]))
        self.assertEqual("1", self.manual_remove.to_delete["101"][0].run_version)
        self.assertEqual("2", self.manual_remove.to_delete["101"][1].run_version)
        self.assertEqual("3", self.manual_remove.to_delete["101"][2].run_version)

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input")
    @patch.object(builtins, "input")
    def test_multiple_versions_found_range_input_reversed(self, mock_input, mock_validate_csv):
        """
        Test: That the correct versions are deleted
        When: The user asks to delete a range of versions in reverse
        """
        self.manual_remove.to_delete["101"] = [self.run1, self.run2, self.run3]
        mock_input.return_value = "3-1"
        mock_validate_csv.return_value = (True, ["1", "2", "3"])
        self.manual_remove.multiple_versions_found("101")
        # We said to delete version 2 so it should be the only entry for that run number
        self.assertEqual(3, len(self.manual_remove.to_delete["101"]))
        self.assertEqual("1", self.manual_remove.to_delete["101"][0].run_version)
        self.assertEqual("2", self.manual_remove.to_delete["101"][1].run_version)
        self.assertEqual("3", self.manual_remove.to_delete["101"][2].run_version)

    def test_validate_csv_single_val(self):
        """
        Test: For expected validation result
        When: User input contains a single run
        """
        actual = self.manual_remove.validate_csv_input("1")
        self.assertEqual((True, [1]), actual)

    def test_validate_csv_single_val_invalid(self):
        """
        Test: For expected validation result (False, [])
        When: User input validation with single value that is invalid
        """
        actual = self.manual_remove.validate_csv_input("a")
        self.assertEqual((False, []), actual)

    def test_validate_csv_list(self):
        """
        Test: For expected validation result
        When: user input contains multiple runs
        """
        actual = self.manual_remove.validate_csv_input("1,2,3")
        self.assertEqual((True, [1, 2, 3]), actual)
        actual = self.manual_remove.validate_csv_input("1-3")
        self.assertEqual((True, [1, 2, 3]), actual)

        # bad input
        actual = self.manual_remove.validate_csv_input("1-2-1")
        self.assertEqual((False, []), actual)

    def test_validate_csv_invalid(self):
        """
        Test: For expected validation result (False, [])
        When: User input is invalid type and multiple
        """
        actual = self.manual_remove.validate_csv_input("t,e,s,t")
        self.assertEqual((False, []), actual)

    # pylint:disable=no-self-use
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.process_results")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.delete_records")
    @patch("autoreduce_scripts.manual_operations.manual_remove.get_run_range", return_value=range(1, 2))
    def test_main(self, mock_get_run_range, mock_delete, mock_process, mock_find):
        """
        Test: The correct control functions are called
        When: The main() function is called
        """
        main(instrument="GEM", first_run=1)
        mock_get_run_range.assert_called_once_with(1, last_run=None)
        mock_find.assert_called_once_with(1)
        mock_process.assert_called_once()
        mock_delete.assert_called_once()

    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.process_results")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.delete_records")
    @patch("autoreduce_scripts.manual_operations.manual_remove.get_run_range")
    def test_main_with_list(self, mock_get_run_range: Mock, mock_delete: Mock, mock_process: Mock, mock_find: Mock):
        """
        Test: The correct control functions are called
        When: The main() function is called
        """
        main(instrument="GEM", first_run=[1, 2, 3])
        mock_get_run_range.assert_not_called()
        mock_find.assert_has_calls([mock.call(1), mock.call(2), mock.call(3)])
        assert mock_process.call_count == 3
        assert mock_delete.call_count == 3

    # pylint:disable=no-self-use
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.process_results")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.delete_records")
    @patch("autoreduce_scripts.manual_operations.manual_remove.user_input_check")
    @patch("autoreduce_scripts.manual_operations.manual_remove.get_run_range", return_value=range(1, 12))
    def test_main_range_greater_than_ten(self, mock_get_run_range, mock_uic, mock_delete, mock_process, mock_find):
        """
        Test: The correct control functions are called including handle_input for many runs
        When: The main() function is called
        """
        main(instrument="GEM", first_run=1, last_run=11)
        mock_get_run_range.assert_called_with(1, last_run=11)
        mock_uic.assert_called_with("GEM", range(1, 12))
        mock_find.assert_called()
        mock_process.assert_called()
        mock_delete.assert_called()

    # pylint:disable=no-self-use
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.process_results")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.delete_records")
    @patch("autoreduce_scripts.manual_operations.manual_remove.get_run_range", return_value=range(1, 10))
    def test_main_range_less_than_ten(self, mock_get_run_range, mock_delete, mock_process, mock_find):
        """
        Test: The correct control functions are called including handle_input for many runs
        When: The main() function is called
        """
        return_value = main(instrument="GEM", first_run=1, last_run=9)

        assert len(return_value) == 9
        mock_get_run_range.assert_called_with(1, last_run=9)
        mock_find.assert_called()
        mock_process.assert_called()
        mock_delete.assert_called()

    # pylint:disable=no-self-use
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.process_results")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.delete_records")
    def test_run(self, mock_delete, mock_process, mock_find):
        """
        Test: The correct control functions are called
        When: The run() function is called
        """
        remove("GEM", 1, False, False)
        mock_find.assert_called_once_with(1)
        mock_process.assert_called_once()
        mock_delete.assert_called_once()

    def test_delete_data_location(self):
        """
        Test: The correct query is run and associated records are removed
        When: Calling delete_data_location
        """
        with patch("autoreduce_scripts.manual_operations.manual_remove.DataLocation") as data_location:
            self.manual_remove.delete_data_location(123)
            data_location.objects.filter.assert_called_once_with(reduction_run_id=123)

    def test_delete_reduction_location(self):
        """
        Test: The correct query is run and associated records are removed
        When: Calling delete_reduction_location
        """
        with patch("autoreduce_scripts.manual_operations.manual_remove.ReductionLocation") as red_location:
            self.manual_remove.delete_reduction_location(123)
            red_location.objects.filter.assert_called_once_with(reduction_run_id=123)

    def test_delete_reduction_run_location(self):
        """
        Test: The correct query is run and associated records are removed
        When: Calling delete_reduction_run_location
        """
        with patch("autoreduce_scripts.manual_operations.manual_remove.ReductionRun") as red_run:
            self.manual_remove.delete_reduction_run(123)
            red_run.objects.filter.assert_called_once_with(id=123)

    def test_delete_records(self):
        """
        Test: Record deletion is attempted directly via the ReducedRun.delete method
        When: delete_records is called while self.to_delete is populated
        """
        mock_record = Mock()
        mock_record.id = 12
        self.manual_remove.to_delete = {"1234": [mock_record]}
        self.manual_remove.delete_records()
        mock_record.delete.assert_called_once()

    @patch.multiple("autoreduce_scripts.manual_operations.manual_remove.ManualRemove",
                    delete_reduction_location=DEFAULT,
                    delete_data_location=DEFAULT,
                    delete_reduction_run=DEFAULT)
    def test_delete_records_integrity_err_reverts_to_manual(self, delete_reduction_location, delete_data_location,
                                                            delete_reduction_run):
        """
        Test: If the ReducedRun.delete fails with Integrity Error
              the code reverts back to the manual deletion of each table entry
        When: delete_records is called while self.to_delete is populated
        """
        mock_record = Mock()
        mock_record.id = 12
        mock_record.delete.side_effect = IntegrityError
        self.manual_remove.to_delete = {"1234": [mock_record]}

        self.manual_remove.delete_records()

        delete_reduction_location.assert_called_once_with(12)
        delete_data_location.assert_called_once_with(12)
        delete_reduction_run.assert_called_once_with(12)

    def test_user_input_check(self):
        """
        Test: user_input_check() returns True of false
        When: Based on user input if range of runs to remove is larger than 10
        """
        with patch.object(builtins, "input", lambda _: "Y"):
            user_input_check(range(1, 11), "GEM")

        inputs = ["N", "Y"]
        with patch.object(builtins, "input", lambda _: inputs.pop()):
            user_input_check(range(1, 11), "GEM")


class TestManualRemoveBatchRuns(TestCase):
    """
    Test manual_remove.py
    """
    fixtures = ["status_fixture"]

    def setUp(self):
        self.manual_remove = ManualRemove(instrument="ARMI")
        # Setup database connection so it is possible to use
        # ReductionRun objects with valid meta data
        self.experiment, self.instrument = create_experiment_and_instrument()

        self.batch_run1 = make_test_batch_run(self.experiment, self.instrument, "1")
        self.batch_run2 = make_test_batch_run(self.experiment, self.instrument, "2")
        self.batch_run3 = make_test_batch_run(self.experiment, self.instrument, "3")

    # pylint:disable=no-self-use
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.process_results")
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.delete_records")
    def test_remove_with_mocks(self, mock_delete, mock_process, mock_find):
        """
        Test: The correct control functions are called
        When: The remove() function is called
        """
        remove("GEM", self.batch_run1.pk, False, batch_run=True)
        mock_find.assert_not_called()
        mock_process.assert_called_once()
        mock_delete.assert_called_once()

    # pylint:disable=no-self-use
    @patch("autoreduce_scripts.manual_operations.manual_remove.ManualRemove.find_run_versions_in_database")
    def test_remove_without_mocks(self, mock_find):
        """
        Test: The ReductionRun object is removed from the database
        When: The remove() function is called
        """
        pks = [self.batch_run1.pk, self.batch_run2.pk, self.batch_run3.pk]
        for pk in pks:
            remove("GEM", pk, False, batch_run=True)
            mock_find.assert_not_called()
            with self.assertRaises(ReductionRun.DoesNotExist):
                ReductionRun.objects.get(pk=pk)

    def test_find_batch_run(self):
        """
        Test: find_batch_run finds the correct run object, which should equal the one from setUp
        When: find_batch_run is called
        """
        assert self.manual_remove.find_batch_run(self.batch_run1.pk)[0] == self.batch_run1
