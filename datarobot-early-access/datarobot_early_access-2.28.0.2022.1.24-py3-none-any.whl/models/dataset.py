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
from collections import namedtuple
import os

import dateutil
from pandas import DataFrame  # noqa F401
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.models.credential import CredentialDataSchema
from datarobot.models.feature import DatasetFeature
from datarobot.models.featurelist import DatasetFeaturelist
from datarobot.models.project import Project
from datarobot.utils import dataframe_to_buffer, encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate
from datarobot.utils.sourcedata import list_of_records_to_buffer
from datarobot.utils.waiters import wait_for_async_resolution

from ..enums import DEFAULT_MAX_WAIT, DEFAULT_TIMEOUT

ProjectLocation = namedtuple("ProjectLocation", ["url", "id"])

FeatureTypeCount = namedtuple("FeatureTypeCount", ["count", "feature_type"])


_base_dataset_schema = t.Dict(
    {
        t.Key("dataset_id"): String,
        t.Key("version_id"): String,
        t.Key("name"): String,
        t.Key("categories"): t.List(String),
        t.Key("creation_date") >> "created_at": t.Call(lambda s: dateutil.parser.parse(s)),
        t.Key("created_by"): String,
        t.Key("data_persisted", optional=True): t.Bool,
        t.Key("is_data_engine_eligible"): t.Bool,
        t.Key("is_latest_version"): t.Bool,
        t.Key("is_snapshot"): t.Bool,
        t.Key("dataset_size", optional=True) >> "size": Int,
        t.Key("row_count", optional=True): Int,
        t.Key("processing_state"): String,
    }
)


class Dataset(APIObject):
    """ Represents a Dataset returned from the api/v2/datasets/ endpoints.

    Attributes
    ----------
    id: string
        The ID of this dataset
    name: string
        The name of this dataset in the catalog
    is_latest_version: bool
        Whether this dataset version is the latest version
        of this dataset
    version_id: string
        The object ID of the catalog_version the dataset belongs to
    categories: list(string)
        An array of strings describing the intended use of the dataset. The
        supported options are "TRAINING" and "PREDICTION".
    created_at: string
        The date when the dataset was created
    created_by: string
        Username of the user who created the dataset
    is_snapshot: bool
        Whether the dataset version is an immutable snapshot of data
        which has previously been retrieved and saved to Data_robot
    data_persisted: bool, optional
        If true, user is allowed to view extended data profile
        (which includes data statistics like min/max/median/mean, histogram, etc.) and download
        data. If false, download is not allowed and only the data schema (feature names and types)
        will be available.
    is_data_engine_eligible: bool
        Whether this dataset can be
        a data source of a data engine query.
    processing_state: string
        Current ingestion process state of
        the dataset
    row_count: int, optional
        The number of rows in the dataset.
    size: int, optional
        The size of the dataset as a CSV in bytes.
    """

    _converter = _base_dataset_schema.allow_extra("*")
    _path = "datasets/"

    def __init__(
        self,
        dataset_id,
        version_id,
        name,
        categories,
        created_at,
        created_by,
        is_data_engine_eligible,
        is_latest_version,
        is_snapshot,
        processing_state,
        data_persisted=None,
        size=None,
        row_count=None,
    ):
        self.id = dataset_id
        self.version_id = version_id
        self.name = name
        self.data_persisted = data_persisted
        self.categories = categories[:]
        self.created_at = created_at
        self.created_by = created_by
        self.is_data_engine_eligible = is_data_engine_eligible
        self.is_latest_version = is_latest_version
        self.is_snapshot = is_snapshot
        self.size = size
        self.row_count = row_count
        self.processing_state = processing_state

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(name={!r}, id={!r})".format(self.__class__.__name__, self.name, self.id)
        )

    @classmethod
    def create_from_file(
        cls,
        file_path=None,
        filelike=None,
        categories=None,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset from a file. Returns when the dataset has
        been successfully uploaded and processed.

        Warning: This function does not clean up it's open files. If you pass a filelike, you are
        responsible for closing it. If you pass a file_path, this will create a file object from
        the file_path but will not close it.

        Parameters
        ----------
        file_path: string, optional
            The path to the file. This will create a file object pointing to that file but will
            not close it.
        filelike: file, optional
            An open and readable file object.
        categories: list[string], optional
            An array of strings describing the intended use of the dataset. The
            current supported options are "TRAINING" and "PREDICTION".
        read_timeout: int, optional
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            A fully armed and operational Dataset
        """
        _assert_single_parameter(("filelike", "file_path"), file_path, filelike)

        upload_url = "{}fromFile/".format(cls._path)
        default_fname = "data.csv"
        if file_path:
            fname = os.path.basename(file_path)
            response = cls._client.build_request_with_file(
                fname=fname,
                file_path=file_path,
                url=upload_url,
                read_timeout=read_timeout,
                method="post",
            )
        else:
            try:
                fname = filelike.name
            except AttributeError:
                fname = default_fname
            response = cls._client.build_request_with_file(
                fname=fname,
                filelike=filelike,
                url=upload_url,
                read_timeout=read_timeout,
                method="post",
            )

        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        dataset = cls.from_location(new_dataset_location)
        if categories:
            dataset.modify(categories=categories)
        return dataset

    @classmethod
    def create_from_in_memory_data(
        cls,
        data_frame=None,
        records=None,
        categories=None,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset from in-memory data. Returns when the dataset has
        been successfully uploaded and processed.

        The data can be either a pandas DataFrame or a list of dictionaries with identical keys.

        Parameters
        ----------
        data_frame: DataFrame, optional
            The data frame to upload
        records: list[dict], optional
            A list of dictionaries with identical keys to upload
        categories: list[string], optional
            An array of strings describing the intended use of the dataset. The
            current supported options are "TRAINING" and "PREDICTION".
        read_timeout: int, optional
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            The Dataset created from the uploaded data
        """
        _assert_single_parameter(("data_frame", "records"), data_frame, records)
        if data_frame is not None:
            buff = dataframe_to_buffer(data_frame)
        else:
            buff = list_of_records_to_buffer(records)
        return cls.create_from_file(
            filelike=buff, categories=categories, read_timeout=read_timeout, max_wait=max_wait,
        )

    @classmethod
    def create_from_url(
        cls,
        url,
        do_snapshot=None,
        persist_data_after_ingestion=None,
        categories=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset from data stored at a url.
        Returns when the dataset has been successfully uploaded and processed.

        Parameters
        ----------
        url: string
            The URL to use as the source of data for the dataset being created.
        do_snapshot: bool, optional
            If unset, uses the server default: True.
            If true, creates a snapshot dataset; if
            false, creates a remote dataset. Creating snapshots from non-file sources may be
            disabled by the permission, `Disable AI Catalog Snapshots`.
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
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            The Dataset created from the uploaded data
        """
        base_data = {
            "url": url,
            "do_snapshot": do_snapshot,
            "persist_data_after_ingestion": persist_data_after_ingestion,
            "categories": categories,
        }
        data = _remove_empty_params(base_data)
        upload_url = "{}fromURL/".format(cls._path)
        response = cls._client.post(upload_url, data=data)

        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        return cls.from_location(new_dataset_location)

    @classmethod
    def create_from_data_source(
        cls,
        data_source_id,
        username=None,
        password=None,
        do_snapshot=None,
        persist_data_after_ingestion=None,
        categories=None,
        credential_id=None,
        use_kerberos=None,
        credential_data=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset from data stored at a DataSource.
        Returns when the dataset has been successfully uploaded and processed.

        .. versionadded:: v2.22

        Parameters
        ----------
        data_source_id: string
            The ID of the DataSource to use as the source of data.
        username: string, optional
            The username for database authentication.
        password: string, optional
            The password (in cleartext) for database authentication. The password
            will be encrypted on the server side in scope of HTTP request and never saved or stored.
        do_snapshot: bool, optional
            If unset, uses the server default: True.
            If true, creates a snapshot dataset; if
            false, creates a remote dataset. Creating snapshots from non-file sources requires may
            be disabled by the permission, `Disable AI Catalog Snapshots`.
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
        credential_data: dict, optional
            The credentials to authenticate with the database, to use instead of user/password or
            credential ID.
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful


        Returns
        -------
        response: Dataset
            The Dataset created from the uploaded data
        """
        base_data = {
            "data_source_id": data_source_id,
            "user": username,
            "password": password,
            "do_snapshot": do_snapshot,
            "persist_data_after_ingestion": persist_data_after_ingestion,
            "categories": categories,
            "credential_id": credential_id,
            "use_kerberos": use_kerberos,
            "credential_data": credential_data,
        }
        data = _remove_empty_params(base_data)

        if "credential_data" in data:
            data["credential_data"] = CredentialDataSchema(data["credential_data"])

        upload_url = "{}fromDataSource/".format(cls._path)
        response = cls._client.post(upload_url, data=data)

        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        return cls.from_location(new_dataset_location)

    @classmethod
    def create_from_query_generator(
        cls, generator_id, dataset_id=None, dataset_version_id=None, max_wait=DEFAULT_MAX_WAIT
    ):
        """
        A blocking call that creates a new Dataset from the query generator.
        Returns when the dataset has been successfully processed. If optional
        parameters are not specified the query is applied to the dataset_id
        and dataset_version_id stored in the query generator. If specified they
        will override the stored dataset_id/dataset_version_id, e.g. to prep a
        prediction dataset.

        Parameters
        ----------
        generator_id: str
            The id of the query generator to use.
        dataset_id: str, optional
            The id of the dataset to apply the query to.
        dataset_version_id: str, optional
            The id of the dataset version to apply the query to. If not specified the
            latest version associated with dataset_id (if specified) is used.
        max_wait : int
            optional, the maximum number of seconds to wait before giving up.

        Returns
        -------
        response: Dataset
            The Dataset created from the query generator
        """
        url = "dataEngineWorkspaceStates/fromDataEngineQueryGenerator/"
        base_data = {
            "query_generator_id": generator_id,
            "dataset_id": dataset_id,
            "dataset_version_id": dataset_version_id,
        }
        data = _remove_empty_params(base_data)
        response = cls._client.post(url, data=data)
        workspace_id = response.json()["workspaceStateId"]

        url = "{}fromDataEngineWorkspaceState/".format(cls._path)
        response = cls._client.post(url, data={"workspace_state_id": workspace_id})
        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        return cls.from_location(new_dataset_location)

    @classmethod
    def get(cls, dataset_id):
        """Get information about a dataset.

        Parameters
        ----------
        dataset_id : string
            the id of the dataset

        Returns
        -------
        dataset : Dataset
            the queried dataset
        """

        path = "{}{}/".format(cls._path, dataset_id)
        return cls.from_location(path)

    @classmethod
    def delete(cls, dataset_id):
        """
        Soft deletes a dataset.  You cannot get it or list it or do actions with it, except for
        un-deleting it.

        Parameters
        ----------
        dataset_id: string
            The id of the dataset to mark for deletion

        Returns
        -------
        None
        """
        path = "{}{}/".format(cls._path, dataset_id)
        cls._client.delete(path)

    @classmethod
    def un_delete(cls, dataset_id):
        """
        Un-deletes a previously deleted dataset.  If the dataset was not deleted, nothing happens.

        Parameters
        ----------
        dataset_id: string
            The id of the dataset to un-delete

        Returns
        -------
        None
        """
        path = "{}{}/deleted/".format(cls._path, dataset_id)
        cls._client.patch(path)

    @classmethod
    def list(cls, category=None, filter_failed=None, order_by=None):
        """
        List all datasets a user can view.


        Parameters
        ----------
        category: string, optional
            Optional. If specified, only dataset versions that have the specified category will be
            included in the results. Categories identify the intended use of the dataset; supported
            categories are "TRAINING" and "PREDICTION".

        filter_failed: bool, optional
            If unset, uses the server default: False.
            Whether datasets that failed during import should be excluded from the results.
            If True invalid datasets will be excluded.

        order_by: string, optional
            If unset, uses the server default: "-created".
            Sorting order which will be applied to catalog list, valid options are:
            - "created" -- ascending order by creation datetime;
            - "-created" -- descending order by creation datetime.

        Returns
        -------
        list[Dataset]
            a list of datasets the user can view

        """
        return list(cls.iterate(category=category, order_by=order_by, filter_failed=filter_failed))

    @classmethod
    def iterate(cls, offset=None, limit=None, category=None, order_by=None, filter_failed=None):
        """
        Get an iterator for the requested datasets a user can view.
        This lazily retrieves results. It does not get the next page from the server until the
        current page is exhausted.

        Parameters
        ----------
        offset: int, optional
            If set, this many results will be skipped

        limit: int, optional
            Specifies the size of each page retrieved from the server.  If unset, uses the server
            default.

        category: string, optional
            Optional. If specified, only dataset versions that have the specified category will be
            included in the results. Categories identify the intended use of the dataset; supported
            categories are "TRAINING" and "PREDICTION".

        filter_failed: bool, optional
            If unset, uses the server default: False.
            Whether datasets that failed during import should be excluded from the results.
            If True invalid datasets will be excluded.

        order_by: string, optional
            If unset, uses the server default: "-created".
            Sorting order which will be applied to catalog list, valid options are:
            - "created" -- ascending order by creation datetime;
            - "-created" -- descending order by creation datetime.

        Yields
        -------
        Dataset
            An iterator of the datasets the user can view

        """
        all_params = {
            "offset": offset,
            "limit": limit,
            "category": category,
            "order_by": order_by,
            "filter_failed": filter_failed,
        }
        params = _remove_empty_params(all_params)
        _update_filter_failed(params)

        for dataset_json in unpaginate(cls._path, params, cls._client):
            yield cls.from_server_data(dataset_json)

    def update(self):
        """
        Updates the Dataset attributes in place with the latest information from the server.

        Returns
        -------
        None
        """
        new_dataset = self.get(self.id)
        update_attrs = (
            "name",
            "created_by",
            "created_at",
            "version_id",
            "is_latest_version",
            "is_snapshot",
            "data_persisted",
            "categories",
            "size",
            "row_count",
            "processing_state",
        )
        for attr in update_attrs:
            setattr(self, attr, getattr(new_dataset, attr))

    def modify(self, name=None, categories=None):
        """
        Modifies the Dataset name and/or categories.  Updates the object in place.

        Parameters
        ----------
        name: string, optional
            The new name of the dataset

        categories: list[string], optional
            A list of strings describing the intended use of the
            dataset. The supported options are "TRAINING" and "PREDICTION". If any
            categories were previously specified for the dataset, they will be overwritten.

        Returns
        -------
        None

        """
        if name is None and categories is None:
            return

        url = "{}{}/".format(self._path, self.id)
        params = {"name": name, "categories": categories}
        params = _remove_empty_params(params)

        response = self._client.patch(url, data=params)
        data = response.json()
        self.name = data["name"]
        self.categories = data["categories"]

    def get_details(self):
        """
        Gets the details for this Dataset

        Returns
        -------
        DatasetDetails
        """
        return DatasetDetails.get(self.id)

    def get_all_features(self, order_by=None):
        """
        Get a list of all the features for this dataset.

        Parameters
        ----------
        order_by: string, optional
            If unset, uses the server default: 'name'.
            How the features should be ordered. Can be 'name' or 'featureType'.

        Returns
        -------
        list[DatasetFeature]
        """
        return list(self.iterate_all_features(order_by=order_by))

    def iterate_all_features(self, offset=None, limit=None, order_by=None):
        """
        Get an iterator for the requested features of a dataset.
        This lazily retrieves results. It does not get the next page from the server until the
        current page is exhausted.

        Parameters
        ----------
        offset: int, optional
            If set, this many results will be skipped.

        limit: int, optional
            Specifies the size of each page retrieved from the server.  If unset, uses the server
            default.

        order_by: string, optional
            If unset, uses the server default: 'name'.
            How the features should be ordered. Can be 'name' or 'featureType'.

        Yields
        -------
        DatasetFeature
        """
        all_params = {
            "offset": offset,
            "limit": limit,
            "order_by": order_by,
        }
        params = _remove_empty_params(all_params)

        url = "{}{}/allFeaturesDetails/".format(self._path, self.id)
        for dataset_json in unpaginate(url, params, self._client):
            yield DatasetFeature.from_server_data(dataset_json)

    def get_featurelists(self):
        """
        Get DatasetFeaturelists created on this Dataset

        Returns
        -------
        feature_lists: list[DatasetFeaturelist]
        """
        url = "{}{}/featurelists/".format(self._path, self.id)
        params = {}
        result = unpaginate(url, params, self._client)
        return [DatasetFeaturelist.from_server_data(el) for el in result]

    def create_featurelist(self, name, features):
        """ Create a new dataset featurelist

        Parameters
        ----------
        name : str
            the name of the modeling featurelist to create. Names must be unique within the
            dataset, or the server will return an error.
        features : list of str
            the names of the features to include in the dataset featurelist. Each feature must
            be a dataset feature.

        Returns
        -------
        featurelist : DatasetFeaturelist
            the newly created featurelist

        Examples
        --------
        .. code-block:: python

            dataset = Dataset.get('1234deadbeeffeeddead4321')
            dataset_features = dataset.get_all_features()
            selected_features = [feat.name for feat in dataset_features][:5]  # select first five
            new_flist = dataset.create_featurelist('Simple Features', selected_features)
        """
        url = "{}{}/featurelists/".format(self._path, self.id)

        payload = {"name": name, "features": features}
        response = self._client.post(url, data=payload)
        return DatasetFeaturelist.from_server_data(response.json())

    def get_file(self, file_path=None, filelike=None):
        """
        Retrieves all the originally uploaded data in CSV form.
        Writes it to either the file or a filelike object that can write bytes.

        Only one of file_path or filelike can be provided and it must be provided as a
        keyword argument (i.e. file_path='path-to-write-to'). If a file-like object is
        provided, the user is responsible for closing it when they are done.

        The user must also have permission to download data.

        Parameters
        ----------
        file_path: string, optional
            The destination to write the file to.
        filelike: file, optional
            A file-like object to write to.  The object must be able to write bytes. The user is
            responsible for closing the object

        Returns
        -------
        None
        """
        _assert_single_parameter(("filelike", "file_path"), filelike, file_path)

        response = self._client.get("{}{}/file/".format(self._path, self.id))
        if file_path:
            with open(file_path, "wb") as f:
                f.write(response.content)
        if filelike:
            filelike.write(response.content)

    def get_projects(self):
        """
        Retrieves the Dataset's projects as ProjectLocation named tuples.

        Returns
        -------
        locations: list[ProjectLocation]
        """
        url = "{}{}/projects/".format(self._path, self.id)
        return [ProjectLocation(**kwargs) for kwargs in unpaginate(url, None, self._client)]

    def create_project(
        self,
        project_name=None,
        user=None,
        password=None,
        credential_id=None,
        use_kerberos=None,
        credential_data=None,
    ):
        """
        Create a :class:`datarobot.models.Project` from this dataset

        Parameters
        ----------
        project_name: string, optional
            The name of the project to be created.
            If not specified, will be "Untitled Project" for database connections, otherwise
            the project name will be based on the file used.
        user: string, optional
            The username for database authentication.
        password: string, optional
            The password (in cleartext) for database authentication. The password
            will be encrypted on the server side in scope of HTTP request and never saved or stored
        credential_id: string, optional
            The ID of the set of credentials to use instead of user and password.
        use_kerberos: bool, optional
            Server default is False.
            If true, use kerberos authentication for database authentication.
        credential_data: dict, optional
            The credentials to authenticate with the database, to use instead of user/password or
            credential ID.

        Returns
        -------
        Project
        """
        return Project.create_from_dataset(
            self.id,
            dataset_version_id=self.version_id,
            project_name=project_name,
            user=user,
            password=password,
            credential_id=credential_id,
            use_kerberos=use_kerberos,
            credential_data=credential_data,
        )

    @classmethod
    def create_version_from_file(
        cls,
        dataset_id,
        file_path=None,
        filelike=None,
        categories=None,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset version from a file. Returns when the new dataset
        version has been successfully uploaded and processed.

        Warning: This function does not clean up it's open files. If you pass a filelike, you are
        responsible for closing it. If you pass a file_path, this will create a file object from
        the file_path but will not close it.

        .. versionadded:: v2.23

        Parameters
        ----------
        dataset_id: string
            The ID of the dataset for which new version to be created
        file_path: string, optional
            The path to the file. This will create a file object pointing to that file but will
            not close it.
        filelike: file, optional
            An open and readable file object.
        categories: list[string], optional
            An array of strings describing the intended use of the dataset. The
            current supported options are "TRAINING" and "PREDICTION".
        read_timeout: int, optional
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            A fully armed and operational Dataset version
        """
        _assert_single_parameter(("filelike", "file_path"), file_path, filelike)

        upload_url = "{}{}/versions/fromFile/".format(cls._path, dataset_id)
        default_fname = "data.csv"
        if file_path:
            fname = os.path.basename(file_path)
            response = cls._client.build_request_with_file(
                fname=fname,
                file_path=file_path,
                url=upload_url,
                read_timeout=read_timeout,
                method="post",
            )
        else:
            try:
                fname = filelike.name
            except AttributeError:
                fname = default_fname
            response = cls._client.build_request_with_file(
                fname=fname,
                filelike=filelike,
                url=upload_url,
                read_timeout=read_timeout,
                method="post",
            )

        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        dataset = cls.from_location(new_dataset_location)
        if categories:
            dataset.modify(categories=categories)
        return dataset

    @classmethod
    def create_version_from_in_memory_data(
        cls,
        dataset_id,
        data_frame=None,
        records=None,
        categories=None,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset version for a dataset from in-memory data.
        Returns when the dataset has been successfully uploaded and processed.

        The data can be either a pandas DataFrame or a list of dictionaries with identical keys.

         .. versionadded:: v2.23

        Parameters
        ----------
        dataset_id: string
            The ID of the dataset for which new version to be created
        data_frame: DataFrame, optional
            The data frame to upload
        records: list[dict], optional
            A list of dictionaries with identical keys to upload
        categories: list[string], optional
            An array of strings describing the intended use of the dataset. The
            current supported options are "TRAINING" and "PREDICTION".
        read_timeout: int, optional
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            The Dataset version created from the uploaded data
        """
        _assert_single_parameter(("data_frame", "records"), data_frame, records)
        if data_frame is not None:
            buff = dataframe_to_buffer(data_frame)
        else:
            buff = list_of_records_to_buffer(records)
        return cls.create_version_from_file(
            dataset_id,
            filelike=buff,
            categories=categories,
            read_timeout=read_timeout,
            max_wait=max_wait,
        )

    @classmethod
    def create_version_from_url(cls, dataset_id, url, categories=None, max_wait=DEFAULT_MAX_WAIT):
        """
        A blocking call that creates a new Dataset from data stored at a url for a given dataset.
        Returns when the dataset has been successfully uploaded and processed.

        .. versionadded:: v2.23

        Parameters
        ----------
        dataset_id: string
            The ID of the dataset for which new version to be created
        url: string
            The URL to use as the source of data for the dataset being created.
        categories: list[string], optional
            An array of strings describing the intended use of the dataset. The
            current supported options are "TRAINING" and "PREDICTION".
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            The Dataset version created from the uploaded data
        """
        base_data = {
            "url": url,
            "categories": categories,
        }
        data = _remove_empty_params(base_data)
        upload_url = "{}{}/versions/fromURL/".format(cls._path, dataset_id)
        response = cls._client.post(upload_url, data=data)

        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        return cls.from_location(new_dataset_location)

    @classmethod
    def create_version_from_data_source(
        cls,
        dataset_id,
        data_source_id,
        username=None,
        password=None,
        categories=None,
        credential_id=None,
        use_kerberos=None,
        credential_data=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        A blocking call that creates a new Dataset from data stored at a DataSource.
        Returns when the dataset has been successfully uploaded and processed.

        .. versionadded:: v2.23

        Parameters
        ----------
        dataset_id: string
            The ID of the dataset for which new version to be created
        data_source_id: string
            The ID of the DataSource to use as the source of data.
        username: string, optional
            The username for database authentication.
        password: string, optional
            The password (in cleartext) for database authentication. The password
            will be encrypted on the server side in scope of HTTP request and never saved or stored.
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
        credential_data: dict, optional
            The credentials to authenticate with the database, to use instead of user/password or
            credential ID.
        max_wait: int, optional
            Time in seconds after which project creation is considered unsuccessful

        Returns
        -------
        response: Dataset
            The Dataset version created from the uploaded data
        """
        base_data = {
            "data_source_id": data_source_id,
            "user": username,
            "password": password,
            "categories": categories,
            "credential_id": credential_id,
            "use_kerberos": use_kerberos,
            "credential_data": credential_data,
        }
        data = _remove_empty_params(base_data)

        if "credential_data" in data:
            data["credential_data"] = CredentialDataSchema(data["credential_data"])

        upload_url = "{}{}/versions/fromDataSource/".format(cls._path, dataset_id)
        response = cls._client.post(upload_url, data=data)

        new_dataset_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        return cls.from_location(new_dataset_location)


def _assert_single_parameter(param_names, *params):
    if sum(param is not None for param in params) != 1:
        raise TypeError("One and only parameter of: {}".format(param_names))


def _remove_empty_params(params_dict):
    return {key: value for key, value in params_dict.items() if value is not None}


def _update_filter_failed(query_params):
    try:
        key = "filter_failed"
        query_params[key] = str(query_params[key]).lower()
    except KeyError:
        pass


def _safe_merge(first, second):
    # type: (t.Dict, t.Dict) -> t.Dict

    second_names = {el.name for el in second.keys}
    if any(el.name in second_names for el in first.keys):
        raise ValueError("Duplicate keys detected")

    return first.merge(second)


class DatasetDetails(APIObject):
    """ Represents a detailed view of a Dataset. The `to_dataset` method creates a Dataset
    from this details view.

    Attributes
    ----------
    dataset_id: string
        The ID of this dataset
    name: string
        The name of this dataset in the catalog
    is_latest_version: bool
        Whether this dataset version is the latest version
        of this dataset
    version_id: string
        The object ID of the catalog_version the dataset belongs to
    categories: list(string)
        An array of strings describing the intended use of the dataset. The
        supported options are "TRAINING" and "PREDICTION".
    created_at: string
        The date when the dataset was created
    created_by: string
        Username of the user who created the dataset
    is_snapshot: bool
        Whether the dataset version is an immutable snapshot of data
        which has previously been retrieved and saved to Data_robot
    data_persisted: bool, optional
        If true, user is allowed to view extended data profile
        (which includes data statistics like min/max/median/mean, histogram, etc.) and download
        data. If false, download is not allowed and only the data schema (feature names and types)
        will be available.
    is_data_engine_eligible: bool
        Whether this dataset can be
        a data source of a data engine query.
    processing_state: string
        Current ingestion process state of
        the dataset
    row_count: int, optional
        The number of rows in the dataset.
    size: int, optional
        The size of the dataset as a CSV in bytes.
    data_engine_query_id: string, optional
        ID of the source data engine query
    data_source_id: string, optional
        ID of the datasource used as the source of the dataset
    data_source_type: string
        the type of the datasource that was used as the source of the
        dataset
    description: string, optional
        the description of the dataset
    eda1_modification_date: string, optional
        the ISO 8601 formatted date and time when the EDA1 for
        the dataset was updated
    eda1_modifier_full_name: string, optional
        the user who was the last to update EDA1 for the
        dataset
    error: string
        details of exception raised during ingestion process, if any
    feature_count: int, optional
        total number of features in the dataset
    feature_count_by_type: list[FeatureTypeCount]
        number of features in the dataset grouped by feature type
    last_modification_date: string
        the ISO 8601 formatted date and time when the dataset
        was last modified
    last_modifier_full_name: string
        full name of user who was the last to modify the
        dataset
    tags: list[string]
        list of tags attached to the item
    uri: string
        the uri to datasource like:
        - 'file_name.csv'
        - 'jdbc:DATA_SOURCE_GIVEN_NAME/SCHEMA.TABLE_NAME'
        - 'jdbc:DATA_SOURCE_GIVEN_NAME/<query>' - for `query` based datasources
        - 'https://s3.amazonaws.com/datarobot_test/kickcars-sample-200.csv'
        - etc.
    """

    _extra_fields = t.Dict(
        {
            t.Key("data_engine_query_id", optional=True): String,
            t.Key("data_source_id", optional=True): String,
            t.Key("data_source_type"): String(allow_blank=True),
            t.Key("description", optional=True): String(allow_blank=True),
            t.Key("eda1_modification_date", optional=True): t.Call(
                lambda s: dateutil.parser.parse(s)
            ),
            t.Key("eda1_modifier_full_name", optional=True): String,
            t.Key("error"): String(allow_blank=True),
            t.Key("feature_count", optional=True): Int,
            t.Key("feature_count_by_type", optional=True): t.List(
                t.Call(lambda d: FeatureTypeCount(**d))
            ),
            t.Key("last_modification_date"): t.Call(lambda s: dateutil.parser.parse(s)),
            t.Key("last_modifier_full_name"): String,
            t.Key("tags", optional=True): t.List(String),
            t.Key("uri"): String,
        }
    )

    _converter = _safe_merge(_extra_fields, _base_dataset_schema).allow_extra("*")

    _path = "datasets/"

    def __init__(
        self,
        dataset_id,
        version_id,
        categories,
        created_by,
        created_at,
        data_source_type,
        error,
        is_latest_version,
        is_snapshot,
        is_data_engine_eligible,
        last_modification_date,
        last_modifier_full_name,
        name,
        uri,
        data_persisted=None,
        data_engine_query_id=None,
        data_source_id=None,
        description=None,
        eda1_modification_date=None,
        eda1_modifier_full_name=None,
        feature_count=None,
        feature_count_by_type=None,
        processing_state=None,
        row_count=None,
        size=None,
        tags=None,
    ):
        self.dataset_id = dataset_id
        self.version_id = version_id
        self.categories = categories
        self.created_by = created_by
        self.created_at = created_at
        self.data_source_type = data_source_type
        self.error = error
        self.is_latest_version = is_latest_version
        self.is_snapshot = is_snapshot
        self.is_data_engine_eligible = is_data_engine_eligible
        self.last_modification_date = last_modification_date
        self.last_modifier_full_name = last_modifier_full_name
        self.name = name
        self.uri = uri
        self.data_persisted = data_persisted
        self.data_engine_query_id = data_engine_query_id
        self.data_source_id = data_source_id
        self.description = description
        self.eda1_modification_date = eda1_modification_date
        self.eda1_modifier_full_name = eda1_modifier_full_name
        self.feature_count = feature_count
        self.feature_count_by_type = feature_count_by_type
        self.processing_state = processing_state
        self.row_count = row_count
        self.size = size
        self.tags = tags

    @classmethod
    def get(cls, dataset_id):
        """
        Get details for a Dataset from the server

        Parameters
        ----------
        dataset_id: str
            The id for the Dataset from which to get details

        Returns
        -------
        DatasetDetails
        """
        path = "{}{}/".format(cls._path, dataset_id)
        return cls.from_location(path)

    def to_dataset(self):
        """
        Build a Dataset object from the information in this object

        Returns
        -------
        Dataset
        """
        return Dataset(
            dataset_id=self.dataset_id,
            name=self.name,
            created_at=self.created_at,
            created_by=self.created_by,
            version_id=self.version_id,
            categories=self.categories,
            is_latest_version=self.is_latest_version,
            is_data_engine_eligible=self.is_data_engine_eligible,
            is_snapshot=self.is_snapshot,
            data_persisted=self.data_persisted,
            size=self.size,
            row_count=self.row_count,
            processing_state=self.processing_state,
        )
