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
from datarobot.client import get_client, staticproperty
from datarobot.models.api_object import APIObject
from datarobot.models.dataset import Dataset
from datarobot.models.sharing import SharingAccess
from datarobot.utils.pagination import unpaginate

from ..utils import encode_utf8_if_py2, from_api, parse_time

_data_source_params_converter = t.Dict(
    {
        t.Key("data_store_id"): String() | t.Null,
        t.Key("table", optional=True): String() | t.Null,
        t.Key("schema", optional=True): String() | t.Null,
        t.Key("partition_column", optional=True): String() | t.Null,
        t.Key("query", optional=True): String() | t.Null,
        t.Key("fetch_size", optional=True): Int() | t.Null,
    }
).ignore_extra("*")


class DataSourceParameters(object):
    """ Data request configuration

    Attributes
    ----------
    data_store_id : str
        the id of the DataStore.
    table : str
        optional, the name of specified database table.
    schema : str
        optional, the name of the schema associated with the table.
    partition_column : str
        optional, the name of the partition column.
    query : str
        optional, the user specified SQL query.
    fetch_size : int
        optional, a user specified fetch size in the range [1, 20000].
        By default a fetchSize will be assigned to balance throughput and memory usage
    """

    def __init__(
        self,
        data_store_id=None,
        table=None,
        schema=None,
        partition_column=None,
        query=None,
        fetch_size=None,
    ):
        _data_source_params_converter.check(
            {
                "data_store_id": data_store_id,
                "table": table,
                "schema": schema,
                "partition_column": partition_column,
                "query": query,
                "fetch_size": fetch_size,
            }
        )
        self.data_store_id = data_store_id
        self.table = table
        self.schema = schema
        self.partition_column = partition_column
        self.query = query
        self.fetch_size = fetch_size

    def collect_payload(self):
        return {
            "data_store_id": self.data_store_id,
            "table": self.table,
            "schema": self.schema,
            "partition_column": self.partition_column,
            "query": self.query,
            "fetch_size": self.fetch_size,
        }

    @classmethod
    def from_server_data(cls, data):
        converted_data = _data_source_params_converter.check(from_api(data))
        return cls(**converted_data)

    def __eq__(self, other):
        self_payload = self.collect_payload()
        other_payload = other.collect_payload()
        del self_payload["data_store_id"]
        del other_payload["data_store_id"]
        return self_payload == other_payload


class DataSource(APIObject):
    """ A data source. Represents data request

    Attributes
    ----------
    id : str
        the id of the data source.
    type : str
        the type of data source.
    canonical_name : str
        the user-friendly name of the data source.
    creator : str
        the id of the user who created the data source.
    updated : datetime.datetime
        the time of the last update.
    params : DataSourceParameters
        a list specifying data source parameters.
    """

    _path = "externalDataSources/"
    _client = staticproperty(get_client)
    _converter = t.Dict(
        {
            t.Key("id", optional=True) >> "data_source_id": String(),
            t.Key("type") >> "data_source_type": String(),
            t.Key("canonical_name"): String(),
            t.Key("creator"): String(),
            t.Key("params"): _data_source_params_converter,
            t.Key("updated"): parse_time,
            t.Key("role"): String(),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        data_source_id=None,
        data_source_type=None,
        canonical_name=None,
        creator=None,
        updated=None,
        params=None,
        role=None,
    ):
        self._id = data_source_id
        self._type = data_source_type
        self.canonical_name = canonical_name
        self._creator = creator
        self._updated = updated
        self.params = params
        self.role = role

    @classmethod
    def list(cls):
        """
        Returns list of available data sources.

        Returns
        -------
        data_sources : list of DataSource instances
            contains a list of available data sources.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_sources = dr.DataSource.list()
            >>> data_sources
            [DataSource('Diagnostics'), DataSource('Airlines 100mb'), DataSource('Airlines 10mb')]
        """
        r_data = cls._client.get(cls._path).json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def get(cls, data_source_id):
        """
        Gets the data source.

        Parameters
        ----------
        data_source_id : str
            the identifier of the data source.

        Returns
        -------
        data_source : DataSource
            the requested data source.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_source = dr.DataSource.get('5a8ac9ab07a57a0001be501f')
            >>> data_source
            DataSource('Diagnostics')
        """
        return cls.from_location("{}{}/".format(cls._path, data_source_id))

    @classmethod
    def create(cls, data_source_type, canonical_name, params):
        """
        Creates the data source.

        Parameters
        ----------
        data_source_type : str
            the type of data source.
        canonical_name : str
            the user-friendly name of the data source.
        params : DataSourceParameters
            a list specifying data source parameters.

        Returns
        -------
        data_source : DataSource
            the created data source.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> params = dr.DataSourceParameters(
            ...     data_store_id='5a8ac90b07a57a0001be501e',
            ...     query='SELECT * FROM airlines10mb WHERE "Year" >= 1995;'
            ... )
            >>> data_source = dr.DataSource.create(
            ...     data_source_type='jdbc',
            ...     canonical_name='airlines stats after 1995',
            ...     params=params
            ... )
            >>> data_source
            DataSource('airlines stats after 1995')
        """
        payload = {
            "type": data_source_type,
            "canonicalName": canonical_name,
            "params": params.collect_payload(),
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def update(self, canonical_name=None, params=None):
        """
        Creates the data source.

        Parameters
        ----------
        canonical_name : str
            optional, the user-friendly name of the data source.
        params : DataSourceParameters
            optional, the identifier of the DataDriver.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_source = dr.DataSource.get('5ad840cc613b480001570953')
            >>> data_source
            DataSource('airlines stats after 1995')
            >>> params = dr.DataSourceParameters(
            ...     query='SELECT * FROM airlines10mb WHERE "Year" >= 1990;'
            ... )
            >>> data_source.update(
            ...     canonical_name='airlines stats after 1990',
            ...     params=params
            ... )
            >>> data_source
            DataSource('airlines stats after 1990')
        """
        payload = {
            "canonicalName": canonical_name or self.canonical_name,
            "params": params.collect_payload() if params else self.params.collect_payload(),
        }
        r_data = self._client.patch("{}{}/".format(self._path, self.id), data=payload).json()
        self.canonical_name = r_data["canonicalName"]
        self.params = DataSourceParameters.from_server_data(r_data.pop("params"))

    def delete(self):
        """ Removes the DataSource """
        self._client.delete("{}{}/".format(self._path, self.id))

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        converted_data = cls._converter.check(from_api(data))
        params = converted_data.pop("params")
        data_store_id = params.pop("data_store_id")
        converted_data["params"] = DataSourceParameters(data_store_id, **params)
        return cls(**converted_data)

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}('{}')".format(self.__class__.__name__, self.canonical_name or self.id)
        )

    @property
    def id(self):
        return self._id

    @property
    def creator(self):
        return self._creator

    @property
    def type(self):
        return self._type

    @property
    def updated(self):
        return self._updated

    def get_access_list(self):
        """ Retrieve what users have access to this data source

        .. versionadded:: v2.14

        Returns
        -------
        list of :class:`SharingAccess <datarobot.SharingAccess>`
        """
        url = "{}{}/accessControl/".format(self._path, self.id)
        return [
            SharingAccess.from_server_data(datum) for datum in unpaginate(url, {}, self._client)
        ]

    def share(self, access_list):
        """ Modify the ability of users to access this data source

        .. versionadded:: v2.14

        Parameters
        ----------
        access_list : list of :class:`SharingAccess <datarobot.SharingAccess>`
            the modifications to make.

        Raises
        ------
        datarobot.ClientError :
            if you do not have permission to share this data source, if the user you're sharing with
            doesn't exist, if the same user appears multiple times in the access_list, or if these
            changes would leave the data source without an owner

        Examples
        --------
        Transfer access to the data source from old_user@datarobot.com to new_user@datarobot.com

        .. code-block:: python

            import datarobot as dr

            new_access = dr.SharingAccess(new_user@datarobot.com,
                                          dr.enums.SHARING_ROLE.OWNER, can_share=True)
            access_list = [dr.SharingAccess(old_user@datarobot.com, None), new_access]

            dr.DataSource.get('my-data-source-id').share(access_list)
        """
        payload = {"data": [access.collect_payload() for access in access_list]}
        self._client.patch(
            "{}{}/accessControl/".format(self._path, self.id), data=payload, keep_attrs={"role"}
        )

    def create_dataset(
        self,
        username=None,
        password=None,
        do_snapshot=None,
        persist_data_after_ingestion=None,
        categories=None,
        credential_id=None,
        use_kerberos=None,
    ):
        """
        Create a :py:class:`Dataset <datarobot.Dataset>` from this data source.

        .. versionadded:: v2.22

        Parameters
        ----------
        username: string, optional
            The username for database authentication.
        password: string, optional
            The password (in cleartext) for database authentication. The password
            will be encrypted on the server side in scope of HTTP request and never saved or stored.
        do_snapshot: bool, optional
            If unset, uses the server default: True.
            If true, creates a snapshot dataset; if
            false, creates a remote dataset. Creating snapshots from non-file sources requires an
            additional permission, `Enable Create Snapshot Data Source`.
        persist_data_after_ingestion: bool, optional
            If unset, uses the server default: True.
            If true, will enforce saving all data
            (for download and sampling) and will allow a user to view extended data profile
            (which includes data statistics like min/max/median/mean, histogram, etc.). If false,
            will not enforce saving data. The data schema (feature names and types) still will be
            available. Specifying this parameter to false and `doSnapshot` to true will result in
            an error.
        categories: list[string], optional
            An array of strings describing the intended use of the dataset. The
            current supported options are "TRAINING" and "PREDICTION".
        credential_id: string, optional
            The ID of the set of credentials to
            use instead of user and password. Note that with this change, username and password
            will become optional.
        use_kerberos: bool, optional
            If unset, uses the server default: False.
            If true, use kerberos authentication for database authentication.

        Returns
        -------
        response: Dataset
            The Dataset created from the uploaded data
        """
        return Dataset.create_from_data_source(
            self.id,
            username=username,
            password=password,
            do_snapshot=do_snapshot,
            persist_data_after_ingestion=persist_data_after_ingestion,
            categories=categories,
            credential_id=credential_id,
            use_kerberos=use_kerberos,
        )
