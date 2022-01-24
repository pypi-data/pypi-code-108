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
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2

ResidualsTrafaret = {
    t.Key("residual_mean"): t.Float,
    t.Key("coefficient_of_determination"): t.Float,
    t.Key("standard_deviation", optional=True): t.Float,
}


class ResidualsChart(APIObject):
    """ Residual analysis chart data for model.

    .. versionadded:: v2.18

    This data is calculated over a randomly downsampled subset of the source data
    (capped at 1000 rows).

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
    source : str
        Lift chart data source. Can be 'validation', 'crossValidation' or 'holdout'.
    data : list
        List of lists with schema described as ``ResidualsChartRow`` above.
    coefficient_of_determination : float
        The r-squared value for the downsampled dataset
    residual_mean : float
        The arithmetic mean of the residual (predicted value minus actual value)
    source_model_id : str
        ID of the model this chart represents; in some cases,
        insights from the parent of a frozen model may be used
    standard_deviation : float
        standard_deviation of residual values
    """

    _converter = (
        t.Dict(
            {
                t.Key("source"): String,
                t.Key("data"): t.List(t.List(t.Float)),
                t.Key("source_model_id"): String,
            }
        )
        .merge(ResidualsTrafaret)
        .ignore_extra("*")
    )

    def __init__(
        self,
        source,
        data,
        residual_mean,
        coefficient_of_determination,
        source_model_id,
        standard_deviation=None,
    ):
        self.source = source
        self.data = data
        self.source_model_id = source_model_id
        self.coefficient_of_determination = coefficient_of_determination
        self.residual_mean = residual_mean
        self.standard_deviation = standard_deviation

    def __repr__(self):
        return encode_utf8_if_py2(u"ResidualChart({})".format(self.source))
