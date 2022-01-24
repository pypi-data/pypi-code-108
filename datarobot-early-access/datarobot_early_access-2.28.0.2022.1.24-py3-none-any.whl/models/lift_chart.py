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

LiftChartBinsTrafaret = t.Dict(
    {
        t.Key("bins"): t.List(
            t.Dict(
                {
                    t.Key("actual"): t.Float,
                    t.Key("predicted"): t.Float,
                    t.Key("bin_weight"): t.Float,
                }
            ).ignore_extra("*")
        )
    }
)


class LiftChart(APIObject):
    """ Lift chart data for model.

    Notes
    -----
    ``LiftChartBin`` is a dict containing the following:

        * ``actual`` (float) Sum of actual target values in bin
        * ``predicted`` (float) Sum of predicted target values in bin
        * ``bin_weight`` (float) The weight of the bin. For weighted projects, it is the sum of \
          the weights of the rows in the bin. For unweighted projects, it is the number of rows in \
          the bin.

    Attributes
    ----------
    source : str
        Lift chart data source. Can be 'validation', 'crossValidation' or 'holdout'.
    bins : list of dict
        List of dicts with schema described as ``LiftChartBin`` above.
    source_model_id : str
        ID of the model this lift chart represents; in some cases,
        insights from the parent of a frozen model may be used
    target_class : str, optional
        For multiclass lift - target class for this lift chart data.
    """

    _converter = (
        t.Dict(
            {
                t.Key("source"): String,
                t.Key("source_model_id"): String,
                t.Key("target_class", optional=True, default=None): String | t.Null,
            }
        )
        .merge(LiftChartBinsTrafaret)
        .ignore_extra("*")
    )

    def __init__(self, source, bins, source_model_id, target_class):
        self.source = source
        self.bins = bins
        self.source_model_id = source_model_id
        self.target_class = target_class

    def __repr__(self):
        if self.target_class:
            return encode_utf8_if_py2(u"LiftChart({}:{})".format(self.target_class, self.source))
        return encode_utf8_if_py2(u"LiftChart({})".format(self.source))
