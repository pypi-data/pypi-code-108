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
from operator import itemgetter

import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject

from ..enums import AnomalyAssessmentStatus, SOURCE_TYPE
from ..utils import encode_utf8_if_py2, from_api
from ..utils.pagination import unpaginate
from ..utils.waiters import wait_for_async_resolution

DEFAULT_BATCH_SIZE = 1000

RecordMetadataTrafaret = t.Dict(
    {
        t.Key("record_id"): String,
        t.Key("project_id"): String,
        t.Key("model_id"): String,
        t.Key("backtest"): String() | Int,
        t.Key("source"): t.Enum(*SOURCE_TYPE.ALL),
        t.Key("series_id"): String() | t.Null,
    }
)


class BaseAPIObject(APIObject):
    def __init__(self, **record_kwargs):
        self.record_id = record_kwargs["record_id"]
        self.project_id = record_kwargs["project_id"]
        self.model_id = record_kwargs["model_id"]
        self.backtest = record_kwargs["backtest"]
        self.source = record_kwargs["source"]
        self.series_id = record_kwargs["series_id"]

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={}, series_id={}, "
            "backtest={}, source={}, record_id={})".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                self.series_id,
                self.backtest,
                self.source,
                self.record_id,
            )
        )

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        """
        Instantiate an object of this class using the data directly from the server,
        meaning that the keys may have the wrong camel casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        keep_attrs : list
            List of the dotted namespace notations for attributes to keep within the
            object structure even if their values are None
        """
        case_converted = from_api(data, keep_attrs=keep_attrs, keep_null_keys=True)
        return cls.from_data(case_converted)


class AnomalyAssessmentRecord(BaseAPIObject):
    """Object which keeps metadata about anomaly assessment insight for the particular
    subset, backtest and series and the links to proceed to get the anomaly assessment data.

    .. versionadded:: v2.25

    Attributes
    ----------
    record_id: str
        The ID of the record.
    project_id: str
        The ID of the project record belongs to.
    model_id: str
        The ID of the model record belongs to.
    backtest: int or "holdout"
        The backtest of the record.
    source: "training" or "validation"
        The source of the record
    series_id: str or None
        The series id of the record for the multiseries projects. Defined only for the multiseries
        projects.
    status: str
        The status of the insight. One of ``datarobot.enums.AnomalyAssessmentStatus``
    status_details: str
        The explanation of the status.
    start_date: str or None
        See start_date info in `Notes` for more details.
    end_date: str or None
        See end_date info in `Notes` for more details.
    prediction_threshold: float or None
        See prediction_threshold info in `Notes` for more details.
    preview_location: str or None
        See preview_location info in `Notes` for more details.
    latest_explanations_location: str or None
        See latest_explanations_location info in `Notes` for more details.
    delete_location: str
        The URL to delete anomaly assessment record and relevant insight data.

    Notes
    -----

    ``Record`` contains:

    * ``record_id`` : the ID of the record.
    * ``project_id`` : the project ID of the record.
    * ``model_id`` : the model ID of the record.
    * ``backtest`` : the backtest of the record.
    * ``source`` : the source of the record.
    * ``series_id`` : the series id of the record for the multiseries projects.
    * ``status`` : the status of the insight.
    * ``status_details`` : the explanation of the status.
    * ``start_date`` : the ISO-formatted timestamp of the first prediction in the subset. Will be
      None if status is not `AnomalyAssessmentStatus.COMPLETED`.
    * ``end_date`` : the ISO-formatted timestamp of the last prediction in the subset. Will be None
      if status is not `AnomalyAssessmentStatus.COMPLETED`.
    * ``prediction_threshold`` : the threshold, all rows with anomaly scores greater or equal to it
      have shap explanations computed.
      Will be None if status is not `AnomalyAssessmentStatus.COMPLETED`.
    * ``preview_location`` :  URL to retrieve predictions preview for the subset. Will be None if
      status is not `AnomalyAssessmentStatus.COMPLETED`.
    * ``latest_explanations_location`` : the URL to retrieve the latest predictions with
      the shap explanations. Will be None if status is not `AnomalyAssessmentStatus.COMPLETED`.
    * ``delete_location`` : the URL to delete anomaly assessment record and relevant insight data.

    """

    _path = "projects/{project_id}/anomalyAssessmentRecords/"
    _create_path = "projects/{project_id}/models/{model_id}/anomalyAssessmentInitialization/"

    _converter = (
        t.Dict(
            {
                t.Key("status"): t.Enum(*AnomalyAssessmentStatus.ALL),
                t.Key("status_details"): String,
                t.Key("start_date"): String() | t.Null,
                t.Key("end_date"): String() | t.Null,
                t.Key("prediction_threshold"): t.Float | t.Null,
                t.Key("preview_location"): String() | t.Null,
                t.Key("delete_location"): String(),
                t.Key("latest_explanations_location"): String() | t.Null,
            }
        )
        .merge(RecordMetadataTrafaret)
        .ignore_extra("*")
    )

    def __init__(
        self,
        status,
        status_details,
        start_date,
        end_date,
        prediction_threshold,
        preview_location,
        delete_location,
        latest_explanations_location,
        **record_kwargs
    ):
        self.status = status
        self.status_details = status_details
        self.start_date = start_date
        self.end_date = end_date
        self.prediction_threshold = prediction_threshold
        self.preview_location = preview_location
        self.delete_location = delete_location
        self.latest_explanations_location = latest_explanations_location
        super(AnomalyAssessmentRecord, self).__init__(**record_kwargs)

    @classmethod
    def list(
        cls,
        project_id,
        model_id,
        backtest=None,
        source=None,
        series_id=None,
        limit=100,
        offset=0,
        with_data_only=False,
    ):
        """Retrieve the list of the anomaly assessment records for the project and model.
        Output can be filtered and limited.

        Parameters
        ----------
        project_id: str
            The ID of the project record belongs to.
        model_id: str
            The ID of the model record belongs to.
        backtest: int or "holdout"
            The backtest to filter records by.
        source: "training" or "validation"
            The source to filter records by.
        series_id: str, optional
            The series id to filter records by. Can be specified for multiseries projects.
        limit: int, optional
            100 by default. At most this many results are returned.
        offset: int, optional
            This many results will be skipped.
        with_data_only: bool, False by default
            Filter by `status` == AnomalyAssessmentStatus.COMPLETED. If True, records with
            no data or not supported will be omitted.

        Returns
        -------
        AnomalyAssessmentRecord
            The anomaly assessment record.
        """
        params = {"limit": limit, "offset": offset}
        if model_id:
            params["modelId"] = model_id
        if backtest:
            params["backtest"] = backtest
        if source:
            params["source"] = source
        if series_id:
            params["series_id"] = series_id
        url = cls._path.format(project_id=project_id)
        if limit == 0:  # unlimited results
            params["limit"] = DEFAULT_BATCH_SIZE
            records = [
                cls.from_server_data(entry) for entry in unpaginate(url, params, cls._client)
            ]
        else:
            r_data = cls._client.get(url, params=params).json()
            records = [cls.from_server_data(item) for item in r_data["data"]]
        if with_data_only:
            records = [
                record for record in records if record.status == AnomalyAssessmentStatus.COMPLETED
            ]
        return records

    @classmethod
    def compute(cls, project_id, model_id, backtest, source, series_id=None):
        """Request anomaly assessment insight computation on the specified subset.

        Parameters
        ----------
        project_id: str
            The ID of the project to compute insight for.
        model_id: str
            The ID of the model to compute insight for.
        backtest: int or "holdout"
            The backtest to compute insight for.
        source: "training" or "validation"
            The source  to compute insight for.
        series_id: str, optional
            The series id to compute insight for. Required for multiseries projects.

        Returns
        -------
        AnomalyAssessmentRecord
            The anomaly assessment record.
        """
        payload = {"backtest": backtest, "source": source}
        if series_id:
            payload["series_id"] = series_id
        url = cls._create_path.format(project_id=project_id, model_id=model_id)
        response = cls._client.post(url, data=payload)
        finished_url = wait_for_async_resolution(cls._client, response.headers["Location"])
        r_data = cls._client.get(finished_url).json()
        # it ll be always one record
        return cls.from_server_data(r_data["data"][0])

    def delete(self):
        """ Delete anomaly assessment record with preview and explanations. """
        self._client.delete(self.delete_location)

    def get_predictions_preview(self):
        """Retrieve aggregated predictions statistics for the anomaly assessment record.

        Returns
        -------
        AnomalyAssessmentPredictionsPreview
        """
        data = self._client.get(self.preview_location).json()
        return AnomalyAssessmentPredictionsPreview.from_server_data(data)

    def get_latest_explanations(self):
        """Retrieve latest predictions along with shap explanations for the most anomalous records.

        Returns
        -------
        AnomalyAssessmentExplanations
        """
        data = self._client.get(self.latest_explanations_location).json()
        return AnomalyAssessmentExplanations.from_server_data(data)

    def get_explanations(self, start_date=None, end_date=None, points_count=None):
        """Retrieve predictions along with shap explanations for the most anomalous records
        in the specified date range/for defined number of points.
        Two out of three parameters: start_date, end_date or points_count must be specified.

        Parameters
        ----------
        start_date: str, optional
            The start of the date range to get explanations in.
            Example: ``2020-01-01T00:00:00.000000Z``
        end_date: str, optional
            The end of the date range to get explanations in.
            Example: ``2020-10-01T00:00:00.000000Z``
        points_count: int, optional
            The number of the rows to return.

        Returns
        -------
        AnomalyAssessmentExplanations
        """
        return AnomalyAssessmentExplanations.get(
            self.project_id,
            self.record_id,
            start_date=start_date,
            end_date=end_date,
            points_count=points_count,
        )

    def get_explanations_data_in_regions(self, regions, prediction_threshold=0.0):
        """Get predictions along with explanations for the specified regions, sorted by
        predictions in descending order.

        Parameters
        ----------
        regions: list of preview_bins
            For each region explanations will be retrieved and merged.
        prediction_threshold: float, optional
            If specified, only points with score greater or equal to the threshold will be returned.

        Returns
        -------
        dict in a form of {'explanations': explanations, 'shap_base_value': shap_base_value}

        """
        explanations = []
        shap_base_value = None
        for region in regions:
            response = self.get_explanations(
                start_date=region["start_date"], end_date=region["end_date"]
            )
            shap_base_value = response.shap_base_value
            for item in response.data:
                if item["prediction"] >= prediction_threshold:
                    explanations.append(item)
        explanations = list(sorted(explanations, key=itemgetter("prediction"), reverse=True))
        return {"explanations": explanations, "shap_base_value": shap_base_value}


class AnomalyAssessmentPredictionsPreview(BaseAPIObject):
    """Aggregated predictions over time for the corresponding anomaly assessment record.
    Intended to find the bins with highest anomaly scores.

    .. versionadded:: v2.25


    Attributes
    ----------
    record_id: str
        The ID of the record.
    project_id: str
        The ID of the project record belongs to.
    model_id: str
        The ID of the model record belongs to.
    backtest: int or "holdout"
        The backtest of the record.
    source: "training" or "validation"
        The source of the record
    series_id: str or None
        The series id of the record for the multiseries projects. Defined only for the multiseries
        projects.
    start_date: str
        the ISO-formatted timestamp of the first prediction in the subset.
    end_date: str
        the ISO-formatted timestamp of the last prediction in the subset.
    preview_bins:  list of preview_bin objects.
        The aggregated predictions for the subset. See more info in `Notes`.

    Notes
    -----

    ``AnomalyAssessmentPredictionsPreview`` contains:

    * ``record_id`` : the id of the corresponding anomaly assessment record.
    * ``project_id`` : the project ID of the corresponding anomaly assessment record.
    * ``model_id`` : the model ID of the corresponding anomaly assessment record.
    * ``backtest`` : the backtest of the corresponding anomaly assessment record.
    * ``source`` : the source of the corresponding anomaly assessment record.
    * ``series_id`` : the series id of the corresponding anomaly assessment record
      for the multiseries projects.
    * ``start_date`` : the  ISO-formatted timestamp of the first prediction in the subset.
    * ``end_date`` : the ISO-formatted timestamp of the last prediction in the subset.
    * ``preview_bins`` :  list of PreviewBin objects. The aggregated predictions for the subset.
      Bins boundaries may differ from actual start/end dates because this is an aggregation.

    ``PreviewBin`` contains:


    * ``start_date`` (str) : the ISO-formatted datetime of the start of the bin.
    * ``end_date`` (str) : the ISO-formatted datetime of the end of the bin.
    * ``avg_predicted`` (float or None) : the average prediction of the model in the bin. None if
      there are no entries in the bin.
    * ``max_predicted`` (float or None) : the maximum prediction of the model in the bin. None if
      there are no entries in the bin.
    * ``frequency`` (int) : the number of the rows in the bin.
    """

    _path = "projects/{project_id}/anomalyAssessmentRecords/{record_id}/predictionsPreview/"

    PreviewBinTrafaret = t.Dict(
        {
            t.Key("avg_predicted"): t.Float() | t.Null,
            t.Key("max_predicted"): t.Float() | t.Null,
            t.Key("start_date"): String,
            t.Key("end_date"): String,
            t.Key("frequency"): Int,
        }
    )

    _converter = (
        t.Dict(
            {
                t.Key("start_date"): String,
                t.Key("end_date"): String,
                t.Key("preview_bins"): t.List(PreviewBinTrafaret),
            }
        )
        .merge(RecordMetadataTrafaret)
        .ignore_extra("*")
    )

    def __init__(self, start_date, end_date, preview_bins, **record_kwargs):
        self.preview_bins = preview_bins
        self.start_date = start_date
        self.end_date = end_date
        super(AnomalyAssessmentPredictionsPreview, self).__init__(**record_kwargs)

    @classmethod
    def get(cls, project_id, record_id):
        """Retrieve aggregated predictions over time.

        Parameters
        ----------
        project_id: str
            The ID of the project.
        record_id: str
            The ID of the anomaly assessment record.

        Returns
        -------
        AnomalyAssessmentPredictionsPreview

        """
        url = cls._path.format(project_id=project_id, record_id=record_id)
        r_data = cls._client.get(url).json()
        return cls.from_server_data(r_data)

    def find_anomalous_regions(self, max_prediction_threshold=0.0):
        """Sort preview bins by max_predicted value and select those with max predicted value
         greater or equal to max prediction threshold.
         Sort the result by max predicted value in descending order.

        Parameters
        ----------
        max_prediction_threshold: float, optional
            Return bins with maximum anomaly score greater or equal to max_prediction_threshold.

        Returns
        -------
        preview_bins: list of preview_bin
            Filtered and sorted preview bins

        """
        no_empty_bins = [bin for bin in self.preview_bins if bin["frequency"]]
        filtered_bins = [
            bin for bin in no_empty_bins if bin["max_predicted"] >= max_prediction_threshold
        ]
        sorted_bins = list(sorted(filtered_bins, key=itemgetter("max_predicted"), reverse=True))
        return sorted_bins


class AnomalyAssessmentExplanations(BaseAPIObject):
    """Object which keeps predictions along with shap explanations for the most anomalous records
    in the specified date range/for defined number of points.

    .. versionadded:: v2.25

    Attributes
    ----------
    record_id: str
        The ID of the record.
    project_id: str
        The ID of the project record belongs to.
    model_id: str
        The ID of the model record belongs to.
    backtest: int or "holdout"
        The backtest of the record.
    source: "training" or "validation"
        The source of the record.
    series_id: str or None
        The series id of the record for the multiseries projects. Defined only for the multiseries
        projects.
    start_date: str or None
        The ISO-formatted datetime of the first row in the ``data``.
    end_date: str or None
        The ISO-formatted datetime of the last row in the ``data``.
    data: array of `data_point` objects or None
        See `data` info in `Notes` for more details.
    shap_base_value: float
        Shap base value.
    count: int
        The number of points in the ``data``.

    Notes
    -----

    ``AnomalyAssessmentExplanations`` contains:

    * ``record_id`` : the id of the corresponding anomaly assessment record.
    * ``project_id`` : the project ID of the corresponding anomaly assessment record.
    * ``model_id`` : the model ID of the corresponding anomaly assessment record.
    * ``backtest`` : the backtest of the corresponding anomaly assessment record.
    * ``source`` : the source of the corresponding anomaly assessment record.
    * ``series_id`` : the series id of the corresponding anomaly assessment record
      for the multiseries projects.
    * ``start_date`` : the ISO-formatted first timestamp in the response.
      Will be None of there is no data in the specified range.
    * ``end_date`` : the ISO-formatted last timestamp in the response.
      Will be None of there is no data in the specified range.
    * ``count`` : The number of points in the response.
    * ``shap_base_value`` : the shap base value.
    * ``data`` :  list of DataPoint objects in the specified date range.

    ``DataPoint`` contains:

     * ``shap_explanation`` : None or an array of up to 10 ShapleyFeatureContribution objects.
       Only rows with the highest anomaly scores have Shapley explanations calculated.
       Value is None if prediction is lower than `prediction_threshold`.
     * ``timestamp`` (str) : ISO-formatted timestamp for the row.
     * ``prediction`` (float) : The output of the model for this row.

    ``ShapleyFeatureContribution`` contains:

     * ``feature_value`` (str) : the feature value for this row. First 50 characters are returned.
     * ``strength`` (float) : the shap value for this feature and row.
     * ``feature`` (str) : the feature name.

    """

    _path = "projects/{project_id}/anomalyAssessmentRecords/{record_id}/explanations/"

    ShapContributionTrafaret = t.Dict(
        {t.Key("feature_value"): String, t.Key("strength"): t.Float, t.Key("feature"): String}
    )

    RowTrafaret = t.Dict(
        {
            t.Key("shap_explanation"): t.List(ShapContributionTrafaret) | t.Null,
            t.Key("timestamp"): String,
            t.Key("prediction"): t.Float,
        }
    )

    _converter = (
        t.Dict(
            {
                t.Key("count"): Int,
                t.Key("shap_base_value"): t.Float,
                t.Key("data"): t.List(RowTrafaret),
                t.Key("start_date"): String() | t.Null,
                t.Key("end_date"): String() | t.Null,
            }
        )
        .merge(RecordMetadataTrafaret)
        .ignore_extra("*")
    )

    def __init__(self, shap_base_value, data, start_date, end_date, count, **record_kwargs):
        self.shap_base_value = shap_base_value
        self.data = data
        self.count = count
        self.start_date = start_date
        self.end_date = end_date
        super(AnomalyAssessmentExplanations, self).__init__(**record_kwargs)

    @classmethod
    def get(cls, project_id, record_id, start_date=None, end_date=None, points_count=None):
        """Retrieve predictions along with shap explanations for the most anomalous records
        in the specified date range/for defined number of points.
        Two out of three parameters: start_date, end_date or points_count must be specified.

        Parameters
        ----------
        project_id: str
            The ID of the project.
        record_id: str
            The ID of the anomaly assessment record.
        start_date: str, optional
            The start of the date range to get explanations in.
            Example: ``2020-01-01T00:00:00.000000Z``
        end_date: str, optional
            The end of the date range to get explanations in.
            Example: ``2020-10-01T00:00:00.000000Z``
        points_count: int, optional
            The number of the rows to return.


        Returns
        -------
        AnomalyAssessmentExplanations

        """
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if points_count:
            params["pointsCount"] = points_count

        url = cls._path.format(project_id=project_id, record_id=record_id)
        r_data = cls._client.get(url, params=params).json()
        return cls.from_server_data(r_data)
