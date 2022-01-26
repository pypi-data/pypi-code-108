#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

from autoai_ts_libs.deps.tspy.data_structures import utils


class Factory:
    # todo these will be re-implemented since interpolator has lambda issues
    def __init__(self, tsc):
        self._tsc = tsc

    def linear(self, fill_value=None, history_size=1, future_size=1):
        if fill_value is not None:
            fill_value = utils.cast_to_j_if_necessary(fill_value, self._tsc)
        return self._tsc._jvm.com.ibm.research.time_series.transforms.interpolators.Interpolators.linear(fill_value, history_size, future_size)

    def cubic(self, fill_value=None, history_size=1, future_size=1):
        if fill_value is not None:
            fill_value = utils.cast_to_j_if_necessary(fill_value, self._tsc)
        return self._tsc._jvm.com.ibm.research.time_series.transforms.interpolators.Interpolators.cubic(fill_value, history_size, future_size)

    def next(self, default_value=None):
        if default_value is not None:
            default_value = utils.cast_to_j_if_necessary(default_value, self._tsc)
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.next(default_value)

    def prev(self, default_value=None):
        if default_value is not None:
            default_value = utils.cast_to_j_if_necessary(default_value, self._tsc)
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.prev(default_value)

    def nearest(self, default_value=None):
        if default_value is not None:
            default_value = utils.cast_to_j_if_necessary(default_value, self._tsc)
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nearest(default_value)

    def fill(self, value):
        if value is not None:
            value = utils.cast_to_j_if_necessary(value, self._tsc)
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.fill(value)

    def nullify(self):
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
