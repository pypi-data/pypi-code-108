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
import responses

from datarobot import RelationshipsConfiguration
from datarobot.helpers.feature_discovery import FeatureDiscoverySetting


@responses.activate
def test_relationships_config_creation(
    relationships_configuration,
    create_dataset_definitions,
    create_relationships,
    create_feature_discovery_settings,
):
    responses.add(
        responses.POST,
        "https://host_name.com/relationshipsConfigurations/",
        json=relationships_configuration,
    )

    settings = [
        FeatureDiscoverySetting(s["name"], s["value"]) for s in create_feature_discovery_settings
    ]
    relationships_configuration = RelationshipsConfiguration.create(
        dataset_definitions=create_dataset_definitions,
        relationships=create_relationships,
        feature_discovery_settings=settings,
    )
    assert responses.calls[0].request.method == "POST"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 2
    assert len(relationships_configuration.relationships) == 2
    assert len(relationships_configuration.feature_discovery_settings) == 2
    assert relationships_configuration.feature_discovery_mode == "manual"


@responses.activate
def test_relationships_config_retrieve(
    relationships_configuration, create_dataset_definitions, create_relationships
):
    id = relationships_configuration["id"]
    responses.add(
        responses.GET,
        "https://host_name.com/relationshipsConfigurations/{}/".format(id),
        json=relationships_configuration,
    )

    result = RelationshipsConfiguration(id=id).get()

    assert responses.calls[0].request.method == "GET"
    assert result.id == id
    assert len(result.dataset_definitions) == 2
    assert len(result.relationships) == 2
    for actual, expected in zip(result.dataset_definitions, create_dataset_definitions):
        assert actual["identifier"] == expected["identifier"]
        assert actual["catalog_version_id"] == expected["catalogVersionId"]
        assert actual["catalog_id"] == expected["catalogId"]
        assert actual["snapshot_policy"] == expected["snapshotPolicy"]

    actual = result.relationships[1]
    expected = create_relationships[1]
    assert actual["dataset1_identifier"] == expected["dataset1Identifier"]
    assert actual["dataset2_identifier"] == expected["dataset2Identifier"]
    assert actual["dataset1_keys"] == expected["dataset1Keys"]
    assert actual["dataset2_keys"] == expected["dataset2Keys"]
    assert actual["feature_derivation_window_end"] == expected["featureDerivationWindowEnd"]
    assert actual["feature_derivation_window_start"] == expected["featureDerivationWindowStart"]
    assert (
        actual["feature_derivation_window_time_unit"] == expected["featureDerivationWindowTimeUnit"]
    )
    assert actual["prediction_point_rounding"] == expected["predictionPointRounding"]
    assert (
        actual["prediction_point_rounding_time_unit"] == expected["predictionPointRoundingTimeUnit"]
    )


@responses.activate
def test_relationships_config_replace(
    relationships_configuration,
    create_dataset_definitions,
    create_relationships,
    create_feature_discovery_settings,
):
    responses.add(
        responses.PUT,
        "https://host_name.com/relationshipsConfigurations/R-ID/",
        json=relationships_configuration,
    )

    relationships_configuration = RelationshipsConfiguration("R-ID").replace(
        dataset_definitions=create_dataset_definitions,
        relationships=create_relationships,
        feature_discovery_settings=create_feature_discovery_settings,
    )
    assert responses.calls[0].request.method == "PUT"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 2
    assert len(relationships_configuration.relationships) == 2
    assert len(relationships_configuration.feature_discovery_settings) == 2
    assert relationships_configuration.feature_discovery_mode == "manual"


@responses.activate
def test_relationships_config_delete(relationships_configuration):
    id = relationships_configuration["id"]
    url = "https://host_name.com/relationshipsConfigurations/{}/".format(id)
    responses.add(responses.DELETE, url)

    relationships_config = RelationshipsConfiguration(id=id)
    relationships_config.delete()

    assert responses.calls[0].request.method == responses.DELETE
    assert responses.calls[0].request.url == url


@responses.activate
def test_jdbc_relationships_config_creation(
    jdbc_relationships_configuration, create_jdbc_dataset_definitions, create_relationships
):
    responses.add(
        responses.POST,
        "https://host_name.com/relationshipsConfigurations/",
        json=jdbc_relationships_configuration,
    )

    relationships_configuration = RelationshipsConfiguration.create(
        dataset_definitions=create_jdbc_dataset_definitions, relationships=create_relationships,
    )
    assert responses.calls[0].request.method == "POST"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 1
    assert len(relationships_configuration.relationships) == 2
    definition = relationships_configuration.dataset_definitions[0]
    assert definition["data_source"]["data_store_name"] == "mssql-remote-dev"
    assert definition["data_source"]["data_store_id"] == "60c6e3f833de57c65440f571"
    assert definition["data_source"]["data_source_id"] == "60c6e3f833de57c65440f581"
    assert definition["data_source"]["dbtable"] == "safer_credit"
    assert definition["data_source"]["schema"] == ""
    assert definition["data_source"]["catalog"] == "safer"


@responses.activate
def test_relationships_config_with_multiple_fdws_creation(
    relationships_configuration_multiple_fdws,
    create_dataset_definitions,
    create_relationships_multiple_fdws,
    create_feature_discovery_settings,
):
    responses.add(
        responses.POST,
        "https://host_name.com/relationshipsConfigurations/",
        json=relationships_configuration_multiple_fdws,
    )

    settings = [
        FeatureDiscoverySetting(s["name"], s["value"]) for s in create_feature_discovery_settings
    ]
    relationships_configuration = RelationshipsConfiguration.create(
        dataset_definitions=create_dataset_definitions,
        relationships=create_relationships_multiple_fdws,
        feature_discovery_settings=settings,
    )
    assert responses.calls[0].request.method == "POST"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 2
    assert len(relationships_configuration.relationships) == 2
    assert relationships_configuration.relationships[1]["feature_derivation_windows"] == [
        {"end": -1, "start": -10, "unit": u"SECOND"},
        {"end": -10, "start": -20, "unit": u"SECOND"},
    ]
    assert len(relationships_configuration.feature_discovery_settings) == 2
    assert relationships_configuration.feature_discovery_mode == "manual"


@responses.activate
def test_relationships_config_multiple_fdws_retrieve(
    relationships_configuration_multiple_fdws,
    create_dataset_definitions,
    create_relationships_multiple_fdws,
):
    id = relationships_configuration_multiple_fdws["id"]
    responses.add(
        responses.GET,
        "https://host_name.com/relationshipsConfigurations/{}/".format(id),
        json=relationships_configuration_multiple_fdws,
    )

    result = RelationshipsConfiguration(id=id).get()

    assert responses.calls[0].request.method == "GET"
    assert result.id == id
    assert len(result.dataset_definitions) == 2
    assert len(result.relationships) == 2
    for actual, expected in zip(result.dataset_definitions, create_dataset_definitions):
        assert actual["identifier"] == expected["identifier"]
        assert actual["catalog_version_id"] == expected["catalogVersionId"]
        assert actual["catalog_id"] == expected["catalogId"]
        assert actual["snapshot_policy"] == expected["snapshotPolicy"]

    actual = result.relationships[1]
    expected = create_relationships_multiple_fdws[1]
    assert actual["dataset1_identifier"] == expected["dataset1Identifier"]
    assert actual["dataset2_identifier"] == expected["dataset2Identifier"]
    assert actual["dataset1_keys"] == expected["dataset1Keys"]
    assert actual["dataset2_keys"] == expected["dataset2Keys"]
    assert actual["feature_derivation_windows"] == expected["featureDerivationWindows"]
