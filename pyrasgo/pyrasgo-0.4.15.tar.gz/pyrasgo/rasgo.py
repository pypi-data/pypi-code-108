import logging
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import webbrowser

from pyrasgo import config

from pyrasgo.api import (
    Admin, Create, Delete, Get, Match, Publish, Read, Save, Update,
)
from pyrasgo.primitives import Collection, DataSource, Feature, FeatureList

from pyrasgo import schemas as api
from pyrasgo.schemas.enums import Granularity, ModelType

from pyrasgo.storage  import Evaluate, Prune, Transform
from pyrasgo.storage.dataframe.utils import generate_unique_id

from pyrasgo.utils import ingestion
from pyrasgo.utils.versioning import deprecated_with_replacement, deprecated_without_replacement


class Rasgo():
    """
    Base connection object to handle interactions with the Rasgo API.
    """
    def __init__(self):
        self._experiment_id = None
        self.get = Get()
        self.match = Match()
        self.create = Create()
        self.update = Update()
        self.publish = Publish()
        self.read = Read()
        self.delete = Delete()
        self.save = Save()
        self.transform = Transform()
        self.evaluate = Evaluate()
        self.prune = Prune()
        self.admin = Admin()

    def open_docs(self):
        webbrowser.open("https://docs.rasgoml.com/rasgo-docs/pyrasgo/pyrasgo-getting-started")

    def pronounce_rasgo(self):
        webbrowser.open("https://www.spanishdict.com/pronunciation/rasgo?langFrom=es")

    def _pyrasgo_version(self):
        from pyrasgo.version import __version__
        return __version__

    def _pyrasgo_api_key(self):
        from pyrasgo.config import get_session_api_key
        return get_session_api_key()

    def activate_experiment(
        self,
        experiment_name: str
    ):
        """
        Activate an experiment with a unique name and id. Experiments are used to
        track dataframe activity across Rasgo methods

        Note: Experiment names must be unique
              Using an existing name will re-activate an old experiment
        """
        df = self.match.dataframe(name=experiment_name)
        adjective = 'existing'
        if not df:
            uid = generate_unique_id()
            df = self.save.dataframe(name=experiment_name, unique_id=uid)
            adjective = 'new'
        self._experiment_id = df.uniqueId
        self.evaluate = Evaluate(experiment_id=self._experiment_id)
        self.prune = Prune(experiment_id=self._experiment_id)
        print(f"Activated {adjective} experiment with name {experiment_name} for dataframe: {df.uniqueId}")

    def end_experiment(self):
        """
        If an experiment is active, deactivate it and stop tracking dataframe activity
        """
        self._experiment_id = None
        self.evaluate = Evaluate()
        self.prune = Prune()
        print(f"Experiment ended")

    def is_experiment_active(self):
        """
        Check if an experiment is active
        """
        print(f"Experiment active for dataframe: {self._experiment_id}" if self._experiment_id else "No experiment active")

# ---------
# Get Calls
# ---------
    @deprecated_with_replacement('v0.3', 'get.collection')
    def get_collection(self, collection_id: int) -> Collection:
        """
        Returns a Rasgo Collection (set of joined Features) matching the specified id
        """
        return self.get.collection(collection_id)

    @deprecated_with_replacement('v0.3', 'get.collection_attributes')
    def get_collection_attributes(self, collection_id: int) -> api.CollectionAttributes:
        """
        Returns a dict of attributes for a collection
        """
        return self.get.collection_attributes(collection_id)

    @deprecated_with_replacement('v0.3', 'get.collections')
    def get_collections(self, include_shared: bool=False) -> List[Collection]:
        """
        Returns all Rasgo Collections (set of joined Features) that I have author access to. Add an include_shared
        parameter to return all Rasgo Collections that I have any access to (author or shared access)
        :param include_shared: Boolean value indicating if the return should include all accessible collections
        """
        return self.get.collections(include_shared=include_shared)

    @deprecated_with_replacement('v0.3', 'get.collections_by_attribute')
    def get_collections_by_attribute(self, key: str, value: str = None) -> List[Collection]:
        """
        Returns a list of Rasgo Collections that match an attribute
        """
        return self.get.collections_by_attribute(key, value)

    @deprecated_with_replacement('v0.3', 'get.data_sources')
    def get_data_sources(self) -> List[DataSource]:
        """
        Returns all DataSources available in your organization or Rasgo Community
        """
        return self.get.data_sources()

    @deprecated_with_replacement('v0.3', 'get.data_source')
    def get_data_source(self, data_source_id: int) -> DataSource:
        """
        Returns the DataSource with the specified id
        """
        return self.get.data_source(data_source_id)

    @deprecated_with_replacement('v0.3', 'get.data_source_stats')
    def get_data_source_stats(self, data_source_id: int):
        """
        Returns the stats profile of the specificed data source
        """
        return self.get.data_source_stats(data_source_id)

    @deprecated_with_replacement('v0.3', 'get.feature')
    def get_feature(self, feature_id: int) -> Feature:
        """
        Returns the Feature with the specified id
        """
        return self.get.feature(feature_id)

    @deprecated_with_replacement('v0.3', 'get.feature_attributes')
    def get_feature_attributes(self, feature_id: int) -> api.FeatureAttributes:
        """
        Returns a dict of attributes for a feature
        """
        return self.get.feature_attributes(feature_id)

    @deprecated_with_replacement('v0.3', 'get.feature_attributes_log')
    def get_feature_attributes_log(self, feature_id: int) -> tuple:
        """
        Returns a list of all attributes values logged to a feature over time
        """
        return self.get.feature_attributes_log(feature_id)

    @deprecated_with_replacement('v0.3', 'get.feature_stats')
    def get_feature_stats(self, feature_id: int) -> Optional[api.FeatureStats]:
        """
        Returns the stats profile for the specified Feature
        """
        return self.get.feature_stats(feature_id)

    @deprecated_with_replacement('v0.3', 'get.features')
    def get_features(self) -> FeatureList:
        """
        Returns a list of Features available in your organization or Rasgo Community
        """
        return self.get.features()

    @deprecated_with_replacement('v0.3', 'get.features_by_attribute')
    def get_features_by_attribute(self, key: str, value: str = None) -> List[Feature]:
        """
        Returns a list of features that match an attribute
        """
        return self.get.features_by_attribute(key, value)

    @deprecated_with_replacement('v0.3', 'get.shared_collections')
    def get_shared_collections(self) -> List[Collection]:
        """
        Returns all Rasgo Collections (set of joined Features) shared in my organization or in Rasgo community
        """
        return self.get.shared_collections()

    @deprecated_with_replacement('v0.3', 'get.source_columns')
    def get_source_columns(self, table: Optional[str] = None, database: Optional[str] = None, schema: Optional[str] = None, data_type: Optional[str] = None) -> pd.DataFrame:
        """
        Returns a DataFrame of columns in Snowflake tables and views that are queryable as feature sources
        """
        return self.get.source_columns(table, database, schema, data_type)

    @deprecated_with_replacement('v0.3', 'get.source_tables')
    def get_source_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> pd.DataFrame:
        """
        Return a DataFrame of Snowflake tables and views that are queryable as feature sources
        """
        return self.get.source_tables(database, schema)


# -------------------
# Post / Create Calls
# -------------------
    @deprecated_without_replacement('v0.3')
    def create_collection(self, name: str,
                          type: Union[str, ModelType],
                          granularity: Union[str, Granularity],
                          description: Optional[str] = None,
                          is_shared: Optional[bool] = False) -> Collection:
        return self.create.collection(name, type, granularity, description, is_shared)

    @deprecated_without_replacement('v0.3')
    def put_collection_attributes(self, collection_id: int, attributes: List[dict]):
        """
        Create or update attributes on a Rasgo Collection

        param attributes: dict [{"key": "value"}, {"key": "value"}]
        """
        return self.update.collection_attributes(collection_id, attributes)

    @deprecated_without_replacement('v0.3')
    def put_feature_attributes(self, feature_id: int, attributes: List[dict]):
        """
        Create or update attributes on a feature

        param attributes: dict [{"key": "value"}, {"key": "value"}]
        """
        return self.update.feature_attributes(feature_id, attributes)


# ------------------
# Workflow Functions
# ------------------
    @deprecated_with_replacement('v0.3', 'data_source.to_dict()')
    def prepare_features_dict(self, data_source_id: int = None):
        """
        Returns a dict of metadata values for the specificed Rasgo Features

        params
        ------
        data_source_id: int: ID of a Rasgo DataSource

        Alternate Usage
        ---------------
        Pass in no params to return a blank dict template
        """
        if data_source_id:
            ds = self.get.data_source(data_source_id)
            return ingestion.save_features_to_dict(ds)
        return ingestion.RASGO_DICT

    @deprecated_with_replacement('v0.3', 'data_source.to_yml()')
    def prepare_features_yml(self, data_souce_id: int, file_name: str, directory: str = None):
        """
        Saves a yml file of metadata values for the specificed Rasgo Features to a directory location

        params
        ------
        data_source_id: int: ID of a Rasgo DataSource
        file_name: str: name for the output file
        directory: str: full dir location for the output file (minus file_name)
        """
        fs = self.get.features_yml(data_souce_id)
        return ingestion.save_features_to_yaml(fs, file_name=file_name, directory=directory)

    @deprecated_with_replacement('v0.3', 'publish.features')
    def publish_features(self, features_dict: dict) -> DataSource:
        return self.publish.features(features_dict)

    @deprecated_without_replacement('v0.3')
    def publish_features_from_df(self,
                                 df: pd.DataFrame,
                                 dimensions: List[str],
                                 features: List[str],
                                 granularity: List[str] = None,
                                 tags: List[str] = None,
                                 sandbox: bool = True):
        granularity = granularity if granularity else []
        tags = tags if tags else []
        raise NotImplementedError("`publish_features_from_df()` is a deprecated method. "
                                  "Please use `publish.features()` or `publish.features_from_source()` instead")

    @deprecated_with_replacement('v0.3', 'publish.features_from_source')
    def publish_features_from_source(self,
                                     data_source_id: int,
                                     features: List[str],
                                     dimensions: List[str],
                                     granularity: List[str] = None,
                                     tags: List[str] = None,
                                     feature_set_name: str = None,
                                     sandbox: bool = True,
                                     if_exists: str = 'fail') -> DataSource:
        """
        Publishes Features from an existing DataSource table

        params:
            data_source_id: ID to a Rasgo DataSource
            features: List of column names that will be features
            dimensions: List of column names that will be dimensions
            granularity: List of grains that describe the form of the data. Common values are: 'day', 'week', 'month', 'second'
            tags: List of tags to be added to all features
            feature_set_name: deprecated parameter - any values passed in are ignored

            if_exists:  fail - returns an error message if features already exists against this table
                        return - returns the features without operating on them
                        edit - edits the existing features
                        new - creates new features

        return:
            Rasgo DataSource
        """
        granularity = granularity if granularity else []
        tags = tags if tags else []

        return self.publish.features_from_source(data_source_id, features, dimensions, granularity, tags, feature_set_name, sandbox, if_exists)

    @deprecated_with_replacement('v0.3', 'publish.features_from_yml')
    def publish_features_from_yml(self,
                                  yml_file: str,
                                  sandbox: Optional[bool] = True,
                                  git_repo: Optional[str] = None) -> DataSource:
        """
        Publishes metadata about Features to Pyrasgo

        :param yml_file: Rasgo compliant yml file that describes the feature(s) being created
        :param sandbox: Status of the features (True = 'Sandboxed' | False = 'Productionized')
        :param git_repo: Filepath string to these feature recipes in git
        :return: description of the features created
        """
        return self.publish.features_from_yml(yml_file, sandbox, git_repo)

    @deprecated_with_replacement('v0.3', 'publish.source_data')
    def publish_source_data(self,
                            source_type: str,
                            file_path: Optional[Path] = None,
                            df: Optional[pd.DataFrame] = None,
                            table: Optional[str] = None,
                            table_database:Optional[str] = None,
                            table_schema: Optional[str] = None,
                            data_source_name: Optional[str] = None,
                            data_source_domain: Optional[str] = None,
                            data_source_table_name: Optional[str] = None, parent_data_source_id: Optional[int] = None,
                            if_exists: Optional[str] = 'fail'
                            ) -> DataSource:
        """
        Push a csv, Dataframe, or table to a Snowflake table and register it as a Rasgo DataSource (TM)

        NOTES: csv files will import all columns as strings

        params:
            source_type: Values: ['csv', 'dataframe', 'table']
            df: pandas DataFrame (only use when passing source_type = 'dataframe')
            file_path: full path to a file on your local machine (only use when passing source_type = 'csv')
            table: name of a valid Snowflake table in your Rasgo account (only use when passing source_type = 'table')
            table_database: Optional: name of the database of the table passed in 'table' param (only use when passing source_type = 'table')
            table_schema: Optional: name of the schema of the table passed in 'table' param (only use when passing source_type = 'table')

            data_source_name: Optional name for the DataSource (if not provided a random string will be used)
            data_source_table_name: Optional name for the DataSource table in Snowflake (if not provided a random string will be used)
            data_source_domain: Optional domain for the DataSource (default is NULL)
            parent_data_source_id: Optional ID of a valid Rasgo DataSource that is a parent to this DataSource (default is NULL)

            if_exists: Values: ['fail', 'append', 'replace'] directs the function what to do if a DataSource already exists with this table name  (defaults to fail)

        return:
            Rasgo DataSource
        """
        return self.publish.source_data(source_type, file_path, df, table, table_database, table_schema, data_source_name, data_source_domain, data_source_table_name, parent_data_source_id, if_exists)

    @deprecated_with_replacement('v0.3', 'read.collection_data')
    def read_collection_data(self,
                             collection_id: int,
                             filters: Optional[Dict[str, str]] = None,
                             limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Collection

        :param collection_id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        return self.read.collection_data(collection_id, filters, limit)

    @deprecated_with_replacement('v0.3', 'read.feature_data')
    def read_feature_data(self,
                          feature_id: int,
                          filters: Optional[Dict[str, str]] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Feature data

        :param feature_id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        return self.read.feature_data(feature_id, filters, limit)

    @deprecated_with_replacement('v0.3', 'read.source_data')
    def read_source_data(self,
                         source_id: int,
                         filters: Optional[Dict[str, str]] = None,
                         limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo DataSource

        :param source_id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        return self.read.source_data(source_id, filters, limit)