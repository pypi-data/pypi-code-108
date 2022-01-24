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
import warnings

import trafaret as t

from datarobot._compat import String
from datarobot.utils import from_api

from ..errors import InvalidRatingTableWarning
from ..utils import encode_utf8_if_py2, get_id_from_response, recognize_sourcedata
from .api_object import APIObject


class RatingTable(APIObject):
    """ Interface to modify and download rating tables.

    Attributes
    ----------
    id : str
        The id of the rating table.
    project_id : str
        The id of the project this rating table belongs to.
    rating_table_name : str
        The name of the rating table.
    original_filename : str
        The name of the file used to create the rating table.
    parent_model_id : str
        The model id of the model the rating table was validated against.
    model_id : str
        The model id of the model that was created from the rating table.
        Can be None if a model has not been created from the rating table.
    model_job_id : str
        The id of the job to create a model from this rating table.
        Can be None if a model has not been created from the rating table.
    validation_job_id : str
        The id of the created job to validate the rating table.
        Can be None if the rating table has not been validated.
    validation_error : str
        Contains a description of any errors caused during validation.
    """

    _converter = t.Dict(
        {
            t.Key("id"): String,
            t.Key("project_id"): String,
            t.Key("rating_table_name", optional=True): String,
            t.Key("original_filename", optional=True): String,
            t.Key("parent_model_id", optional=True): String,
            t.Key("model_id", optional=True): String,
            t.Key("model_job_id", optional=True): String,
            t.Key("validation_job_id", optional=True): String,
            t.Key("validation_error", optional=True): String(allow_blank=True),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id,
        rating_table_name,
        original_filename,
        project_id,
        parent_model_id,
        model_id=None,
        model_job_id=None,
        validation_job_id=None,
        validation_error=None,
    ):
        self.id = id
        self.rating_table_name = rating_table_name
        self.original_filename = original_filename
        self.project_id = project_id
        self.parent_model_id = parent_model_id
        self.model_id = model_id
        self.model_job_id = model_job_id
        self.validation_job_id = validation_job_id
        self.validation_error = validation_error

    @classmethod
    def from_server_data(cls, data, should_warn=True, keep_attrs=None):
        """
        Instantiate an object of this class using the data directly from the server,
        meaning that the keys may have the wrong camel casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        should_warn : bool
            Whether or not to issue a warning if an invalid rating table is being retrieved.
        """
        case_converted = from_api(data, keep_attrs=keep_attrs)
        if should_warn:
            cls._warn_on_validation_error(case_converted["validation_error"])
        return cls.from_data(case_converted)

    def __repr__(self):
        return encode_utf8_if_py2(u"{}({})".format(type(self).__name__, self.rating_table_name))

    @staticmethod
    def _warn_on_validation_error(validation_error):
        if validation_error != "":
            warnings.warn(
                u"The retrieved rating table was invalid, "
                u"validation error: {}".format(validation_error),
                InvalidRatingTableWarning,
                stacklevel=6,
            )

    @classmethod
    def get(cls, project_id, rating_table_id):
        """Retrieve a single rating table

        Parameters
        ----------
        project_id : str
            The ID of the project the rating table is associated with.
        rating_table_id : str
            The ID of the rating table

        Returns
        -------
        rating_table : RatingTable
            The queried instance
        """
        path = "projects/{}/ratingTables/{}/".format(project_id, rating_table_id)
        rating_table = cls.from_location(path)
        return rating_table

    @classmethod
    def create(
        cls, project_id, parent_model_id, filename, rating_table_name="Uploaded Rating Table"
    ):
        """
        Uploads and validates a new rating table CSV

        Parameters
        ----------
        project_id : str
            id of the project the rating table belongs to
        parent_model_id : str
            id of the model for which this rating table should be validated against
        filename : str
            The path of the CSV file containing the modified rating table.
        rating_table_name : str, optional
            A human friendly name for the new rating table. The string may be
            truncated and a suffix may be added to maintain unique names of all
            rating tables.

        Returns
        -------
        job: Job
            an instance of created async job

        Raises
        ------
        InputNotUnderstoodError
            Raised if `filename` isn't one of supported types.
        ClientError (400)
            Raised if `parent_model_id` is invalid.
        """
        from .job import Job

        form_data = {
            "parent_model_id": parent_model_id,
            "rating_table_name": rating_table_name,
        }
        path = "projects/{}/ratingTables/".format(project_id)

        default_fname = "rating_table.csv"
        filesource_kwargs = recognize_sourcedata(filename, default_fname)
        response = cls._client.build_request_with_file(
            url=path,
            form_data=form_data,
            method="post",
            file_field_name="ratingTableFile",
            **filesource_kwargs
        )
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    def download(self, filepath):
        """
        Download a csv file containing the contents of this rating table

        Parameters
        ----------
        filepath : str
            The path at which to save the rating table file.
        """
        path = "projects/{}/ratingTables/{}/file".format(self.project_id, self.id)
        response = self._client.get(path)
        with open(filepath, mode="wb") as out_file:
            out_file.write(response.content)

    def rename(self, rating_table_name):
        """
        Renames a rating table to a different name.

        Parameters
        ----------
        rating_table_name : str
            The new name to rename the rating table to.
        """
        path = "projects/{}/ratingTables/{}/".format(self.project_id, self.id)
        response = self._client.patch(path, data={"ratingTableName": rating_table_name})
        updated_rating_table = self.from_server_data(response.json())
        self.rating_table_name = updated_rating_table.rating_table_name

    def create_model(self):
        """
        Creates a new model from this rating table record. This rating table
        must not already be associated with a model and must be valid.

        Returns
        -------
        job: Job
            an instance of created async job

        Raises
        ------
        ClientError (422)
            Raised if creating model from a RatingTable that failed validation
        JobAlreadyRequested
            Raised if creating model from a RatingTable that is already
            associated with a RatingTableModel
        """
        from .model import RatingTableModel

        return RatingTableModel.create_from_rating_table(self.project_id, self.id)
