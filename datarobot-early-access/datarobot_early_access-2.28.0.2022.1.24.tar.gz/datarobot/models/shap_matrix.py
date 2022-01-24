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
import pandas as pd
import six
import trafaret as t

from datarobot import errors
from datarobot._compat import String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2, get_id_from_response
from datarobot.utils.pagination import unpaginate


class ShapMatrix(APIObject):
    """
    Represents SHAP based prediction explanations and provides access to score values.

    Attributes
    ----------
    project_id : str
        id of the project the model belongs to
    shap_matrix_id : str
        id of the generated SHAP matrix
    model_id : str
        id of the model used to
    dataset_id : str
         id of the prediction dataset SHAP values were computed for

    Examples
    --------
    .. code-block:: python

        import datarobot as dr

        # request SHAP matrix calculation
        shap_matrix_job = dr.ShapMatrix.create(project_id, model_id, dataset_id)
        shap_matrix = shap_matrix_job.get_result_when_complete()

        # list available SHAP matrices
        shap_matrices = dr.ShapMatrix.list(project_id)
        shap_matrix = shap_matrices[0]

        # get SHAP matrix as dataframe
        shap_matrix_values = shap_matrix.get_as_dataframe()
    """

    _path = "projects/{}/shapMatrices/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("project_id"): String(),
            t.Key("model_id"): String(),
            t.Key("dataset_id"): String(),
        }
    ).allow_extra("*")

    def __init__(self, project_id, id, model_id=None, dataset_id=None):
        self.project_id = project_id
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.id = id

    def __repr__(self):
        template = u"{}(id={!r}, project_id={!r}, model_id={!r}, dataset_id={!r})"
        return encode_utf8_if_py2(
            template.format(
                type(self).__name__, self.id, self.project_id, self.model_id, self.dataset_id,
            )
        )

    @classmethod
    def create(cls, project_id, model_id, dataset_id):
        """ Calculate SHAP based prediction explanations against previously uploaded dataset.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for which prediction explanations are requested
        dataset_id : str
            id of the prediction dataset for which prediction explanations are requested (as
            uploaded from Project.upload_dataset)

        Returns
        -------
        job : ShapMatrixJob
            The job computing the SHAP based prediction explanations

        Raises
        ------
        ClientError
            If the server responded with 4xx status. Possible reasons are project, model or dataset
            don't exist, user is not allowed or model doesn't support SHAP based prediction
            explanations
        ServerError
            If the server responded with 5xx status
        """
        data = {"model_id": model_id, "dataset_id": dataset_id}
        url = "projects/{}/shapMatrices/".format(project_id)
        response = cls._client.post(url, data=data)
        job_id = get_id_from_response(response)
        from .shap_matrix_job import ShapMatrixJob

        return ShapMatrixJob.get(
            project_id=project_id, job_id=job_id, model_id=model_id, dataset_id=dataset_id
        )

    @classmethod
    def from_location(cls, location, model_id=None, dataset_id=None):
        head, tail = location.split("/shapMatrices/", 1)
        project_id, id = head.split("/")[-1], tail.split("/")[0]
        return cls(project_id=project_id, id=id, model_id=model_id, dataset_id=dataset_id)

    @classmethod
    def list(cls, project_id):
        """
        Fetch all the computed SHAP prediction explanations for a project.

        Parameters
        ----------
        project_id : str
            id of the project

        Returns
        -------
        List of ShapMatrix
            A list of :py:class:`ShapMatrix <datarobot.models.ShapMatrix>` objects

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        data = unpaginate(
            initial_url=cls._path.format(project_id), initial_params=None, client=cls._client
        )
        result = [cls.from_server_data(item) for item in data]
        return result

    @classmethod
    def get(cls, project_id, id):
        """
        Retrieve the specific SHAP matrix.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        id : str
            id of the SHAP matrix

        Returns
        -------
        :py:class:`ShapMatrix <datarobot.models.ShapMatrix>` object representing specified record
        """
        return cls(project_id=project_id, id=id)

    def get_as_dataframe(self):
        """
        Retrieve SHAP matrix values as dataframe.

        Returns
        -------
        dataframe : pandas.DataFrame
            A dataframe with SHAP scores

        Raises
        ------
        datarobot.dse.errors.ClientError
            if the server responded with 4xx status.
        datarobot.dse.errors.ServerError
            if the server responded with 5xx status.
        """
        path = self._path.format(self.project_id) + "{}/".format(self.id)
        resp = self._client.get(path, headers={"Accept": "text/csv"}, stream=True)
        if resp.status_code == 200:
            content = resp.content.decode("utf-8")
            return pd.read_csv(six.StringIO(content), index_col=0, encoding="utf-8")
        else:
            raise errors.ServerError(
                "Server returned unknown status code: {}".format(resp.status_code),
                resp.status_code,
            )
