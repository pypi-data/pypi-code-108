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

import trafaret as t

from datarobot._compat import String
from datarobot.client import get_client, staticproperty
from datarobot.models.api_object import APIObject

from ..utils import encode_utf8_if_py2


class DataDriver(APIObject):
    """ A data driver

    Attributes
    ----------
    id : str
        the id of the driver.
    class_name : str
        the Java class name for the driver.
    canonical_name : str
        the user-friendly name of the driver.
    creator : str
        the id of the user who created the driver.
    base_names : list of str
        a list of the file name(s) of the jar files.
    """

    _path = "externalDataDrivers/"
    _file_upload_path = "externalDataDriverFile/"
    _client = staticproperty(get_client)
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("class_name"): String(),
            t.Key("canonical_name"): String(),
            t.Key("creator"): String(),
            t.Key("base_names"): t.List(String()),
        }
    ).allow_extra("*")

    def __init__(
        self, id=None, creator=None, base_names=None, class_name=None, canonical_name=None
    ):
        self._id = id
        self._creator = creator
        self._base_names = base_names
        self.class_name = class_name
        self.canonical_name = canonical_name

    @classmethod
    def list(cls):
        """
        Returns list of available drivers.

        Returns
        -------
        drivers : list of DataDriver instances
            contains a list of available drivers.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> drivers = dr.DataDriver.list()
            >>> drivers
            [DataDriver('mysql'), DataDriver('RedShift'), DataDriver('PostgreSQL')]
        """
        r_data = cls._client.get(cls._path).json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def get(cls, driver_id):
        """
        Gets the driver.

        Parameters
        ----------
        driver_id : str
            the identifier of the driver.

        Returns
        -------
        driver : DataDriver
            the required driver.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> driver = dr.DataDriver.get('5ad08a1889453d0001ea7c5c')
            >>> driver
            DataDriver('PostgreSQL')
        """
        return cls.from_location("{}{}/".format(cls._path, driver_id))

    @classmethod
    def create(cls, class_name, canonical_name, files):
        """
        Creates the driver. Only available to admin users.

        Parameters
        ----------
        class_name : str
            the Java class name for the driver.
        canonical_name : str
            the user-friendly name of the driver.
        files : list of str
            a list of the file paths on file system file_path(s) for the driver.

        Returns
        -------
        driver : DataDriver
            the created driver.

        Raises
        ------
        ClientError
            raised if user is not granted for `Can manage JDBC database drivers` feature

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> driver = dr.DataDriver.create(
            ...     class_name='org.postgresql.Driver',
            ...     canonical_name='PostgreSQL',
            ...     files=['/tmp/postgresql-42.2.2.jar']
            ... )
            >>> driver
            DataDriver('PostgreSQL')
        """

        base_names = []
        local_jar_urls = []
        for file_path in files:
            name = file_path.split(os.sep)[-1]
            resp = cls._client.build_request_with_file(
                "POST", cls._file_upload_path, name, file_path=file_path
            ).json()
            base_names.append(name)
            local_jar_urls.append(resp["localUrl"])

        payload = {
            "className": class_name,
            "canonicalName": canonical_name,
            "localJarUrls": local_jar_urls,
            "baseNames": base_names,
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def update(self, class_name=None, canonical_name=None):
        """
        Updates the driver. Only available to admin users.

        Parameters
        ----------
        class_name : str
            the Java class name for the driver.
        canonical_name : str
            the user-friendly name of the driver.

        Raises
        ------
        ClientError
            raised if user is not granted for `Can manage JDBC database drivers` feature

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> driver = dr.DataDriver.get('5ad08a1889453d0001ea7c5c')
            >>> driver.canonical_name
            'PostgreSQL'
            >>> driver.update(canonical_name='postgres')
            >>> driver.canonical_name
            'postgres'
        """
        payload = {
            "className": class_name or self.class_name,
            "canonicalName": canonical_name or self.canonical_name,
        }
        r_data = self._client.patch("{}{}/".format(self._path, self.id), data=payload).json()
        self.class_name = r_data["className"]
        self.canonical_name = r_data["canonicalName"]

    def delete(self):
        """
        Removes the driver. Only available to admin users.

        Raises
        ------
        ClientError
            raised if user is not granted for `Can manage JDBC database drivers` feature
        """
        self._client.delete("{}{}/".format(self._path, self.id))

    @property
    def id(self):
        return self._id

    @property
    def creator(self):
        return self._creator

    @property
    def base_names(self):
        return self._base_names

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}('{}')".format(self.__class__.__name__, self.canonical_name or self.id)
        )
