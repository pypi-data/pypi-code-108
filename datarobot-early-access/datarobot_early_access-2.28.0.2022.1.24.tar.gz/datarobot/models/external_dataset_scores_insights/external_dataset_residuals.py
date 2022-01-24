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
from datarobot.errors import ClientError
from datarobot.models.api_object import APIObject
from datarobot.models.residuals import ResidualsTrafaret
from datarobot.utils import encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate

from .external_scores import DEFAULT_BATCH_SIZE


class ExternalResidualsChart(APIObject):
    """ Residual analysis dataset chart data for model .
    This data is calculated over a randomly downsampled subset of the source data
    (capped at 1000 rows).

    versionadded:: v2.21

    Notes
    -----

    ``ResidualsChartRow`` is a list of floats and ints containing the following:
        * Element 0 (float) is the actual target value for the source data row.
        * Element 1 (float) is the predicted target value for that row.
        * Element 2 (float) is the error rate of predicted - actual and is optional.
        * Element 3 (int) is the row number in the source dataset from which the values
          were selected and is optional.

    Attributes
    ----------
    data : list
        List of lists with schema described as ``ResidualsChartRow`` above.
    coefficient_of_determination : float
        The r-squared value for the downsampled dataset
    residual_mean : float
        The arithmetic mean of the residual (predicted value minus actual value)
    dataset_id : str
        ID of the dataset this chart belongs
    standard_deviation : float
        standard deviation of residual values
    """

    _converter = (
        t.Dict(
            {
                t.Key("dataset_id"): String,
                t.Key("data"): t.List(t.Tuple(t.Float, t.Float, t.Float, Int | t.Null)),
            }
        )
        .merge(ResidualsTrafaret)
        .ignore_extra("*")
    )

    _path = "projects/{}/models/{}/datasetResidualsCharts/"

    def __init__(
        self, dataset_id, residual_mean, coefficient_of_determination, standard_deviation, data
    ):
        self.dataset_id = dataset_id
        self.residual_mean = residual_mean
        self.coefficient_of_determination = coefficient_of_determination
        self.standard_deviation = standard_deviation
        self.data = data

    @classmethod
    def list(cls, project_id, model_id, dataset_id=None, offset=0, limit=100):
        """ Retrieve list of residual charts for the model.

        Parameters
        ----------
        project_id: str
            id of the project
        model_id: str
            if specified, only lift chart for this model will be retrieved
        dataset_id: str, optional
            if specified, only lift chart for this dataset will be retrieved
        offset: int, optional
            this many results will be skipped, default: 0
        limit: int, optional
            at most this many results are returned, default: 100, max 1000.
            To return all results, specify 0

        Returns
        -------
            A list of :py:class:`ExternalResidualsChart <datarobot.ExternalResidualsChart>` objects
        """
        url = cls._path.format(project_id, model_id)
        params = {"offset": offset, "limit": limit}
        if dataset_id:
            params["datasetId"] = dataset_id
        if limit == 0:  # unlimited results
            params["limit"] = DEFAULT_BATCH_SIZE
            return [cls.from_server_data(entry) for entry in unpaginate(url, params, cls._client)]
        return [cls.from_server_data(i) for i in cls._client.get(url, params=params).json()["data"]]

    @classmethod
    def get(cls, project_id, model_id, dataset_id):
        """ Retrieve residual chart for the model and prediction dataset.

        Parameters
        ----------
        project_id: str
            project id
        model_id: str
            model id
        dataset_id: str
            prediction dataset id

        Returns
        -------
            :py:class:`ExternalResidualsChart <datarobot.ExternalResidualsChart>` object

        """
        resp = cls.list(project_id, model_id, dataset_id=dataset_id, offset=0, limit=1)
        if not resp:
            raise ClientError("Requested residual chart does not exist.", 404)
        return resp[0]

    def __repr__(self):
        return encode_utf8_if_py2(u"ExternalResidualChart({})".format(self.dataset_id))
