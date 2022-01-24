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
import unittest

from datarobot.helpers import partitioning_methods as pm
from datarobot.helpers.partitioning_methods import BasePartitioningMethod


class TestPartitionMethodDispatch(unittest.TestCase):
    def test_random_cv(self):
        partition_data = dict(cv_method="random", validation_type="CV", holdout_pct=20, reps=5)
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.RandomCV)

    def test_random_tvh(self):
        partition_data = dict(
            cv_method="random", validation_type="TVH", holdout_pct=20, validation_pct=16
        )
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.RandomTVH)

    def test_stratified_cv(self):
        partition_data = dict(cv_method="stratified", validation_type="CV", holdout_pct=20, reps=5)
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.StratifiedCV)

    def test_stratified_tvh(self):
        partition_data = dict(
            cv_method="stratified", validation_type="TVH", holdout_pct=20, validation_pct=16
        )
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.StratifiedTVH)

    def test_user_cv(self):
        partition_data = dict(
            cv_method="user",
            validation_type="CV",
            user_partition_col="partitioner",
            cv_holdout_level="holdout_level",
        )
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.UserCV)

    def test_user_tvh(self):
        partition_data = dict(
            cv_method="user",
            validation_type="TVH",
            user_partition_col="partitioner",
            training_level="training",
            validation_level="validation",
            holdout_level="holdout",
        )
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.UserTVH)

    def test_group_cv(self):
        partition_data = dict(
            cv_method="group",
            validation_type="CV",
            partition_key_cols=["groupby1", "groupby2"],
            holdout_pct=20,
            reps=5,
        )
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.GroupCV)

    def test_group_tvh(self):
        partition_data = dict(
            cv_method="group",
            validation_type="TVH",
            partition_key_cols=["groupby1", "groupby2"],
            holdout_pct=20,
            validation_pct=16,
        )
        part = BasePartitioningMethod.from_data(partition_data)
        self.assertIsInstance(part, pm.GroupTVH)

    def test_you_screwed_up(self):
        with self.assertRaises(ValueError):
            BasePartitioningMethod.from_data({"bananas": "and cream"})

    def test_none_in_none_out(self):
        part = BasePartitioningMethod.from_data(None)
        self.assertIsNone(part)
