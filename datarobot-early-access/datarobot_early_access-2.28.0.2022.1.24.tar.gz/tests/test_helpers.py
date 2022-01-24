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
import os
import unittest

import six.moves.urllib.parse as urllibparse

from datarobot.helpers.eligibility_result import EligibilityResult
from datarobot.helpers.partitioning_methods import (
    BasePartitioningMethod,
    DatetimePartitioningSpecification,
    GroupTVH,
)

_here = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(_here, "fixtures")


def fixture_file_path(filename):
    return os.path.join(FIXTURES_DIR, filename)


class URLParamsTestCase(unittest.TestCase):
    def assert_has_params(self, url, **params):
        query_string = urllibparse.unquote(url).split("?")[1]
        query_parts = query_string.split("&")
        query_pairs = [param.split("=") for param in query_parts]
        query_params = {pair[0]: pair[1] for pair in query_pairs}

        for key, value in query_params.items():
            self.assertIn(key, query_params, "Expected parameter {} not found".format(key))
            self.assertEqual(query_params[key], params[key])


class HelpersTestCase(unittest.TestCase):
    def test_cant_create_without_cv(self):
        with self.assertRaises(TypeError):
            BasePartitioningMethod(validation_type="CV")

        with self.assertRaises(TypeError):
            BasePartitioningMethod(cv_method="user")

    def test_partitioning_repr(self):
        p_method = GroupTVH(
            holdout_pct=1,
            validation_pct=2,
            partition_key_cols=["one_feature", "sec feature"],
            seed=42,
        )
        assert repr(p_method).startswith("GroupTVH({")

    def test_create_with_right(self):
        p_method = BasePartitioningMethod(validation_type="CV", cv_method="user")
        self.assertEqual(p_method.validation_type, "CV")
        self.assertEqual(p_method.cv_method, "user")

    def test_collect_payload(self):
        p_method = BasePartitioningMethod(validation_type="CV", cv_method="user")
        p = p_method.collect_payload()
        self.assertTrue("validation_type" in p)
        self.assertTrue("cv_method" in p)
        self.assertTrue("partition_key_cols" in p)
        self.assertEqual(p["validation_type"], "CV")
        self.assertIsNone(p["partition_key_cols"])

    def test_datetime_collect_payload_unsupervised_mode(self):
        # if unsupervised_mode is not set or False we don't want it in payload
        spec = DatetimePartitioningSpecification("date", unsupervised_mode=False)
        payload = spec.collect_payload()
        assert "unsupervised_mode" not in payload

        # otherwise it should be present
        spec = DatetimePartitioningSpecification("date", unsupervised_mode=True)
        payload = spec.collect_payload()
        assert payload["unsupervised_mode"] is True


def test_eligiblity_result_repr():
    er = EligibilityResult(False)
    representation = str(er)
    assert "supported=False" in representation
    assert "reason=''" in representation
    assert "context=''" in representation

    er = EligibilityResult(True, reason="reason", context="context")
    representation = str(er)
    assert "supported=True" in representation
    assert "reason='reason'" in representation
    assert "context='context'" in representation


def test_eligibility_result_with_japanese(unicode_string):
    er = EligibilityResult(True, reason=unicode_string, context=unicode_string)
    print(er)  # test __repr__
