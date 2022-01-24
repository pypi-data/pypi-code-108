#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import datetime
import unittest

import pandas as pd
import pytest
import responses

from datarobot import errors
from datarobot.client import Client, set_client
from datarobot.errors import DataRobotDeprecationWarning
from datarobot.utils import (
    dataframe_to_buffer,
    deprecation,
    from_api,
    get_id_from_response,
    is_urlsource,
    parse_time,
    recognize_sourcedata,
    to_api,
)
from datarobot.utils.sourcedata import list_of_records_to_buffer
from tests.test_helpers import fixture_file_path
from tests.utils import warns


class TestDataframeSerialization(unittest.TestCase):
    def test_list_of_records_to_buffer(self):
        records = [{"a": "b", "c": "d"}, {"a": "x", "c": "y"}]
        expected = "a,c\r\nb,d\r\nx,y\r\n"
        buff = list_of_records_to_buffer(records)
        self.assertEqual(buff.read(), expected)

    def test_no_index_please(self):
        df = pd.DataFrame({"a": range(100), "b": range(100)})
        buff = dataframe_to_buffer(df)
        readback = pd.read_csv(buff)
        self.assertEqual(readback.columns.tolist(), ["a", "b"])

    def test_parse_time(self):
        self.assertEqual("BAD TIME", parse_time("BAD TIME"))  # returns value
        test_string_time = datetime.datetime.now().isoformat()
        self.assertIsInstance(test_string_time, str)
        self.assertIsInstance(parse_time(test_string_time), datetime.datetime)

    @responses.activate
    @pytest.mark.usefixtures("no_client_version_check")
    def test_get_id_from_response_location_header(self):
        responses.add(
            responses.POST,
            "http://nothing/",
            body="",
            adding_headers={"Location": "http://nothing/f-id/"},
        )
        client = set_client(Client(token="no_matter", endpoint="http://nothing"))
        resp = client.post("")
        self.assertEqual(get_id_from_response(resp), "f-id")

    def test_csv_buffer_is_quoted(self):
        """"
        This tests that dataframes are correctly quoted when saved back to csv, so
        that columns containing line endings won't be interpreted as multiple rows
        See: PRED-3203
        """
        df = pd.DataFrame({"A": ["test\rtest", 2], "B": ["test\n\n\n\r\ntest", 0.75]})
        buff = dataframe_to_buffer(df)
        readback = pd.read_csv(buff)
        assert df.shape[0] == readback.shape[0]


class TestFromAPI(unittest.TestCase):
    def test_nested_list_of_objects_all_changed(self):
        source = {"oneFish": [{"twoFish": "redFish"}, {"blueFish": "noFish"}]}
        result = from_api(source)
        inner = result["one_fish"]
        self.assertEqual(inner[0]["two_fish"], "redFish")
        self.assertEqual(inner[1]["blue_fish"], "noFish")

    def test_nested_objects_all_changed(self):
        source = {"oneFish": {"twoFish": "redFish"}}

        result = from_api(source)
        self.assertEqual(result["one_fish"]["two_fish"], "redFish")


def test_from_api_filter_nones():
    data_in = {
        "someValue": {"nestedNone": None, "nestedNotNone": ""},
        "listNone": [{"someValue": None, "someNotNone": ""}],
        "otherNone": None,
    }
    data_out = {"some_value": {"nested_not_none": ""}, "list_none": [{"some_not_none": ""}]}
    assert data_out == from_api(data_in)


def test_from_api_no_filter_nones():
    data_in = {
        "someValue": {"nestedNone": None, "nestedNotNone": ""},
        "listNone": [{"someValue": None, "someNotNone": ""}],
        "otherNone": None,
    }
    data_out = {
        "some_value": {"nested_none": None, "nested_not_none": ""},
        "list_none": [{"some_value": None, "some_not_none": ""}],
        "other_none": None,
    }
    assert data_out == from_api(data_in, keep_null_keys=True)


def test_from_api_keep_nones():
    data_in = {
        "someValue": {"nestedNone": None, "nestedNotNone": "", "levelTwo": {"levelThree": None}},
        "otherNone": None,
        "keepLevelOne": None,
    }
    data_out = {
        "some_value": {
            "nested_not_none": "",
            "nested_none": None,
            "level_two": {"level_three": None},
        },
        "keep_level_one": None,
    }
    assert data_out == from_api(
        data_in,
        keep_attrs=["some_value.nested_none", "some_value.level_two.level_three", "keep_level_one"],
    )


def test_from_api_multiple_underscore_ignored():
    in_data = {"samplePct__gte": 64}
    expected = {"sample_pct__gte": 64}
    assert from_api(in_data) == expected


def test_to_api_multiple_underscore_ignored():
    in_data = {"sample_pct__gte": 64}
    expected = {"samplePct__gte": 64}
    assert to_api(in_data) == expected


def test_from_api_single_letter():
    in_data = {"iAmAKey": "test"}
    expected = {"i_am_a_key": "test"}
    assert from_api(in_data) == expected


def test_to_api_single_letter():
    in_data = {"i_am_a_key": "test"}
    expected = {"iAmAKey": "test"}
    assert to_api(in_data) == expected


def test_to_api_APIObject(dummy_api_object_class, dummy_api_object_values):
    in_data = dummy_api_object_class(**dummy_api_object_values)
    expected = {
        "parakeet": dummy_api_object_values.get("parakeet"),
        "jones": dummy_api_object_values.get("jones"),
        "squakSquak": dummy_api_object_values.get("squak_squak"),
    }
    assert to_api(in_data) == expected


def test_to_api_nested_APIObjects(dummy_nested_api_object_class, dummy_api_object_values):
    in_data = dummy_nested_api_object_class(**dummy_api_object_values)
    expected = {
        "parakeet": dummy_api_object_values.get("parakeet"),
        "jones": dummy_api_object_values.get("jones"),
        "squakSquak": dummy_api_object_values.get("squak_squak"),
        "nested": {
            "parakeet": dummy_api_object_values.get("parakeet"),
            "jones": dummy_api_object_values.get("jones"),
            "squakSquak": dummy_api_object_values.get("squak_squak"),
        },
    }
    assert to_api(in_data) == expected


@pytest.mark.parametrize(
    "bad_input", ["parakeet_fail_string", 1987, ["some", "list"], ("a", "tuple")]
)
def test_to_api_fails_on_non_dict_or_object(bad_input):
    with pytest.raises(AssertionError):
        to_api(bad_input)


@deprecation.deprecated(deprecated_since_version="v0.1.2", will_remove_version="v1.2.3")
def bar(arg1, arg2):
    """
    A dummy function to use for testing the deprecation mechanisms

    Parameters
    ----------
    arg1 : int
    arg2 : int

    Returns
    -------
    total : int
        arg1 + arg2

    """
    return arg1 + arg2


@deprecation.deprecated(
    deprecated_since_version="v0.1.2",
    will_remove_version="v1.2.3",
    message="Use of `bar` is recommended instead.",
)
def foo(arg1, arg2):
    """
    A dummy function to use for testing the deprecation mechanisms

    Parameters
    ----------
    arg1 : int
    arg2 : int

    Returns
    -------
    total : int
        foo + bar

    """
    return arg1 + arg2


def test_deprecation_with_message(known_warning):
    foo(1, 2)
    w_msg = known_warning[0].message.args[0]
    assert (
        w_msg == "`foo` has been deprecated in `v0.1.2`, will be removed "
        "in `v1.2.3`. Use of `bar` is recommended instead."
    )


def test_deprecation_message(known_warning):
    bar(1, 2)
    w_instance = known_warning[0].message
    assert isinstance(w_instance, DataRobotDeprecationWarning)


class TestSourcedataUtils(unittest.TestCase):
    def setUp(self):
        self.default_fname = "predict.csv"

    def test_recognize_sourcedata_passed_dataframe(self):
        df = pd.DataFrame({"a": range(100), "b": range(100)})
        kwargs = recognize_sourcedata(df, self.default_fname)
        self.assertTrue("filelike" in kwargs)
        self.assertEqual(kwargs.get("fname"), self.default_fname)
        buff = kwargs["filelike"]
        readback = pd.read_csv(buff)
        self.assertEqual(readback.columns.tolist(), ["a", "b"])

    def test_recognize_sourcedata_passed_filelike(self):
        path = fixture_file_path("synthetic-100.csv")
        with open(path, "rb") as fd:
            kwargs = recognize_sourcedata(fd, self.default_fname)
            self.assertTrue(kwargs.get("filelike") is fd)
            self.assertEqual(kwargs.get("fname"), self.default_fname)

    def test_recognize_sourcedata_passed_filepath(self):
        file_path = fixture_file_path("synthetic-100.csv")
        kwargs = recognize_sourcedata(file_path, self.default_fname)
        self.assertEqual(kwargs.get("file_path"), file_path)
        self.assertEqual(kwargs.get("fname"), "synthetic-100.csv")

    def test_recognize_sourcedata_passed_content(self):
        content = b"a,b,c\n" + b"1,2,3\n" * 100
        kwargs = recognize_sourcedata(content, self.default_fname)
        self.assertEqual(kwargs.get("content"), content)
        self.assertEqual(kwargs.get("fname"), self.default_fname)

    def test_is_urlsource_passed_true(self):
        result = is_urlsource("http://path_to_urlsource")
        self.assertTrue(result)

    def test_is_urlsource_file_passed_true(self):
        result = is_urlsource("file://path_to_urlsource")
        self.assertTrue(result)

    def test_is_urlsource_file_passed_false(self):
        result = is_urlsource("filename")
        self.assertFalse(result)

    def test_is_urlsource_passed_false(self):
        result = is_urlsource("not_a_path_to_urlsource")
        self.assertFalse(result)

    def test_is_urlsource_s3_passed_true(self):
        result = is_urlsource("s3://path/to/a/bucket/data.csv")
        self.assertTrue(result)

    def test_fatfingered_filepath_raises(self):
        content = b"/home/datarobot/mistypefilepath.csv"
        with self.assertRaises(errors.InputNotUnderstoodError):
            recognize_sourcedata(content, self.default_fname)


def test_resource():
    """Python 3 ResourceWarning of implicitly closed files."""
    with warns():
        open(__file__)


class TestImports(unittest.TestCase):
    def test_rename(self):
        """datarobot_sdk rename."""
        with self.assertRaises(ImportError):
            import datarobot_sdk  # noqa
