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
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2, parse_time

from ..enums import AllowedTimeUnitsSAFER, FeatureDiscoveryMode
from ..helpers.feature_discovery import DatasetDefinition, FeatureDiscoverySetting, Relationship


class RelationshipsConfiguration(APIObject):
    """ A Relationships configuration specifies a set of secondary datasets as well as
    the relationships among them. It is used to configure Feature Discovery for a project
    to generate features automatically from these datasets.

    Attributes
    ----------
    id : string
        Id of the created relationships configuration
    dataset_definitions: list
        Each element is a dataset_definitions for a dataset.
    relationships: list
        Each element is a relationship between two datasets
    feature_discovery_mode: str
        Mode of feature discovery. Supported values are 'default' and 'manual'
    feature_discovery_settings: list
        List of feature discovery settings used to customize the feature discovery process

    The `dataset_definitions` structure is

    identifier: string
        Alias of the dataset (used directly as part of the generated feature names)
    catalog_id: str, or None
        Identifier of the catalog item
    catalog_version_id: str
        Identifier of the catalog item version
    primary_temporal_key: string, optional
        Name of the column indicating time of record creation
    feature_list_id: string, optional
        Identifier of the feature list. This decides which columns in the dataset are
        used for feature generation
    snapshot_policy: str
        Policy to use  when creating a project or making predictions.
        Must be one of the following values:
        'specified': Use specific snapshot specified by catalogVersionId
        'latest': Use latest snapshot from the same catalog item
        'dynamic': Get data from the source (only applicable for JDBC datasets)
    feature_lists: list
        List of feature list info
    data_source: dict
        Data source info if the dataset is from data source
    data_sources: list
        List of Data source details for a JDBC datasets
    is_deleted: bool, optional
        Whether the dataset is deleted or not

    The `data source info` structured is

    data_store_id: str
        Id of the data store.
    data_store_name : str
         User-friendly name of the data store.
    url : str
        Url used to connect to the data store.
    dbtable : str
        Name of table from the data store.
    schema: str
        Schema definition of the table from the data store
    catalog: str
        Catalog name of the data source.

    The `feature list info` structure is

    id : str
        Id of the featurelist
    name : str
        Name of the featurelist
    features : list of str
        Names of all the Features in the featurelist
    dataset_id : str
        Project the featurelist belongs to
    creation_date : datetime.datetime
        When the featurelist was created
    user_created : bool
        Whether the featurelist was created by a user or by DataRobot automation
    created_by: str
        Name of user who created it
    description : str
        Description of the featurelist.  Can be updated by the user
        and may be supplied by default for DataRobot-created featurelists.
    dataset_id: str
        Dataset which is associated with the feature list
    dataset_version_id: str or None
        Version of the dataset which is associated with feature list.
        Only relevant for Informative features

    The `relationships` schema is

    dataset1_identifier: str or None
        Identifier of the first dataset in this relationship.
        This is specified in the indentifier field of dataset_definition structure.
        If None, then the relationship is with the primary dataset.
    dataset2_identifier: str
        Identifier of the second dataset in this relationship.
        This is specified in the identifier field of dataset_definition schema.
    dataset1_keys: list of str (max length: 10 min length: 1)
        Column(s) from the first dataset which are used to join to the second dataset
    dataset2_keys: list of str (max length: 10 min length: 1)
        Column(s) from the second dataset that are used to join to the first dataset
    time_unit: str, or None
        Time unit of the feature derivation window. Supported
        values are MILLISECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR.
        If present, the feature engineering Graph will perform time-aware joins.
    feature_derivation_window_start: int, or None
        How many time_units of each dataset's primary temporal key into the past relative
        to the datetimePartitionColumn the feature derivation window should begin.
        Will be a negative integer,
        If present, the feature engineering Graph will perform time-aware joins.
    feature_derivation_window_end: int, or None
        How many timeUnits of each dataset's record
        primary temporal key into the past relative to the datetimePartitionColumn the
        feature derivation window should end.  Will be a non-positive integer, if present.
        If present, the feature engineering Graph will perform time-aware joins.
    feature_derivation_window_time_unit: int or None
        Time unit of the feature derivation window. Supported values are
        MILLISECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR
        If present, time-aware joins will be used.
        Only applicable when dataset1Identifier is not provided.
    feature_derivation_windows: list of dict, or None
        List of feature derivation windows settings. If present, time-aware joins will be used.
        Only allowed when feature_derivation_window_start,
        feature_derivation_window_end and feature_derivation_window_time_unit are not provided.
    prediction_point_rounding: int, or None
        Closest value of prediction_point_rounding_time_unit to round the prediction point
        into the past when applying the feature derivation window. Will be a positive integer,
        if present.Only applicable when dataset1_identifier is not provided.
    prediction_point_rounding_time_unit: str, or None
        time unit of the prediction point rounding. Supported values are
        MILLISECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR
        Only applicable when dataset1_identifier is not provided.

    The `feature_derivation_windows` is a list of dictionary with schema:
        start: int
            How many time_units of each dataset's primary temporal key into the past relative
            to the datetimePartitionColumn the feature derivation window should begin.
        end: int
            How many timeUnits of each dataset's record
            primary temporal key into the past relative to the datetimePartitionColumn the
            feature derivation window should end.
        unit: string
            Time unit of the feature derivation window.
            One of ``datarobot.enums.AllowedTimeUnitsSAFER``.

    The `feature_discovery_settings` structure is:

    name: str
        Name of the feature discovery setting
    value: bool
        Value of the feature discovery setting

    To see the list of possible settings, create a RelationshipConfiguration without specifying
    settings and check its `feature_discovery_settings` attribute, which is a list of possible
    settings with their default values.
    """

    _path = "relationshipsConfigurations/"
    data_source_trafaret = t.Dict(
        {
            t.Key("data_store_name"): String,
            t.Key("data_store_id"): String,
            t.Key("url"): String,
            t.Key("dbtable"): String | t.Null,
            t.Key("schema", optional=True): String(allow_blank=True) | t.Null,
            t.Key("catalog", optional=True): String(allow_blank=True) | t.Null,
            t.Key("data_source_id", optional=True): String | t.Null,
        }
    ).ignore_extra("*")
    feature_list_info = t.Dict(
        {
            t.Key("id"): String,
            t.Key("features"): t.List(String),
            t.Key("name"): String,
            t.Key("description"): String,
            t.Key("dataset_id"): String,
            t.Key("user_created"): t.Bool,
            t.Key("creation_date"): parse_time,
            t.Key("created_by"): String,
            t.Key("dataset_version_id", optional=True): String,
        }
    ).ignore_extra("*")
    dataset_definitions_trafaret = t.Dict(
        {
            t.Key("identifier"): String(min_length=3, max_length=20),
            t.Key("catalog_version_id"): String,
            t.Key("catalog_id"): String,
            t.Key("primary_temporal_key", optional=True): String | t.Null,
            t.Key("feature_list_id", optional=True): String | t.Null,
            t.Key("snapshot_policy", optional=True, default="latest"): t.Enum(
                "latest", "specified", "dynamic"
            ),
            t.Key("feature_lists", optional=True): t.List(feature_list_info),
            t.Key("data_source", optional=True): data_source_trafaret | t.Null,
            t.Key("data_sources", optional=True): t.List(data_source_trafaret) | t.Null,
            t.Key("is_deleted", optional=True): t.Bool | t.Null,
        }
    ).ignore_extra("*")
    feature_derivation_window_trafaret = t.Dict(
        {
            t.Key("start"): Int(lt=0),
            t.Key("end"): Int(lte=0),
            t.Key("unit"): t.Enum(*AllowedTimeUnitsSAFER.ALL),
        }
    )

    relationships_trafaret = t.Dict(
        {
            t.Key("dataset1_identifier", optional=True): String | t.Null,
            t.Key("dataset2_identifier"): String,
            t.Key("dataset1_keys"): t.List(String, min_length=1, max_length=10),
            t.Key("dataset2_keys"): t.List(String, min_length=1, max_length=10),
            t.Key("feature_derivation_window_start", optional=True): Int(lt=0),
            t.Key("feature_derivation_window_end", optional=True): Int(lte=0),
            t.Key("feature_derivation_window_time_unit", optional=True): t.Enum(
                *AllowedTimeUnitsSAFER.ALL
            ),
            t.Key("feature_derivation_windows", optional=True): t.List(
                feature_derivation_window_trafaret
            ),
            t.Key("prediction_point_rounding", optional=True): Int(gt=0, lte=30),
            t.Key("prediction_point_rounding_time_unit", optional=True): t.Enum(
                *AllowedTimeUnitsSAFER.ALL
            ),
        }
    ).ignore_extra("*")

    feature_discovery_setting_trafaret = t.Dict(
        {t.Key("name"): String, t.Key("value"): t.Bool}
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("dataset_definitions"): t.List(dataset_definitions_trafaret, min_length=1),
            t.Key("relationships"): t.List(relationships_trafaret, min_length=1),
            t.Key("feature_discovery_mode", optional=True): t.Enum(*FeatureDiscoveryMode.ALL),
            t.Key("feature_discovery_settings", optional=True): t.List(
                feature_discovery_setting_trafaret
            ),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id,
        dataset_definitions=None,
        relationships=None,
        feature_discovery_mode=None,
        feature_discovery_settings=None,
    ):
        self.id = id
        self.dataset_definitions = dataset_definitions
        self.relationships = relationships
        self.feature_discovery_mode = feature_discovery_mode
        self.feature_discovery_settings = feature_discovery_settings

    def __repr__(self):
        return encode_utf8_if_py2(u"{}()".format(self.__class__.__name__))

    @classmethod
    def create(cls, dataset_definitions, relationships, feature_discovery_settings=None):
        """ Create a Relationships Configuration

        Parameters
        ----------
        dataset_definitions: list of dataset definitions
            Each element is a ``datarobot.helpers.feature_discovery.DatasetDefinition``
        relationships: list of relationships
            Each element is a ``datarobot.helpers.feature_discovery.Relationship``
        feature_discovery_settings : list of feature discovery settings, optional
            Each element is a dictionary or a
            ``datarobot.helpers.feature_discovery.FeatureDiscoverySetting``. If not provided,
            default settings will be used.

        Returns
        -------
        relationships_configuration: RelationshipsConfiguration
            Created relationships configuration

        Examples
        --------
        .. code-block:: python

            dataset_definition = dr.DatasetDefinition(
                identifier='profile',
                catalog_id='5fd06b4af24c641b68e4d88f',
                catalog_version_id='5fd06b4af24c641b68e4d88f'
            )
            relationship = dr.Relationship(
                dataset2_identifier='profile',
                dataset1_keys=['CustomerID'],
                dataset2_keys=['CustomerID'],
                feature_derivation_window_start=-14,
                feature_derivation_window_end=-1,
                feature_derivation_window_time_unit='DAY',
                prediction_point_rounding=1,
                prediction_point_rounding_time_unit='DAY'
            )
            dataset_definitions = [dataset_definition]
            relationships = [relationship]
            relationship_config = dr.RelationshipsConfiguration.create(
                dataset_definitions=dataset_definitions,
                relationships=relationships
            )
            >>> relationship_config.id
            '5c88a37770fc42a2fcc62759'
        """
        payload_dataset_definition = []
        for dd in dataset_definitions:
            if isinstance(dd, DatasetDefinition):
                payload_dataset_definition.append(dd.to_payload())
            else:
                payload_dataset_definition.append(dd)

        payload_relationships = []
        for rel in relationships:
            if isinstance(rel, Relationship):
                payload_relationships.append(rel.to_payload())
            else:
                payload_relationships.append(rel)

        payload_data = {
            "datasetDefinitions": payload_dataset_definition,
            "relationships": payload_relationships,
        }

        if feature_discovery_settings is not None:
            settings = []
            for item in feature_discovery_settings:
                if isinstance(item, FeatureDiscoverySetting):
                    settings.append(item.to_dict())
                else:
                    settings.append(item)
            payload_data["feature_discovery_settings"] = settings

        response = cls._client.post(cls._path, data=payload_data).json()
        return RelationshipsConfiguration.from_server_data(response)

    def get(self):
        """ Retrieve the Relationships configuration for a given id

        Returns
        -------
        relationships_configuration: RelationshipsConfiguration
            The requested relationships configuration

        Raises
        ------
        ClientError
            Raised if an invalid relationships config id is provided.

        Examples
        --------
        .. code-block:: python

            relationships_config = dr.RelationshipsConfiguration(valid_config_id)
            result = relationships_config.get()
            >>> result.id
            '5c88a37770fc42a2fcc62759'
        """
        return self.from_location("{}{}/".format(self._path, self.id))

    def replace(self, dataset_definitions, relationships, feature_discovery_settings=None):
        """ Update the Relationships Configuration which is not used in
        the feature discovery Project

        Parameters
        ----------
        dataset_definitions: list of dataset definition
            Each element is a ``datarobot.helpers.feature_discovery.DatasetDefinition``
        relationships: list of relationships
            Each element is a ``datarobot.helpers.feature_discovery.Relationship``
        feature_discovery_settings : list of feature discovery settings, optional
            Each element is a dictionary or a
            ``datarobot.helpers.feature_discovery.FeatureDiscoverySetting``. If not provided,
            default settings will be used.

        Returns
        -------
        relationships_configuration: RelationshipsConfiguration
            the updated relationships configuration
        """
        payload_dataset_definition = []
        for dd in dataset_definitions:
            if isinstance(dd, DatasetDefinition):
                payload_dataset_definition.append(dd.to_payload())
            else:
                payload_dataset_definition.append(dd)

        payload_relationships = []
        for rel in relationships:
            if isinstance(rel, Relationship):
                payload_relationships.append(rel.to_payload())
            else:
                payload_relationships.append(rel)

        payload_data = {
            "datasetDefinitions": payload_dataset_definition,
            "relationships": payload_relationships,
        }

        if feature_discovery_settings is not None:
            settings = []
            for item in feature_discovery_settings:
                if isinstance(item, FeatureDiscoverySetting):
                    settings.append(item.to_dict())
                else:
                    settings.append(item)
            payload_data["feature_discovery_settings"] = settings

        url = "{}{}/".format(self._path, self.id)
        response = self._client.put(url, json=payload_data).json()
        return RelationshipsConfiguration.from_server_data(response)

    def delete(self):
        """
        Delete the Relationships configuration

        Raises
        ------
        ClientError
            Raised if an invalid relationships config id is provided.

        Examples
        --------
        .. code-block:: python

            # Deleting with a valid id
            relationships_config = dr.RelationshipsConfiguration(valid_config_id)
            status_code = relationships_config.delete()
            status_code
            >>> 204
            relationships_config.get()
            >>> ClientError: Relationships Configuration not found
        """
        self._client.delete("{}{}/".format(self._path, self.id))
