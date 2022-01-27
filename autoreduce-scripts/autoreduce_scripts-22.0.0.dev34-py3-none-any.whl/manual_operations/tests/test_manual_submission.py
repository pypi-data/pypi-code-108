# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Test cases for the manual job submission script
"""
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, Mock, patch

import h5py
import numpy as np
from autoreduce_utils.clients.connection_exception import ConnectionException
from autoreduce_utils.clients.icat_client import ICATClient
from autoreduce_utils.clients.queue_client import QueueClient
from autoreduce_utils.message.message import Message
from django.test import TestCase
from parameterized import parameterized

from autoreduce_scripts.manual_operations import manual_submission as ms
from autoreduce_scripts.manual_operations.rb_categories import RBCategory
from autoreduce_scripts.manual_operations.tests.test_manual_remove import (FakeMessage,
                                                                           create_experiment_and_instrument,
                                                                           make_test_run)


@contextmanager
def temp_hdffile():
    """
    Writes a HDF5 file into a temporary file.
    Used in tests to ensure that experiment references are read correctly.

    The location of the experiment reference number
    in the HDF5 file is standard for ISIS NXS files.
    """
    try:
        with NamedTemporaryFile() as tmpfile:
            with h5py.File(tmpfile.name, "w") as hdffile:
                # this code writes out the string the same way it's contained
                # in the datafiles - as a numpy list of bytes
                dtype = h5py.special_dtype(vlen=bytes)
                group = hdffile.create_group("information")
                group.create_dataset("experiment_identifier", data=np.array([b"1234567"], dtype=dtype))
                group.create_dataset("title", data=np.array([b"test_title"], dtype=dtype))
                yield tmpfile
    finally:
        pass


# pylint:disable=no-self-use
class TestManualSubmission(TestCase):
    """
    Test manual_submission.py
    """
    fixtures = ["status_fixture"]

    def setUp(self):
        """ Creates test variables used throughout the test suite """
        self.valid_return = ("location", "rb")

        self.experiment, self.instrument = create_experiment_and_instrument()

        self.run1 = make_test_run(self.experiment, self.instrument, "1")

    def mock_database_query_result(self, side_effects):
        """ Sets the return value(s) of database queries to those provided
        :param side_effects: A list of values to return from the database query (in sequence)"""
        mock_query_result = MagicMock(name="mock_query_result")
        mock_query_result.fetchall.side_effect = side_effects

    def make_query_return_object(self, return_from):
        """ Creates a MagicMock object in a format which mimics the format of
        an object returned from a query to ICAT or the auto-reduction database
        :param return_from: A string representing what type of return object
        to be mocked
        :return: The formatted MagicMock object """
        ret_obj = [MagicMock(name="Return object")]
        if return_from == "icat":
            ret_obj[0].location = self.valid_return[0]
            ret_obj[0].dataset.investigation.name = self.valid_return[1]
        elif return_from == "db_location":
            ret_obj[0].file_path = self.valid_return[0]
        elif return_from == "db_rb":
            ret_obj[0].reference_number = self.valid_return[1]
        return ret_obj

    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_database',
           return_value=(None, None, None))
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_icat', return_value=(None, None))
    @patch('autoreduce_scripts.manual_operations.manual_submission.read_from_datafile', return_value=None)
    def test_get_checks_database_then_icat(self, read_from_datafile, mock_from_icat, mock_from_database):
        """
        Test: Data for a given run is searched for in the database before calling ICAT
        When: get_run_data is called for a datafile which isn't in the database
        """
        ms.get_run_data("instrument", -1, "file_ext")
        mock_from_database.assert_called_once()
        mock_from_icat.assert_called_once()
        read_from_datafile.assert_called_once()

    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_database',
           return_value=("string", 1234567, "some title"))
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_icat', return_value=(None, None))
    def test_get_database_hit_skips_icat(self, mock_from_icat, mock_from_database):
        """
        Test: Data for a given run is searched for in the database before calling ICAT
        When: get_run_data is called for a datafile which isn't in the database
        """
        result = ms.get_run_data("instrument", -1, "file_ext")
        assert result[0] == "string"
        assert result[1] == 1234567
        assert result[2] == "some title"
        mock_from_database.assert_called_once()
        mock_from_icat.assert_not_called()

    def test_get_from_database_no_run(self):
        """
        Test: None is returned
        When: get_run_data_from_database can't find a ReductionRun record
        """
        result = ms.get_run_data_from_database('GEM', 1234567)
        for result_item in result:
            assert result_item is None

    def test_get_from_database(self):
        """
        Test: Data for a given run can be retrieved from the database in the expected format
        When: get_run_data_from_database is called and the data is present
        in the database
        """
        actual = ms.get_run_data_from_database('ARMI', 101)
        # Values from testing database
        expected = (FakeMessage().data, '1231231', 'Test title')
        self.assertEqual(expected, actual)

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_icat')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_icat_instrument_prefix')
    def test_get_from_icat_when_file_exists_without_zeroes(self, _, login_icat: Mock):
        """
        Test: Data for a given run can be retrieved from ICAT in the expected format
        When: get_run_data_from_icat is called and the data is present in ICAT
        """
        login_icat.return_value.execute_query.return_value = self.make_query_return_object("icat")
        loc, rb_num = ms.get_run_data_from_icat("instrument", -1, "file_ext")
        login_icat.return_value.execute_query.assert_called_once()
        self.assertEqual((loc, rb_num), self.valid_return)

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_icat')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_icat_instrument_prefix', return_value='MAR')
    def test_icat_uses_prefix_mapper(self, _, login_icat: Mock):
        """
        Test: The instrument shorthand name is used
        When: querying ICAT with function get_run_data_from_icat
        """
        icat_client = login_icat.return_value
        data_file = Mock()
        data_file.location = 'location'
        data_file.dataset.investigation.name = 'inv_name'
        # Add return here to ensure we do NOT try fall through cases
        # and do NOT have to deal with multiple calls to mock
        icat_client.execute_query.return_value = [data_file]
        actual_loc, actual_inv_name = ms.get_run_data_from_icat('MARI', '123', 'nxs')
        self.assertEqual('location', actual_loc)
        self.assertEqual('inv_name', actual_inv_name)
        login_icat.assert_called_once()
        icat_client.execute_query.assert_called_once_with("SELECT df FROM Datafile df WHERE"
                                                          " df.name = 'MAR00123.nxs' INCLUDE"
                                                          " df.dataset AS ds, ds.investigation")

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_icat')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_icat_instrument_prefix')
    def test_get_run_data_from_icat_when_first_file_not_found(self, _, login_icat: Mock):
        """
        Test: that get_run_data_from_icat can handle a number of failed ICAT
        data file search attempts before it returns valid data file and check that
        expected format is then still returned.
        When: get_run_data_from_icat is called and the file is initially not
        found in ICAT.
        """
        # icat returns: not found a number of times before file found
        login_icat.return_value.execute_query.side_effect = [None, None, None, self.make_query_return_object("icat")]
        # call the method to test
        location_and_rb = ms.get_run_data_from_icat("instrument", -1, "file_ext")
        # how many times have icat been called
        self.assertEqual(login_icat.return_value.execute_query.call_count, 4)
        # check returned format is OK
        self.assertEqual(location_and_rb, self.valid_return)

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_icat')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_icat_instrument_prefix')
    def test_get_run_data_from_icat_raises_runtimeerror(self, _, login_icat: Mock):
        """
        Test: that get_run_data_from_icat can handle a number of failed ICAT
        data file search attempts before it returns valid data file and check that
        expected format is then still returned.
        When: get_run_data_from_icat is called and the file is initially not
        found in ICAT.
        """
        # icat returns: not found a number of times before file found
        login_icat.return_value.execute_query.side_effect = [None, None, None, None]
        # call the method to test
        with self.assertRaises(RuntimeError):
            ms.get_run_data_from_icat("instrument", -1, "file_ext")

    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_database')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data_from_icat')
    def test_get_when_run_number_not_int(self, mock_from_icat, mock_from_database):
        """
        Test: A SystemExit is raised and neither the database nor ICAT are checked for data
        When: get_run_data is called with a run_number which cannot be cast to int
        """
        with self.assertRaises(ValueError):
            ms.get_run_data("instrument", "invalid run number", "file_ext")
        mock_from_icat.assert_not_called()
        mock_from_database.assert_not_called()

    def test_submit_run(self):
        """
        Test: A given run is submitted to the DataReady queue
        When: submit_run is called with valid arguments
        """
        sub_run_args = {
            "active_mq_client": MagicMock(name="QueueClient"),
            "rb_number": -1,
            "instrument": "instrument",
            "data_file_location": "data_file_location",
            "run_number": -1,
            "reduction_arguments": {
                "test_int": 123,
                "test_list": [1, 2, 3]
            },
            "user_id": 15151,
            "description": "test_description",
            "run_title": "test run title",
            "software": {
                "name": "Mantid",
                "version": "6.2.0"
            }
        }
        ms.submit_run(**sub_run_args)
        message = Message(rb_number=sub_run_args["rb_number"],
                          instrument=sub_run_args["instrument"],
                          data=sub_run_args["data_file_location"],
                          run_number=sub_run_args["run_number"],
                          facility="ISIS",
                          started_by=sub_run_args["user_id"],
                          reduction_arguments=sub_run_args["reduction_arguments"],
                          description=sub_run_args["description"],
                          run_title=sub_run_args["run_title"],
                          software=sub_run_args["software"])

        sub_run_args["active_mq_client"].send.assert_called_with('/queue/DataReady', message, priority=1)

    @patch('icat.Client')
    @patch('autoreduce_scripts.manual_operations.manual_submission.ICATClient.connect')
    def test_icat_login_valid(self, mock_connect, _):
        """
        Test: A valid ICAT client is returned
        When: We can log in via the client
        Note: We mock the connect so it does not actual perform the connect (default pass)
        """
        actual = ms.login_icat()
        self.assertIsInstance(actual, ICATClient)
        mock_connect.assert_called_once()

    @patch('icat.Client')
    @patch('autoreduce_scripts.manual_operations.manual_submission.ICATClient.connect')
    def test_icat_login_invalid(self, mock_connect, _):
        """
        Test: None is returned
        When: We are unable to log in via the icat client
        """
        con_exp = ConnectionException('icat')
        mock_connect.side_effect = con_exp
        with self.assertRaises(RuntimeError):
            ms.login_icat()
        mock_connect.assert_called_once()

    @patch('autoreduce_scripts.manual_operations.manual_submission.QueueClient.connect')
    def test_queue_login_valid(self, _):
        """
        Test: A valid Queue client is returned
        When: We can log in via the queue client
        Note: We mock the connect so it does not actual perform the connect (default pass)
        """
        actual = ms.login_queue()
        self.assertIsInstance(actual, QueueClient)

    @patch('autoreduce_scripts.manual_operations.manual_submission.QueueClient.connect')
    def test_queue_login_invalid(self, mock_connect):
        """
        Test: An exception is raised
        When: We are unable to log in via the client
        """
        con_exp = ConnectionException('Queue')
        mock_connect.side_effect = con_exp
        self.assertRaises(RuntimeError, ms.login_queue)

    def test_submit_run_no_amq(self):
        """
        Test: That there is an early return
        When: Calling submit_run with active_mq as None
        """
        with self.assertRaises(RuntimeError):
            ms.submit_run(active_mq_client=None,
                          rb_number="123",
                          instrument="instr",
                          software={
                              "name": "Mantid",
                              "version": "6.2.0"
                          },
                          data_file_location="loc",
                          run_number=123,
                          run_title="")

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_queue')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data',
           return_value=('test/file/path', "2222", "some title"))
    @patch('autoreduce_scripts.manual_operations.manual_submission.submit_run')
    def test_main_valid(self, mock_submit, mock_get_loc, mock_queue):
        """
        Test: The control methods are called in the correct order
        When: main is called and the environment (client settings, input, etc.) is valid
        """
        # Setup Mock clients
        mock_queue_client = mock_queue.return_value

        mock_reduction_script = Mock()
        mock_reduction_args = Mock()
        mock_userid = Mock()
        mock_description = Mock()
        mock_software = Mock()

        # Call functionality
        return_value = ms.main(instrument='TEST',
                               runs=1111,
                               software=mock_software,
                               reduction_script=mock_reduction_script,
                               reduction_arguments=mock_reduction_args,
                               user_id=mock_userid,
                               description=mock_description)

        # Assert
        assert len(return_value) == 1
        mock_queue.assert_called_once()
        mock_get_loc.assert_called_once_with('TEST', 1111, "nxs")
        mock_submit.assert_called_once_with(mock_queue_client,
                                            "2222",
                                            'TEST',
                                            'test/file/path',
                                            1111,
                                            run_title="some title",
                                            software=mock_software,
                                            reduction_script=mock_reduction_script,
                                            reduction_arguments=mock_reduction_args,
                                            user_id=mock_userid,
                                            description=mock_description)

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_queue')
    @patch('autoreduce_scripts.manual_operations.manual_submission.get_run_data', return_value=(None, None, None))
    @patch('autoreduce_scripts.manual_operations.manual_submission.submit_run')
    def test_main_not_found_in_icat(self, mock_submit: Mock, mock_get_loc: Mock, mock_queue: Mock):
        """
        Test: The control methods are called in the correct order
        When: main is called and the environment (client settings, input, etc.) is valid
        """
        mock_reduction_script = Mock()
        mock_reduction_args = Mock()
        mock_userid = Mock()
        mock_description = Mock()
        mock_software = Mock()

        # Call functionality
        ms.main(instrument='TEST',
                runs=1111,
                software=mock_software,
                reduction_script=mock_reduction_script,
                reduction_arguments=mock_reduction_args,
                user_id=mock_userid,
                description=mock_description)

        mock_queue.assert_called_once()
        mock_get_loc.assert_called_once()
        mock_submit.assert_not_called()

    @patch('autoreduce_scripts.manual_operations.manual_submission.login_icat', side_effect=RuntimeError)
    def test_main_bad_client(self, mock_login_icat):
        """
        Test: A RuntimeError is raised
        When: Neither ICAT or Database connections can be established
        """
        self.assertRaises(RuntimeError, ms.main, 'TEST', 1111, {"name": "Mantid", "version": "6.2.0"})
        mock_login_icat.assert_called_once()

    @parameterized.expand([
        ["210NNNN", RBCategory.DIRECT_ACCESS],
        ["211NNNN", RBCategory.RAPID_ACCESS],
        ["212NNNN", RBCategory.RAPID_ACCESS],
        ["2130NNN", RBCategory.COMMISSIONING],
        ["2135NNN", RBCategory.CALIBRATION],
        ["215NNNN", RBCategory.INDUSTRIAL_ACCESS],
        ["216NNNN", RBCategory.INTERNATIONAL_PARTNERS],
        ["219NNNN", RBCategory.XPESS_ACCESS],
        ["214NNNN", RBCategory.UNCATEGORIZED],
        ["217NNNN", RBCategory.UNCATEGORIZED],
        ["218NNNN", RBCategory.UNCATEGORIZED],
        ["99999999999", RBCategory.UNCATEGORIZED],
        ["0", RBCategory.UNCATEGORIZED],
        ["1234", RBCategory.UNCATEGORIZED],
    ])
    def test_categorize_rb_number(self, rb_num, expected_category):
        """
        Test that the RB number is categorized correctly depending on the numbers in it.
        """
        assert ms.categorize_rb_number(rb_num) == expected_category

    def test_read_rb_from_datafile(self):
        """
        Test that the rb number can be read from the datafile's
        experiment_reference HDF5 group
        """
        with temp_hdffile() as tmpfile:
            # replace / with \\ so that it looks like a Windows path
            ms.read_from_datafile(tmpfile.name.replace("/", "\\\\"), "experiment_identifier")

    def test_read_rb_from_datafile_no_rb_number(self):
        """
        Test that a RuntimeError is raised if the rb number is
        not found in the datafile's experiment_reference HDF5 group
        """
        with NamedTemporaryFile() as tmpfile:
            with h5py.File(tmpfile.name, "w") as hdffile:
                hdffile.create_group("information")

            # replace / with \\ so that it looks like a Windows path
            with self.assertRaises(RuntimeError):
                ms.read_from_datafile(tmpfile.name.replace("/", "\\\\"), "experiment_identifier")

    def test_read_rb_from_datafile_empty_nxs(self):
        """
        Test that a RuntimeError is raised if the file provided is empty
        """
        with NamedTemporaryFile() as tmpfile:
            with h5py.File(tmpfile.name, "w"):
                pass

            # replace / with \\ so that it looks like a Windows path
            with self.assertRaises(RuntimeError):
                ms.read_from_datafile(tmpfile.name.replace("/", "\\\\"), "experiment_identifier")

    def test_icat_datafile_query(self):
        """
        Test that RuntimeError is raised if the icat_client provided is None
        """
        with self.assertRaises(RuntimeError):
            ms.icat_datafile_query(None, "test")

    def test_overwrite_icat_calibration_placeholder(self):
        """
        Test that runs with CAL_<some string> get their RB overwritten with
        one from the datafile
        """
        with temp_hdffile() as tmpfile:
            assert ms.overwrite_icat_calibration_placeholder(tmpfile.name, "CAL_TEST",
                                                             "experiment_identifier") == "1234567"

    def test_no_overwrite_icat_calibration_placeholder(self):
        """
        Test that the RB is not overwritten when CAL is not present in the string
        """
        with temp_hdffile() as tmpfile:
            assert ms.overwrite_icat_calibration_placeholder(tmpfile.name, "test_rb_number",
                                                             "experiment_identifier") == "test_rb_number"
