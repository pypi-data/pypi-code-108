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
from datarobot.errors import ClientError
from datarobot.models.lift_chart import LiftChartBinsTrafaret
from datarobot.utils.pagination import unpaginate

from ...utils import encode_utf8_if_py2
from ..api_object import APIObject
from .external_scores import DEFAULT_BATCH_SIZE


class ExternalLiftChart(APIObject):
    """ Lift chart for the model and prediction dataset with target or actual value column in
    unsupervised case.

    .. versionadded:: v2.21


    ``LiftChartBin`` is a dict containing the following:

        * ``actual`` (float) Sum of actual target values in bin
        * ``predicted`` (float) Sum of predicted target values in bin
        * ``bin_weight`` (float) The weight of the bin. For weighted projects, it is the sum of \
          the weights of the rows in the bin. For unweighted projects, it is the number of rows in \
          the bin.

    Attributes
    ----------
    dataset_id: str
        id of the prediction dataset with target or actual value column for unsupervised case
    bins: list of dict
        List of dicts with schema described as ``LiftChartBin`` above.

    """

    _path = "projects/{project_id}/models/{model_id}/datasetLiftCharts/"

    _converter = (
        t.Dict({t.Key("dataset_id"): String()}).merge(LiftChartBinsTrafaret).ignore_extra("*")
    )

    def __init__(self, dataset_id, bins):
        self.dataset_id = dataset_id
        self.bins = bins

    def __repr__(self):
        return encode_utf8_if_py2(
            u"ExternalLiftChart(dataset_id={}, bins={})".format(self.dataset_id, self.bins)
        )

    @classmethod
    def list(cls, project_id, model_id, dataset_id=None, offset=0, limit=100):
        """ Retrieve list of the lift charts for the model.

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
            A list of :py:class:`ExternalLiftChart <datarobot.ExternalLiftChart>` objects
        """
        url = cls._path.format(project_id=project_id, model_id=model_id)
        params = {"limit": limit, "offset": offset}
        if dataset_id:
            params["datasetId"] = dataset_id
        if limit == 0:  # unlimited results
            params["limit"] = DEFAULT_BATCH_SIZE
            return [cls.from_server_data(entry) for entry in unpaginate(url, params, cls._client)]
        r_data = cls._client.get(url, params=params).json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def get(cls, project_id, model_id, dataset_id):
        """ Retrieve lift chart for the model and prediction dataset.

        Parameters
        ----------
        project_id: str
            project id
        model_id: str
            model id
        dataset_id: str
            prediction dataset id with target or actual value column for unsupervised case

        Returns
        -------
            :py:class:`ExternalLiftChart <datarobot.ExternalLiftChart>` object

        """
        # always should return <=1 chart
        if dataset_id is None:
            raise ValueError("dataset_id must be specified")
        charts = cls.list(project_id, model_id, dataset_id=dataset_id)
        if not charts:
            raise ClientError("Requested lift chart does not exist.", 404)
        return charts[0]
