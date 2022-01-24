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

from datarobot._compat import String
from datarobot.client import get_client, staticproperty
from datarobot.models.api_object import APIObject
from datarobot.models.sharing import SharingAccess
from datarobot.utils.pagination import unpaginate

from ..utils import encode_utf8_if_py2, from_api, parse_time

_data_store_params_converter = t.Dict(
    {t.Key("driver_id"): String(), t.Key("jdbc_url", optional=True): String() | t.Null()}
).ignore_extra("*")


class DataStoreParameters(object):
    def __init__(self, driver_id, jdbc_url):
        _data_store_params_converter.check({"driver_id": driver_id, "jdbc_url": jdbc_url})
        self.driver_id = driver_id
        self.jdbc_url = jdbc_url

    def collect_payload(self):
        return {"driver_id": self.driver_id, "jdbc_url": self.jdbc_url}


class DataStore(APIObject):
    """ A data store. Represents database

    Attributes
    ----------
    id : str
        the id of the data store.
    data_store_type : str
        the type of data store.
    canonical_name : str
        the user-friendly name of the data store.
    creator : str
        the id of the user who created the data store.
    updated : datetime.datetime
        the time of the last update
    params : DataStoreParameters
        a list specifying data store parameters.
    """

    _path = "externalDataStores/"
    _client = staticproperty(get_client)
    _converter = t.Dict(
        {
            t.Key("id", optional=True) >> "data_store_id": String(),
            t.Key("type") >> "data_store_type": String(),
            t.Key("canonical_name"): String(),
            t.Key("creator"): String(),
            t.Key("params"): _data_store_params_converter,
            t.Key("updated"): parse_time,
            t.Key("role"): String(),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        data_store_id=None,
        data_store_type=None,
        canonical_name=None,
        creator=None,
        updated=None,
        params=None,
        role=None,
    ):
        self._id = data_store_id
        self._type = data_store_type
        self.canonical_name = canonical_name
        self._creator = creator
        self._updated = updated
        self.params = params
        self.role = role

    @classmethod
    def list(cls):
        """
        Returns list of available data stores.

        Returns
        -------
        data_stores : list of DataStore instances
            contains a list of available data stores.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_stores = dr.DataStore.list()
            >>> data_stores
            [DataStore('Demo'), DataStore('Airlines')]
        """
        r_data = cls._client.get(cls._path).json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def get(cls, data_store_id):
        """
        Gets the data store.

        Parameters
        ----------
        data_store_id : str
            the identifier of the data store.

        Returns
        -------
        data_store : DataStore
            the required data store.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_store = dr.DataStore.get('5a8ac90b07a57a0001be501e')
            >>> data_store
            DataStore('Demo')
        """
        return cls.from_location("{}{}/".format(cls._path, data_store_id))

    @classmethod
    def create(cls, data_store_type, canonical_name, driver_id, jdbc_url):
        """
        Creates the data store.

        Parameters
        ----------
        data_store_type : str
            the type of data store.
        canonical_name : str
            the user-friendly name of the data store.
        driver_id : str
            the identifier of the DataDriver.
        jdbc_url : str
             the full JDBC url, for example `jdbc:postgresql://my.dbaddress.org:5432/my_db`.

        Returns
        -------
        data_store : DataStore
            the created data store.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_store = dr.DataStore.create(
            ...     data_store_type='jdbc',
            ...     canonical_name='Demo DB',
            ...     driver_id='5a6af02eb15372000117c040',
            ...     jdbc_url='jdbc:postgresql://my.db.address.org:5432/perftest'
            ... )
            >>> data_store
            DataStore('Demo DB')
        """
        payload = {
            "type": data_store_type,
            "canonicalName": canonical_name,
            "params": DataStoreParameters(driver_id=driver_id, jdbc_url=jdbc_url).collect_payload(),
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def update(self, canonical_name=None, driver_id=None, jdbc_url=None):
        """
        Updates the data store.

        Parameters
        ----------
        canonical_name : str
            optional, the user-friendly name of the data store.
        driver_id : str
            optional, the identifier of the DataDriver.
        jdbc_url : str
            optional, the full JDBC url,
            for example `jdbc:postgresql://my.dbaddress.org:5432/my_db`.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_store = dr.DataStore.get('5ad5d2afef5cd700014d3cae')
            >>> data_store
            DataStore('Demo DB')
            >>> data_store.update(canonical_name='Demo DB updated')
            >>> data_store
            DataStore('Demo DB updated')
        """
        payload = {
            "canonicalName": canonical_name or self.canonical_name,
            "params": DataStoreParameters(
                driver_id=driver_id or self.params.driver_id,
                jdbc_url=jdbc_url or self.params.jdbc_url,
            ).collect_payload(),
        }
        r_data = self._client.patch("{}{}/".format(self._path, self.id), data=payload).json()
        self.canonical_name = r_data["canonicalName"]
        self.params = DataStoreParameters(r_data["params"]["driverId"], r_data["params"]["jdbcUrl"])

    def delete(self):
        """ Removes the DataStore """
        self._client.delete("{}{}/".format(self._path, self.id))

    def test(self, username, password):
        """
        Tests database connection.

        Parameters
        ----------
        username : str
            the username for database authentication.
        password : str
            the password for database authentication. The password is encrypted
            at server side and never saved / stored

        Returns
        -------
        message : dict
            message with status.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_store = dr.DataStore.get('5ad5d2afef5cd700014d3cae')
            >>> data_store.test(username='db_username', password='db_password')
            {'message': 'Connection successful'}
        """
        payload = {"user": username, "password": password}
        return self._client.post("{}{}/test/".format(self._path, self.id), data=payload).json()

    def schemas(self, username, password):
        """
        Returns list of available schemas.

        Parameters
        ----------
        username : str
            the username for database authentication.
        password : str
            the password for database authentication. The password is encrypted
            at server side and never saved / stored

        Returns
        -------
        response : dict
            dict with database name and list of str - available schemas

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_store = dr.DataStore.get('5ad5d2afef5cd700014d3cae')
            >>> data_store.schemas(username='db_username', password='db_password')
            {'catalog': 'perftest', 'schemas': ['demo', 'information_schema', 'public']}
        """
        payload = {"user": username, "password": password}
        return self._client.post("{}{}/schemas/".format(self._path, self.id), data=payload).json()

    def tables(self, username, password, schema=None):
        """
        Returns list of available tables in schema.

        Parameters
        ----------
        username : str
            optional, the username for database authentication.
        password : str
            optional, the password for database authentication. The password is encrypted
            at server side and never saved / stored
        schema : str
            optional, the schema name.

        Returns
        -------
        response : dict
            dict with catalog name and tables info

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_store = dr.DataStore.get('5ad5d2afef5cd700014d3cae')
            >>> data_store.tables(username='db_username', password='db_password', schema='demo')
            {'tables': [{'type': 'TABLE', 'name': 'diagnosis', 'schema': 'demo'}, {'type': 'TABLE',
            'name': 'kickcars', 'schema': 'demo'}, {'type': 'TABLE', 'name': 'patient',
            'schema': 'demo'}, {'type': 'TABLE', 'name': 'transcript', 'schema': 'demo'}],
            'catalog': 'perftest'}
        """
        payload = {"schema": schema, "user": username, "password": password}
        return self._client.post("{}{}/tables/".format(self._path, self.id), data=payload).json()

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        converted_data = cls._converter.check(from_api(data))
        params = converted_data.pop("params")
        converted_data["params"] = DataStoreParameters(params["driver_id"], params.get("jdbc_url"))
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
        """ Retrieve what users have access to this data store

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
        """ Modify the ability of users to access this data store

        .. versionadded:: v2.14

        Parameters
        ----------
        access_list : list of :class:`SharingAccess <datarobot.SharingAccess>`
            the modifications to make.

        Raises
        ------
        datarobot.ClientError :
            if you do not have permission to share this data store, if the user you're sharing with
            doesn't exist, if the same user appears multiple times in the access_list, or if these
            changes would leave the data store without an owner.

        Examples
        --------
        Transfer access to the data store from old_user@datarobot.com to new_user@datarobot.com

        .. code-block:: python

            import datarobot as dr

            new_access = dr.SharingAccess(new_user@datarobot.com,
                                          dr.enums.SHARING_ROLE.OWNER, can_share=True)
            access_list = [dr.SharingAccess(old_user@datarobot.com, None), new_access]

            dr.DataStore.get('my-data-store-id').share(access_list)
        """
        payload = {"data": [access.collect_payload() for access in access_list]}
        self._client.patch(
            "{}{}/accessControl/".format(self._path, self.id), data=payload, keep_attrs={"role"}
        )
