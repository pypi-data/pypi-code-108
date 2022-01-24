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
import six
import trafaret as t

from datarobot import errors
from datarobot._compat import String
from datarobot.models.api_object import APIObject
from datarobot.utils import parse_time

from ..helpers.feature_discovery import SecondaryDataset


class DatasetConfiguration(object):
    """Specify a dataset configuration

    .. versionadded:: v2.20

    Attributes
    ----------
    feature_engineering_graph_id: str
        Id of the feature engineering graph
    secondary_datasets: list of SecondaryDataset
        List of secondary datasets
    """

    def __init__(self, feature_engineering_graph_id=None, secondary_datasets=None):
        self.feature_engineering_graph_id = feature_engineering_graph_id
        self.secondary_datasets = secondary_datasets

    def to_dict(self):
        return {
            "feature_engineering_graph_id": self.feature_engineering_graph_id,
            "secondary_datasets": [dataset.to_dict() for dataset in self.secondary_datasets],
        }


class DatasetsCredentials(object):
    """Credentials of the JDBC/ dynamic based secondary datasets

    .. versionadded:: v2.23

    Attributes
    ----------
    credential_id: str
        Id of credential store
    catalog_version_id: str
        Catalog version Id of the secondary dataset
    url: str, optional
        JDBC connection URL for the dataset
    """

    def __init__(self, credential_id=None, catalog_version_id=None, url=None):
        self.credential_id = credential_id
        self.catalog_version_id = catalog_version_id
        self.url = url

    def to_dict(self):
        return {
            "credential_id": self.credential_id,
            "catalog_version_id": self.catalog_version_id,
            "url": self.url,
        }


class SecondaryDatasetConfigurations(APIObject):
    """ Create secondary dataset configurations for a given project

    .. versionadded:: v2.20

    Attributes
    ----------
    id : str
        Id of this secondary dataset configuration
    project_id : str
        Id of the associated project.
    config: list of DatasetConfiguration (Deprecated in version v2.23)
        List of secondary dataset configurations
    secondary_datasets: list of SecondaryDataset (new in v2.23)
        List of secondary datasets (secondaryDataset)
    name: str
        Verbose name of the SecondaryDatasetConfig. null if it wasn't specified.
    created: datetime.datetime
        DR-formatted datetime. null for legacy (before DR 6.0) db records.
    creator_user_id: str
        Id of the user created this config.
    creator_full_name: str
        fullname or email of the user created this config.
    featurelist_id: str, optional
        Id of the feature list. null if it wasn't specified.
    credential_ids: list of DatasetsCredentials, optional
        credentials used by the secondary datasets if the datasets used
        in the configuration are from datasource
    is_default: bool, optional
        Boolean flag if default config created during feature disovery aim
    project_version: str, optional
        Version of project when its created (Release version)
    """

    _base_url = "projects/{}/secondaryDatasetsConfigurations/"
    _stored_credentials = t.Dict(
        {
            t.Key("credential_id"): String,
            t.Key("catalog_version_id"): String,
            t.Key("url", optional=True): String | t.Null,
        }
    )
    _secondary_dataset_converter = t.Dict(
        {
            t.Key("identifier"): String(min_length=3, max_length=20),
            t.Key("catalog_version_id"): String,
            t.Key("catalog_id"): String,
            t.Key("snapshot_policy", optional=True, default="latest"): t.Enum(
                "latest", "specified", "dynamic"
            ),
        }
    )

    _dataset_configuration_converter = t.Dict(
        {
            t.Key("feature_engineering_graph_id"): String(),
            t.Key("secondary_datasets"): t.List(_secondary_dataset_converter),
        }
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("project_id"): String(),
            t.Key("config", optional=True): t.List(_dataset_configuration_converter),
            t.Key("secondary_datasets"): t.List(_secondary_dataset_converter),
            t.Key("name", optional=True): String | t.Null,
            t.Key("creator_full_name", optional=True): String(),
            t.Key("creator_user_id", optional=True): String(),
            t.Key("created", optional=True): parse_time,
            t.Key("featurelist_id", optional=True): String | t.Null,
            t.Key("credential_ids", optional=True): t.List(_stored_credentials),
            t.Key("is_default", optional=True): t.Bool,
            t.Key("project_version", optional=True): String | t.Null,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id=None,
        project_id=None,
        config=None,
        secondary_datasets=None,
        name=None,
        creator_full_name=None,
        creator_user_id=None,
        created=None,
        featurelist_id=None,
        credential_ids=None,
        is_default=None,
        project_version=None,
    ):
        self.id = id
        self.project_id = project_id
        self.config = config
        self.name = name
        self.secondary_datasets = secondary_datasets
        self.creator_full_name = creator_full_name
        self.creator_user_id = creator_user_id
        self.created = created
        self.featurelist_id = featurelist_id
        self.credential_ids = credential_ids
        self.is_default = is_default
        self.project_version = project_version

    def to_dict(self):
        config, secondary_datasets = None, None
        if self.config:
            config = [c.to_dict() for c in self.config]
        if self.secondary_datasets:
            secondary_datasets = [sc.to_dict() for sc in self.secondary_datasets]
        return {
            "id": self.id,
            "project_id": self.project_id,
            "config": config,
            "name": self.name,
            "secondary_datasets": secondary_datasets,
            "creator_full_name": self.creator_full_name,
            "creator_user_id": self.creator_user_id,
            "created": self.created,
            "featurelist_id": self.featurelist_id,
            "credential_ids": self.credential_ids,
            "is_default": self.is_default,
            "project_version": self.project_version,
        }

    @classmethod
    def from_data(cls, data):
        checked = cls._converter.check(data)
        safe_data = cls._filter_data(checked)

        id = safe_data.get("id", None)
        project_id = safe_data.get("project_id", None)
        name = safe_data.get("name", None)
        secondary_datasets = safe_data.get("secondary_datasets", None)
        creator_full_name = safe_data.get("creator_full_name", None)
        creator_user_id = safe_data.get("creator_user_id", None)
        created = safe_data.get("created", None)
        featurelist_id = safe_data.get("featurelist_id", None)
        credential_ids = safe_data.get("credential_ids", None)
        is_default = safe_data.get("is_default", None)
        project_version = safe_data.get("project_version", None)
        dataset_configs = safe_data.get("config", [])

        conf_list = []
        for conf in dataset_configs:
            graph_id = conf.get("feature_engineering_graph_id", None)
            datasets = conf.get("secondary_datasets", None)
            dataset_list = []
            for d in datasets:
                dataset = SecondaryDataset(**d)
                dataset_list.append(dataset)
            dataset_configuration = DatasetConfiguration(graph_id, dataset_list)
            conf_list.append(dataset_configuration)

        secondary_datasets_list = []
        for d in secondary_datasets:
            dataset = SecondaryDataset(**d)
            secondary_datasets_list.append(dataset)
        return SecondaryDatasetConfigurations(
            id=id,
            project_id=project_id,
            config=conf_list,
            secondary_datasets=secondary_datasets_list,
            name=name,
            creator_full_name=creator_full_name,
            creator_user_id=creator_user_id,
            created=created,
            featurelist_id=featurelist_id,
            credential_ids=credential_ids,
            is_default=is_default,
            project_version=project_version,
        )

    @classmethod
    def create(cls, project_id, secondary_datasets, name, featurelist_id=None):
        """ create secondary dataset configurations

        .. versionadded:: v2.20

        Parameters
        ----------
        project_id : str
            id of the associated project.
        secondary_datasets: list of SecondaryDataset (New in version v2.23)
            list of secondary datasets used by the configuration
            each element is a ``datarobot.helpers.feature_discovery.SecondaryDataset``
        name: str (New in version v2.23)
            Name of the secondary datasets configuration
        featurelist_id: str, or None (New in version v2.23)
            Id of the featurelist

        Returns
        -------
        an instance of SecondaryDatasetConfigurations

        Raises
        ------
        ClientError
            raised if incorrect configuration parameters are provided

        Examples
        --------
        .. code-block:: python

            profile_secondary_dataset = dr.SecondaryDataset(
                identifier='profile',
                catalog_id='5ec4aec1f072bc028e3471ae',
                catalog_version_id='5ec4aec2f072bc028e3471b1',
                snapshot_policy='latest'
            )

            transaction_secondary_dataset = dr.SecondaryDataset(
                identifier='transaction',
                catalog_id='5ec4aec268f0f30289a03901',
                catalog_version_id='5ec4aec268f0f30289a03900',
                snapshot_policy='latest'
            )

            secondary_datasets = [profile_secondary_dataset, transaction_secondary_dataset]
            new_secondary_dataset_config = dr.SecondaryDatasetConfigurations.create(
                project_id=project.id,
                name='My config',
                secondary_datasets=secondary_datasets
            )


            >>> new_secondary_dataset_config.id
            '5fd1e86c589238a4e635e93d'
        """
        if not project_id:
            raise errors.ClientError(six.text_type("project_id cannot be None or empty"), 422)
        if not secondary_datasets:
            raise errors.ClientError(
                six.text_type("secondary_datasets cannot be None or empty"), 422,
            )

        url = cls._base_url.format(project_id)
        payload_secondary_datasets = []
        for sec_dataset in secondary_datasets:
            if isinstance(sec_dataset, SecondaryDataset):
                payload_secondary_datasets.append(sec_dataset.to_payload())
            else:
                payload_secondary_datasets.append(sec_dataset)

        payload = {
            "name": name,
            "featurelistId": featurelist_id,
            "secondaryDatasets": payload_secondary_datasets,
        }
        response = cls._client.post(url, data=payload)

        status = response.status_code
        if status == 201:
            return cls.from_server_data(response.json())
        else:
            error_msg = response.json().get(
                "message", six.text_type("error in processing secondary dataset configuration")
            )
            raise errors.ClientError(
                error_msg + six.text_type(" with server returned status {}").format(status), status,
            )

    def delete(self):
        """ Removes the Secondary datasets configuration

        .. versionadded:: v2.21

        Raises
        ------
        ClientError
            Raised if an invalid or already deleted secondary dataset config id is provided

        Examples
        --------
        .. code-block:: python

            # Deleting with a valid secondary_dataset_config id
            status_code = dr.SecondaryDatasetConfigurations.delete(some_config_id)
            status_code
            >>> 204
        """
        url = self._base_url.format(self.project_id)
        self._client.delete("{}{}/".format(url, self.id))

    def get(self):
        """ Retrieve a single secondary dataset configuration for a given id

        .. versionadded:: v2.21

        Returns
        -------
        secondary_dataset_configurations : SecondaryDatasetConfigurations
            The requested secondary dataset configurations

        Examples
        --------
        .. code-block:: python

            config_id = '5fd1e86c589238a4e635e93d'
            secondary_dataset_config = dr.SecondaryDatasetConfigurations(id=config_id).get()
            >>> secondary_dataset_config
            {
                 'created': datetime.datetime(2020, 12, 9, 6, 16, 22, tzinfo=tzutc()),
                 'creator_full_name': u'abc@datarobot.com',
                 'creator_user_id': u'asdf4af1gf4bdsd2fba1de0a',
                 'credential_ids': None,
                 'featurelist_id': None,
                 'id': u'5fd1e86c589238a4e635e93d',
                 'is_default': True,
                 'name': u'My config',
                 'project_id': u'5fd06afce2456ec1e9d20457',
                 'project_version': None,
                 'secondary_datasets': [
                        {
                            'snapshot_policy': u'latest',
                            'identifier': u'profile',
                            'catalog_version_id': u'5fd06b4af24c641b68e4d88f',
                            'catalog_id': u'5fd06b4af24c641b68e4d88e'
                        },
                        {
                            'snapshot_policy': u'dynamic',
                            'identifier': u'transaction',
                            'catalog_version_id': u'5fd1e86c589238a4e635e98e',
                            'catalog_id': u'5fd1e86c589238a4e635e98d'
                        }
                 ]
            }
        """
        assert self.project_id
        url = self._base_url.format(self.project_id)
        return self.from_location("{}{}/".format(url, self.id))

    @classmethod
    def list(cls, project_id, featurelist_id=None, limit=None, offset=None):
        """ Returns list of secondary dataset configurations.

        .. versionadded:: v2.23

        Parameters
        ----------
        project_id: str
            The Id of project
        featurelist_id: str, optional
            Id of the feature list to filter the secondary datasets configurations

        Returns
        -------
        secondary_dataset_configurations : list of SecondaryDatasetConfigurations
            The requested list of secondary dataset configurations for a given project

        Examples
        --------
        .. code-block:: python

            pid = '5fd06afce2456ec1e9d20457'
            secondary_dataset_configs = dr.SecondaryDatasetConfigurations.list(pid)
            >>> secondary_dataset_configs[0]
                {
                     'created': datetime.datetime(2020, 12, 9, 6, 16, 22, tzinfo=tzutc()),
                     'creator_full_name': u'abc@datarobot.com',
                     'creator_user_id': u'asdf4af1gf4bdsd2fba1de0a',
                     'credential_ids': None,
                     'featurelist_id': None,
                     'id': u'5fd1e86c589238a4e635e93d',
                     'is_default': True,
                     'name': u'My config',
                     'project_id': u'5fd06afce2456ec1e9d20457',
                     'project_version': None,
                     'secondary_datasets': [
                            {
                                'snapshot_policy': u'latest',
                                'identifier': u'profile',
                                'catalog_version_id': u'5fd06b4af24c641b68e4d88f',
                                'catalog_id': u'5fd06b4af24c641b68e4d88e'
                            },
                            {
                                'snapshot_policy': u'dynamic',
                                'identifier': u'transaction',
                                'catalog_version_id': u'5fd1e86c589238a4e635e98e',
                                'catalog_id': u'5fd1e86c589238a4e635e98d'
                            }
                     ]
                }
        """
        kwargs = {}
        if featurelist_id:
            kwargs["featurelistId"] = featurelist_id
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset

        url = cls._base_url.format(project_id)
        r_data = cls._client.get(url, params=kwargs).json()
        return [SecondaryDatasetConfigurations.from_server_data(item) for item in r_data["data"]]
