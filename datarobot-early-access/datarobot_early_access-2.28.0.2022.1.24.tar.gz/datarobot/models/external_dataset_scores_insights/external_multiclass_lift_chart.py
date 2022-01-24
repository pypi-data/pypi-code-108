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


class ExternalMulticlassLiftChart(APIObject):
    """ Multiclass Lift chart for the model and external dataset with target.
    Available only for Multiclass projects.

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
        id of the external dataset with target
    target_class: str
        target class for the lift chart
    bins: list of dict
        List of dicts with schema described as ``LiftChartBin`` above.
    """

    _path = "projects/{project_id}/models/{model_id}/datasetMulticlassLiftCharts/"

    _converter = (
        t.Dict({t.Key("dataset_id"): String(), t.Key("target_class"): String()})
        .merge(LiftChartBinsTrafaret)
        .ignore_extra("*")
    )

    def __init__(self, dataset_id, target_class, bins):
        self.dataset_id = dataset_id
        self.target_class = target_class
        self.bins = bins

    def __repr__(self):
        return encode_utf8_if_py2(
            u"ExternalMulticlassLiftChart(dataset_id={}, target_class={}, bins={})".format(
                self.dataset_id, self.target_class, self.bins
            )
        )

    @classmethod
    def list(cls, project_id, model_id, dataset_id=None, offset=0, limit=100):
        """ Retrieve list of the multiclass lift charts for the model.
        Parameters
        ----------
        project_id: str
            id of the project
        model_id: str
            id of the model to retrieve a chart from
        dataset_id: str, optional
            if specified, only lift chart for this dataset will be retrieved
        offset: int, optional
            this many results will be skipped, default: 0
        limit: int, optional
            at most this many results are returned, default: 100, max 1000.
            To return all results, specify 0
        Returns
        -------
            A list of :py:class:`ExternalMulticlassLiftChart
            <datarobot.ExternalMulticlassLiftChart>` objects
        """
        url = cls._path.format(project_id=project_id, model_id=model_id)
        params = {"limit": limit, "offset": offset}
        if dataset_id:
            params["datasetId"] = dataset_id
        if limit == 0:  # unlimited results
            params["limit"] = DEFAULT_BATCH_SIZE
            charts_data = unpaginate(url, params, cls._client)
        else:
            charts_data = cls._client.get(url, params=params).json()["data"]

        results = []
        for chart in charts_data:
            for classbin in chart["classBins"]:
                results.append(dict(dataset_id=chart["datasetId"], **classbin))

        return [cls.from_server_data(item) for item in results]

    @classmethod
    def get(cls, project_id, model_id, dataset_id, target_class):
        """ Retrieve multiclass lift chart for the model and external dataset on a specific class.
        Parameters
        ----------
        project_id: str
            project id
        model_id: str
            model id
        dataset_id: str
            external dataset id with target
        target_class: str
            target class for the lift chart
        Returns
        -------
            :py:class:`ExternalMulticlassLiftChart <datarobot.ExternalMulticlassLiftChart>` object
        """
        if dataset_id is None:
            raise ValueError("dataset_id must be specified")
        if target_class is None:
            raise ValueError("target_class must be specified")
        charts = cls.list(project_id, model_id, dataset_id=dataset_id)
        filtered_charts = [x for x in charts if x.target_class == target_class]
        if not filtered_charts:
            raise ClientError("Requested multiclass lift chart does not exist.", 404)
        return filtered_charts[0]
