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
""" This module is deprecated; please use prediction_explanations.py instead."""

from datetime import datetime

import pandas as pd
import trafaret as t

from datarobot._compat import Int, String

from ..utils import deprecated, encode_utf8_if_py2, get_id_from_response
from .api_object import APIObject
from .prediction_explanations import (
    prediction_explanations_entry_trafaret,
    prediction_values_trafaret,
)

int_float_string = t.Type(int) | t.Type(float) | String(allow_blank=True)

reason_code_trafaret = t.Dict(
    {
        t.Key("row_id"): Int,
        t.Key("prediction"): int_float_string,
        t.Key("adjusted_prediction", optional=True): int_float_string,
        t.Key("prediction_values"): t.List(prediction_values_trafaret),
        t.Key("adjusted_prediction_values", optional=True): t.List(prediction_values_trafaret),
        t.Key("reason_codes"): t.List(prediction_explanations_entry_trafaret),
    }
).ignore_extra("*")


class ReasonCodesInitialization(APIObject):
    """
    Represents a reason codes initialization of a model.

    Attributes
    ----------
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model reason codes initialization is for
    reason_codes_sample : list of dict
        a small sample of reason codes that could be generated for the model
    """

    _path_template = "projects/{}/models/{}/reasonCodesInitialization/"
    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("reason_codes_sample"): t.List(reason_code_trafaret),
        }
    ).allow_extra("*")

    def __init__(self, project_id, model_id, reason_codes_sample=None):
        self.project_id = project_id
        self.model_id = model_id
        self.reason_codes_sample = reason_codes_sample

        self._path = self._path_template.format(self.project_id, self.model_id)

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(project_id={}, model_id={})".format(
                type(self).__name__, self.project_id, self.model_id
            )
        )

    @classmethod
    @deprecated("2.12", "2.15", "Please use PredictionExplanationsInitialization.get instead.")
    def get(cls, project_id, model_id):
        """
        Retrieve the reason codes initialization for a model.

        Reason codes initializations are a prerequisite for computing reason codes, and include
        a sample what the computed reason codes for a prediction dataset would look like.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model reason codes initialization is for

        Returns
        -------
        reason_codes_initialization : ReasonCodesInitialization
            The queried instance.

        Raises
        ------
        ClientError (404)
            If the project or model does not exist or the initialization has not been computed.
        """
        path = cls._path_template.format(project_id, model_id)
        return cls.from_location(path)

    @classmethod
    @deprecated("2.12", "2.15", "Please use PredictionExplanationsInitialization.create instead.")
    def create(cls, project_id, model_id):
        """
        Create a reason codes initialization for the specified model.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for which initialization is requested

        Returns
        -------
        job : Job
            an instance of created async job
        """
        from .job import Job

        response = cls._client.post(cls._path_template.format(project_id, model_id))
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    @deprecated("2.12", "2.15", "Please use PredictionExplanationsInitialization.delete instead.")
    def delete(self):
        """
        Delete this reason codes initialization.
        """
        self._client.delete(self._path)


class ReasonCodes(APIObject):
    """
    Represents reason codes metadata and provides access to computation results.

    Examples
    --------
    .. code-block:: python

        reason_codes = dr.ReasonCodes.get(project_id, reason_codes_id)
        for row in reason_codes.get_rows():
            print(row)  # row is an instance of ReasonCodesRow

    Attributes
    ----------
    id : str
        id of the record and reason codes computation result
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model reason codes initialization is for
    dataset_id : str
        id of the prediction dataset reason codes were computed for
    max_codes : int
        maximum number of reason codes to supply per row of the dataset
    threshold_low : float
        the lower threshold, below which a prediction must score in order for reason codes to be
        computed for a row in the dataset
    threshold_high : float
        the high threshold, above which a prediction must score in order for reason codes to be
        computed for a row in the dataset
    num_columns : int
        the number of columns reason codes were computed for
    finish_time : float
        timestamp referencing when computation for these reason codes finished
    reason_codes_location : str
        where to retrieve the reason codes
    """

    _path_template = "projects/{}/reasonCodesRecords/"
    _codes_path_template = "projects/{}/reasonCodes/"
    _converter = t.Dict(
        {
            t.Key("id"): String,
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("dataset_id"): String,
            t.Key("max_codes"): Int,
            t.Key("threshold_low", optional=True): t.Float,
            t.Key("threshold_high", optional=True): t.Float,
            t.Key("num_columns"): Int,
            t.Key("finish_time"): t.Float,
            t.Key("reason_codes_location"): String,
        }
    ).allow_extra("*")

    def __init__(
        self,
        id,
        project_id,
        model_id,
        dataset_id,
        max_codes,
        num_columns,
        finish_time,
        reason_codes_location,
        threshold_low=None,
        threshold_high=None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.max_codes = max_codes
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.id = id
        self.num_columns = num_columns
        self.finish_time = datetime.fromtimestamp(finish_time)
        self.reason_codes_location = reason_codes_location

        self._path = self._path_template.format(self.project_id)

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(id={}, project_id={}, model_id={})".format(
                type(self).__name__, self.id, self.project_id, self.model_id
            )
        )

    @classmethod
    @deprecated("2.12", "2.15", "Please use PredictionExplanations.get instead.")
    def get(cls, project_id, reason_codes_id):
        """
        Retrieve a specific reason codes.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        reason_codes_id : str
            id of the reason codes

        Returns
        -------
        reason_codes : ReasonCodes
            The queried instance.
        """
        path = "{}{}/".format(cls._path_template.format(project_id), reason_codes_id)
        return cls.from_location(path)

    @classmethod
    @deprecated("2.12", "2.15", "Please use PredictionExplanations.create instead.")
    def create(
        cls,
        project_id,
        model_id,
        dataset_id,
        max_codes=None,
        threshold_low=None,
        threshold_high=None,
    ):
        """
        Create a reason codes for the specified dataset.

        In order to create ReasonCodesPage for a particular model and dataset, you must first:

          * Compute feature impact for the model via ``datarobot.Model.get_feature_impact()``
          * Compute a ReasonCodesInitialization for the model via
            ``datarobot.ReasonCodesInitialization.create(project_id, model_id)``
          * Compute predictions for the model and dataset via
            ``datarobot.Model.request_predictions(dataset_id)``

        ``threshold_high`` and ``threshold_low`` are optional filters applied to speed up
        computation.  When at least one is specified, only the selected outlier rows will have
        reason codes computed. Rows are considered to be outliers if their predicted
        value (in case of regression projects) or probability of being the positive
        class (in case of classification projects) is less than ``threshold_low`` or greater than
        ``thresholdHigh``.  If neither is specified, reason codes will be computed for all rows.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for which reason codes are requested
        dataset_id : str
            id of the prediction dataset for which reason codes are requested
        threshold_low : float, optional
            the lower threshold, below which a prediction must score in order for reason codes to be
            computed for a row in the dataset. If neither ``threshold_high`` nor ``threshold_low``
            is specified, reason codes will be computed for all rows.
        threshold_high : float, optional
            the high threshold, above which a prediction must score in order for reason codes to be
            computed. If neither ``threshold_high`` nor ``threshold_low`` is specified, reason codes
            will be computed for all rows.
        max_codes : int, optional
            the maximum number of reason codes to supply per row of the dataset, default: 3.

        Returns
        -------
        job: Job
            an instance of created async job
        """
        from .job import Job

        payload = {
            "model_id": model_id,
            "dataset_id": dataset_id,
        }
        if max_codes is not None:
            payload["max_codes"] = max_codes
        if threshold_low is not None:
            payload["threshold_low"] = threshold_low
        if threshold_high is not None:
            payload["threshold_high"] = threshold_high
        response = cls._client.post(cls._codes_path_template.format(project_id), data=payload)
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    @classmethod
    @deprecated("2.12", "2.15", "Please use PredictionExplanations.list instead.")
    def list(cls, project_id, model_id=None, limit=None, offset=None):
        """
        List of reason codes for a specified project.

        Parameters
        ----------
        project_id : str
            id of the project to list reason codes for
        model_id : str, optional
            if specified, only reason codes computed for this model will be returned
        limit : int or None
            at most this many results are returned, default: no limit
        offset : int or None
            this many results will be skipped, default: 0

        Returns
        -------
        reason_codes : list[ReasonCodes]
        """
        response = cls._client.get(
            cls._path_template.format(project_id),
            params={"model_id": model_id, "limit": limit, "offset": offset},
        )
        r_data = response.json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @deprecated(
        "2.12",
        "2.15",
        "Please use the PredictionExplanations interface instead of the ReasonCodes interface.",
    )
    def get_rows(self, batch_size=None, exclude_adjusted_predictions=True):
        """
        Retrieve reason codes rows.

        Parameters
        ----------
        batch_size : int
            maximum number of reason codes rows to retrieve per request
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.

        Yields
        ------
        reason_codes_row : ReasonCodesRow
            Represents reason codes computed for a prediction row.
        """
        page = self.get_reason_codes_page(
            limit=batch_size, exclude_adjusted_predictions=exclude_adjusted_predictions
        )
        while True:
            for row in page.data:
                yield ReasonCodesRow(**row)
            if not page.next_page:
                break
            page = ReasonCodesPage.from_location(page.next_page)

    def get_all_as_dataframe(self, exclude_adjusted_predictions=True):
        """
        Retrieve all reason codes rows and return them as a pandas.DataFrame.

        Returned dataframe has the following structure:

            - row_id : row id from prediction dataset
            - prediction : the output of the model for this row
            - adjusted_prediction : adjusted prediction values (only appears for projects that
              utilize prediction adjustments, e.g. projects with an exposure column)
            - class_0_label : a class level from the target (only appears for classification
              projects)
            - class_0_probability : the probability that the target is this class (only appears for
              classification projects)
            - class_1_label : a class level from the target (only appears for classification
              projects)
            - class_1_probability : the probability that the target is this class (only appears for
              classification projects)
            - reason_0_feature : the name of the feature contributing to the prediction for this
              reason
            - reason_0_feature_value : the value the feature took on
            - reason_0_label : the output being driven by this reason.  For regression projects,
              this is the name of the target feature.  For classification projects, this is the
              class label whose probability increasing would correspond to a positive strength.
            - reason_0_qualitative_strength : a human-readable description of how strongly the
              feature affected the prediction (e.g. '+++', '--', '+') for this reason
            - reason_0_strength : the amount this feature's value affected the prediction
            - ...
            - reason_N_feature : the name of the feature contributing to the prediction for this
              reason
            - reason_N_feature_value : the value the feature took on
            - reason_N_label : the output being driven by this reason.  For regression projects,
              this is the name of the target feature.  For classification projects, this is the
              class label whose probability increasing would correspond to a positive strength.
            - reason_N_qualitative_strength : a human-readable description of how strongly the
              feature affected the prediction (e.g. '+++', '--', '+') for this reason
            - reason_N_strength : the amount this feature's value affected the prediction

        Parameters
        ----------
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set this to False to include adjusted prediction values in
            the returned dataframe.

        Returns
        -------
        dataframe: pandas.DataFrame
        """
        columns = ["row_id", "prediction"]
        rows = self.get_rows(
            batch_size=1, exclude_adjusted_predictions=exclude_adjusted_predictions
        )
        first_row = next(rows)
        adjusted_predictions_in_data = first_row.adjusted_prediction is not None
        if adjusted_predictions_in_data:
            columns.append("adjusted_prediction")
        # for regression, length is 1; for classification, length is number of levels in target
        # i.e. 2 for binary classification
        is_classification = len(first_row.prediction_values) > 1
        # include class label/probability for classification project
        if is_classification:
            for i in range(len(first_row.prediction_values)):
                columns.extend(["class_{}_label".format(i), "class_{}_probability".format(i)])
        for i in range(self.max_codes):
            columns.extend(
                [
                    "reason_{}_feature".format(i),
                    "reason_{}_feature_value".format(i),
                    "reason_{}_label".format(i),
                    "reason_{}_qualitative_strength".format(i),
                    "reason_{}_strength".format(i),
                ]
            )
        rc_list = []

        for i, row in enumerate(
            self.get_rows(exclude_adjusted_predictions=exclude_adjusted_predictions)
        ):
            data = [row.row_id, row.prediction]
            if adjusted_predictions_in_data:
                data.append(row.adjusted_prediction)
            if is_classification:
                for pred_value in row.prediction_values:
                    data.extend([pred_value["label"], pred_value["value"]])
            for rc in row.reason_codes:
                data.extend(
                    [
                        rc["feature"],
                        rc["feature_value"],
                        rc["label"],
                        rc["qualitative_strength"],
                        rc["strength"],
                    ]
                )
            rc_list.append(data + [None] * (len(columns) - len(data)))

        return pd.DataFrame(data=rc_list, columns=columns)

    def download_to_csv(self, filename, encoding="utf-8", exclude_adjusted_predictions=True):
        """
        Save reason codes rows into CSV file.

        Parameters
        ----------
        filename : str or file object
            path or file object to save reason codes rows
        encoding : string, optional
            A string representing the encoding to use in the output file, defaults to 'utf-8'
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.
        """
        df = self.get_all_as_dataframe(exclude_adjusted_predictions=exclude_adjusted_predictions)
        df.to_csv(path_or_buf=filename, header=True, index=False, encoding=encoding)

    def get_reason_codes_page(self, limit=None, offset=None, exclude_adjusted_predictions=True):
        """
        Get reason codes.

        If you don't want use a generator interface, you can access paginated reason codes directly.

        Parameters
        ----------
        limit : int or None
            the number of records to return, the server will use a (possibly finite) default if not
            specified
        offset : int or None
            the number of records to skip, default 0
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.

        Returns
        -------
        reason_codes : ReasonCodesPage
        """
        kwargs = {"limit": limit, "exclude_adjusted_predictions": exclude_adjusted_predictions}
        if offset:
            kwargs["offset"] = offset
        return ReasonCodesPage.get(self.project_id, self.id, **kwargs)

    @deprecated("2.12", "2.15", "Please use PredictionExplanations.delete instead.")
    def delete(self):
        """
        Delete this reason codes.
        """
        path = "{}{}/".format(self._path_template.format(self.project_id), self.id)
        self._client.delete(path)


class ReasonCodesRow(object):
    """
    Represents reason codes computed for a prediction row.

    Notes
    -----

    ``PredictionValue`` contains:

    * ``label`` : describes what this model output corresponds to.  For regression projects,
      it is the name of the target feature.  For classification projects, it is a level from
      the target feature.
    * ``value`` : the output of the prediction.  For regression projects, it is the predicted
      value of the target.  For classification projects, it is the predicted probability the
      row belongs to the class identified by the label.


    ``ReasonCode`` contains:

    * ``label`` : described what output was driven by this reason code.  For regression
      projects, it is the name of the target feature.  For classification projects, it is the
      class whose probability increasing would correspond to a positive strength of this
      reason code.
    * ``feature`` : the name of the feature contributing to the prediction
    * ``feature_value`` : the value the feature took on for this row
    * ``strength`` : the amount this feature's value affected the prediction
    * ``qualitativate_strength`` : a human-readable description of how strongly the feature
      affected the prediction (e.g. '+++', '--', '+')

    Attributes
    ----------
    row_id : int
        which row this ``ReasonCodeRow`` describes
    prediction : float
        the output of the model for this row
    adjusted_prediction : float or None
        adjusted prediction value for projects that provide this information, None otherwise
    prediction_values : list
        an array of dictionaries with a schema described as ``PredictionValue``
    adjusted_prediction_values : list
        same as prediction_values but for adjusted predictions
    reason_codes : list
        an array of dictionaries with a schema described as ``ReasonCode``
    """

    def __init__(
        self,
        row_id,
        prediction,
        prediction_values,
        reason_codes=None,
        adjusted_prediction=None,
        adjusted_prediction_values=None,
    ):
        self.row_id = row_id
        self.prediction = prediction
        self.prediction_values = prediction_values
        self.reason_codes = reason_codes
        self.adjusted_prediction = adjusted_prediction
        self.adjusted_prediction_values = adjusted_prediction_values

    def __repr__(self):
        return "{}(row_id={}, prediction={})".format(
            type(self).__name__, self.row_id, self.prediction
        )


class ReasonCodesPage(APIObject):
    """
    Represents batch of reason codes received by one request.

    Attributes
    ----------
    id : str
        id of the reason codes computation result
    data : list[dict]
        list of raw reason codes, each row corresponds to a row of the prediction dataset
    count : int
        total number of rows computed
    previous_page : str
        where to retrieve previous page of reason codes, None if current page is the first
    next_page : str
        where to retrieve next page of reason codes, None if current page is the last
    reason_codes_record_location : str
        where to retrieve the reason codes metadata
    adjustment_method : str
        Adjustment method that was applied to predictions, or 'N/A' if no adjustments were done.
    """

    _path_template = "projects/{}/reasonCodes/"
    _converter = t.Dict(
        {
            t.Key("id"): String,
            t.Key("count"): Int,
            t.Key("previous", optional=True): String(),
            t.Key("next", optional=True): String(),
            t.Key("data"): t.List(reason_code_trafaret),
            t.Key("reason_codes_record_location"): t.URL,
            t.Key("adjustment_method", default="N/A"): String(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id,
        count=None,
        previous=None,
        next=None,
        data=None,
        reason_codes_record_location=None,
        adjustment_method=None,
    ):
        self.id = id
        self.count = count
        self.previous_page = previous
        self.next_page = next
        self.data = data
        self.reason_codes_record_location = reason_codes_record_location
        self.adjustment_method = adjustment_method

    def __repr__(self):
        return encode_utf8_if_py2(u"{}(id={})".format(type(self).__name__, self.id))

    @classmethod
    def get(
        cls, project_id, reason_codes_id, limit=None, offset=0, exclude_adjusted_predictions=True
    ):
        """
        Retrieve reason codes.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        reason_codes_id : str
            id of the reason codes
        limit : int or None
            the number of records to return, the server will use a (possibly finite) default if not
            specified
        offset : int or None
            the number of records to skip, default 0
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.

        Returns
        -------
        reason_codes : ReasonCodesPage
            The queried instance.
        """
        params = {
            "offset": offset,
            "exclude_adjusted_predictions": "true" if exclude_adjusted_predictions else "false",
        }
        if limit:
            params["limit"] = limit
        path = "{}{}/".format(cls._path_template.format(project_id), reason_codes_id)
        return cls.from_location(path, params=params)

    @classmethod
    def from_location(cls, path, params=None):
        server_data = cls._client.get(path, params=params).json()
        return cls.from_server_data(server_data)
