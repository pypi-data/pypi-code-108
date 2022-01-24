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
from datarobot.models.confusion_chart import ConfusionChartTrafaret
from datarobot.utils.pagination import unpaginate

from ...utils import encode_utf8_if_py2
from ..api_object import APIObject
from .external_scores import DEFAULT_BATCH_SIZE


class ExternalConfusionChart(APIObject):
    """ Confusion chart for the model and prediction dataset with target.

    .. versionadded:: v2.21


    ``ClassMetrics`` is a dict containing the following:

        * ``class_name`` (string) name of the class
        * ``actual_count`` (int) number of times this class is seen in the validation data
        * ``predicted_count`` (int) number of times this class has been predicted for the \
          validation data
        * ``f1`` (float) F1 score
        * ``recall`` (float) recall score
        * ``precision`` (float) precision score
        * ``was_actual_percentages`` (list of dict) one vs all actual percentages in format \
          specified below.
            * ``other_class_name`` (string) the name of the other class
            * ``percentage`` (float) the percentage of the times this class was predicted when is \
              was actually class (from 0 to 1)
        * ``was_predicted_percentages`` (list of dict) one vs all predicted percentages in format \
          specified below.
            * ``other_class_name`` (string) the name of the other class
            * ``percentage`` (float) the percentage of the times this class was actual predicted \
              (from 0 to 1)
        * ``confusion_matrix_one_vs_all`` (list of list) 2d list representing 2x2 one vs all matrix.
            * This represents the True/False Negative/Positive rates as integer for each class. \
              The data structure looks like:
            * ``[ [ True Negative, False Positive ], [ False Negative, True Positive ] ]``

    Attributes
    ----------
    dataset_id: str
        id of the external dataset with target
    model_id: str
        id of the model this confusion chart represents
    raw_data : dict
        All of the raw data for the Confusion Chart
    confusion_matrix : list of list
        The NxN confusion matrix
    classes : list
        The names of each of the classes
    class_metrics : list of dicts
        List of dicts with schema described as ``ClassMetrics`` above.

    """

    _path = "projects/{project_id}/models/{model_id}/datasetConfusionCharts/"
    _single_chart_path = (
        "projects/{project_id}/models/{model_id}/datasetConfusionCharts/{dataset_id}/"
    )
    _metadata_path = (
        "projects/{project_id}/models/{model_id}/datasetConfusionCharts/{dataset_id}/metadata/"
    )
    _converter = t.Dict(
        {t.Key("dataset_id"): String(), t.Key("data"): ConfusionChartTrafaret}
    ).ignore_extra("*")

    def __init__(self, dataset_id, data):
        self.dataset_id = dataset_id
        self.raw_data = data
        self.class_metrics = data["class_metrics"]
        self.confusion_matrix = data["confusion_matrix"]
        self.classes = data["classes"]

    def __repr__(self):
        return encode_utf8_if_py2(
            u"ExternalConfusionChart(dataset_id={}, classes={})".format(
                self.dataset_id, self.classes
            )
        )

    @classmethod
    def list(cls, project_id, model_id, dataset_id=None, offset=0, limit=100):
        """ Retrieve list of the confusion charts for the model.

        Parameters
        ----------
        project_id: str
            id of the project
        model_id: str
            id of the model to retrieve a chart from
        dataset_id: str, optional
            if specified, only confusion chart for this dataset will be retrieved
        offset: int, optional
            this many results will be skipped, default: 0
        limit: int, optional
            at most this many results are returned, default: 100, max 1000.
            To return all results, specify 0

        Returns
        -------
            A list of :py:class:`ExternalConfusionChart <datarobot.ExternalConfusionChart>` objects
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
        """ Retrieve confusion chart for the model and external dataset.

        Parameters
        ----------
        project_id: str
            project id
        model_id: str
            model id
        dataset_id: str
            external dataset id with target

        Returns
        -------
            :py:class:`ExternalConfusionChart <datarobot.ExternalConfusionChart>` object

        """
        if dataset_id is None:
            raise ValueError("dataset_id must be specified")
        url = cls._single_chart_path.format(
            project_id=project_id, model_id=model_id, dataset_id=dataset_id
        )

        confusion_chart = cls._client.get(url).json()
        metadata = cls._get_metadata(
            project_id=project_id, model_id=model_id, dataset_id=dataset_id
        )
        confusion_chart["data"]["classes"] = metadata["classNames"]
        return cls.from_server_data(confusion_chart)

    @classmethod
    def _get_metadata(cls, project_id, model_id, dataset_id):
        """ Retrieve confusion chart metadata.

        Parameters
        ----------
        project_id: str
            project id
        model_id: str
            model id
        dataset_id: str
            external dataset id with target

        Returns
        -------
            metadata : dict
                metadata of the confusion chart

        """
        url = cls._metadata_path.format(
            project_id=project_id, model_id=model_id, dataset_id=dataset_id
        )
        return cls._client.get(url).json()
