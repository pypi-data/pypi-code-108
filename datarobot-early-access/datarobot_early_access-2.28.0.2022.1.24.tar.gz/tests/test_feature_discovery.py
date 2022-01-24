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

from datarobot.helpers.feature_discovery import DatasetDefinition, Relationship, SecondaryDataset


class TestFeatureDiscoveryHelper(unittest.TestCase):
    def test_dataset_definition_to_payload(self):
        dataset_definition = DatasetDefinition(
            identifier="profile",
            catalog_id="5ec4aec1f072bc028e3471ae",
            catalog_version_id="5ec4aec2f072bc028e3471b1",
        )

        dd_payload = dataset_definition.to_payload()
        assert dd_payload["identifier"] == "profile"
        assert dd_payload["catalogId"] == "5ec4aec1f072bc028e3471ae"
        assert dd_payload["catalogVersionId"] == "5ec4aec2f072bc028e3471b1"

        dataset_definition = DatasetDefinition(
            identifier="transaction",
            catalog_id="5ec4aec1f072bc028e3471ae",
            catalog_version_id="5ec4aec2f072bc028e3471b1",
            feature_list_id="5ec4aec2f072bc028e3471b5",
            primary_temporal_key="Date",
        )
        dd_payload = dataset_definition.to_payload()
        assert dd_payload["identifier"] == "transaction"
        assert dd_payload["catalogId"] == "5ec4aec1f072bc028e3471ae"
        assert dd_payload["catalogVersionId"] == "5ec4aec2f072bc028e3471b1"
        assert dd_payload["featureListId"] == "5ec4aec2f072bc028e3471b5"
        assert dd_payload["primaryTemporalKey"] == "Date"

    def test_dataset_definition_to_dict(self):
        dataset_definition = DatasetDefinition(
            identifier="profile",
            catalog_id="5ec4aec1f072bc028e3471ae",
            catalog_version_id="5ec4aec2f072bc028e3471b1",
        )

        dd_dict = dataset_definition.to_dict()
        assert dd_dict["identifier"] == "profile"
        assert dd_dict["catalog_id"] == "5ec4aec1f072bc028e3471ae"
        assert dd_dict["catalog_version_id"] == "5ec4aec2f072bc028e3471b1"
        assert dd_dict["snapshot_policy"] == "latest"
        assert dd_dict["feature_list_id"] is None
        assert dd_dict["primary_temporal_key"] is None

        dataset_definition = DatasetDefinition(
            identifier="transaction",
            catalog_id="5ec4aec1f072bc028e3471ae",
            catalog_version_id="5ec4aec2f072bc028e3471b1",
            feature_list_id="5ec4aec2f072bc028e3471b5",
            primary_temporal_key="Date",
        )
        dd_dict = dataset_definition.to_dict()
        assert dd_dict["identifier"] == "transaction"
        assert dd_dict["catalog_id"] == "5ec4aec1f072bc028e3471ae"
        assert dd_dict["catalog_version_id"] == "5ec4aec2f072bc028e3471b1"
        assert dd_dict["snapshot_policy"] == "latest"
        assert dd_dict["feature_list_id"] == "5ec4aec2f072bc028e3471b5"
        assert dd_dict["primary_temporal_key"] == "Date"

    def test_relationship_to_payload(self):
        relationship = Relationship(
            dataset1_identifier="profile",
            dataset2_identifier="transaction",
            dataset1_keys=["CustomerID"],
            dataset2_keys=["CustomerID"],
        )
        rel_payload = relationship.to_payload()
        assert rel_payload["dataset1Identifier"] == "profile"
        assert rel_payload["dataset2Identifier"] == "transaction"
        assert rel_payload["dataset1Keys"] == ["CustomerID"]
        assert rel_payload["dataset2Keys"] == ["CustomerID"]
        assert "featureDerivationWindowStart" not in rel_payload
        assert "featureDerivationWindowEnd" not in rel_payload
        assert "featureDerivationWindowTimeUnit" not in rel_payload
        assert "predictionPointRounding" not in rel_payload
        assert "predictionPointRoundingTimeUnit" not in rel_payload

        relationship = Relationship(
            dataset2_identifier="profile",
            dataset1_keys=["CustomerID"],
            dataset2_keys=["CustomerID"],
            feature_derivation_window_start=-14,
            feature_derivation_window_end=0,
            feature_derivation_window_time_unit="DAY",
            prediction_point_rounding=0,
            prediction_point_rounding_time_unit="DAY",
        )
        rel_payload = relationship.to_payload()
        assert rel_payload["dataset2Identifier"] == "profile"
        assert rel_payload["dataset1Keys"] == ["CustomerID"]
        assert rel_payload["dataset2Keys"] == ["CustomerID"]
        assert "dataset1Identifier" not in rel_payload
        assert rel_payload["featureDerivationWindowStart"] == -14
        assert rel_payload["featureDerivationWindowEnd"] == 0
        assert rel_payload["featureDerivationWindowTimeUnit"] == "DAY"
        assert rel_payload["predictionPointRounding"] == 0
        assert rel_payload["predictionPointRoundingTimeUnit"] == "DAY"

    def test_relationship_to_dict(self):
        relationship = Relationship(
            dataset1_identifier="profile",
            dataset2_identifier="transaction",
            dataset1_keys=["CustomerID"],
            dataset2_keys=["CustomerID"],
        )
        rel_dict = relationship.to_dict()
        assert rel_dict["dataset1_identifier"] == "profile"
        assert rel_dict["dataset2_identifier"] == "transaction"
        assert rel_dict["dataset1_keys"] == ["CustomerID"]
        assert rel_dict["dataset2_keys"] == ["CustomerID"]
        assert rel_dict["feature_derivation_window_start"] is None
        assert rel_dict["feature_derivation_window_end"] is None
        assert rel_dict["feature_derivation_window_time_unit"] is None
        assert rel_dict["prediction_point_rounding"] is None
        assert rel_dict["prediction_point_rounding_time_unit"] is None

        relationship = Relationship(
            dataset2_identifier="profile",
            dataset1_keys=["CustomerID"],
            dataset2_keys=["CustomerID"],
            feature_derivation_window_start=-14,
            feature_derivation_window_end=0,
            feature_derivation_window_time_unit="DAY",
            prediction_point_rounding=0,
            prediction_point_rounding_time_unit="DAY",
        )
        rel_dict = relationship.to_dict()
        assert rel_dict["dataset2_identifier"] == "profile"
        assert rel_dict["dataset1_keys"] == ["CustomerID"]
        assert rel_dict["dataset2_keys"] == ["CustomerID"]
        assert rel_dict["dataset1_identifier"] is None
        assert rel_dict["feature_derivation_window_start"] == -14
        assert rel_dict["feature_derivation_window_end"] == 0
        assert rel_dict["feature_derivation_window_time_unit"] == "DAY"
        assert rel_dict["prediction_point_rounding"] == 0
        assert rel_dict["prediction_point_rounding_time_unit"] == "DAY"

    def test_secondary_dataset_to_payload(self):
        secondary_dataset = SecondaryDataset(
            identifier="profile",
            catalog_id="5ec4aec1f072bc028e3471ae",
            catalog_version_id="5ec4aec2f072bc028e3471b1",
        )

        sec_dataset_payload = secondary_dataset.to_payload()
        assert sec_dataset_payload["identifier"] == "profile"
        assert sec_dataset_payload["catalogId"] == "5ec4aec1f072bc028e3471ae"
        assert sec_dataset_payload["catalogVersionId"] == "5ec4aec2f072bc028e3471b1"
        assert sec_dataset_payload["snapshotPolicy"] == "latest"

    def test_secondary_dataset_to_dict(self):
        secondary_dataset = SecondaryDataset(
            identifier="profile",
            catalog_id="5ec4aec1f072bc028e3471ae",
            catalog_version_id="5ec4aec2f072bc028e3471b1",
        )

        sec_dataset_dict = secondary_dataset.to_dict()
        assert sec_dataset_dict["identifier"] == "profile"
        assert sec_dataset_dict["catalog_id"] == "5ec4aec1f072bc028e3471ae"
        assert sec_dataset_dict["catalog_version_id"] == "5ec4aec2f072bc028e3471b1"
        assert sec_dataset_dict["snapshot_policy"] == "latest"
