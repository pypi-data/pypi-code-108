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

from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures import utils


class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc

    def dl(self, func=None):
        if func is None:
            return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.dl()
        else:
            return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.dl(
                utils.IMatcher(func)
            )

    def jaro_winkler(self):
        return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.jaroWinkler()

    def sbd(self):
        return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.sbd()

    def dtw(self, func):
        j_func = lambda o1, o2: func(Observation(self._tsc, o1.getTimeTick(), o1.getValue()),
                                     Observation(self._tsc, o2.getTimeTick(), o2.getValue()))
        return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.nonConstraintDtw(
            utils.IObjectDistanceCalculator(j_func)
        )

    def sakoe_chiba_dtw(self, func, constraint):
        j_func = lambda o1, o2: func(Observation(self._tsc, o1.getTimeTick(), o1.getValue()),
                                     Observation(self._tsc, o2.getTimeTick(), o2.getValue()))
        return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.sakoeChibaDtw(
            utils.IObjectDistanceCalculator(j_func),
            constraint
        )

    def itakura_parralelogram_dtw(self, func, constraint, center_offset_percentage):
        j_func = lambda o1, o2: func(Observation(self._tsc, o1.getTimeTick(), o1.getValue()),
                                     Observation(self._tsc, o2.getTimeTick(), o2.getValue()))
        return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.itakuraParallelogramDtw(
            utils.IObjectDistanceCalculator(j_func),
            constraint,
            center_offset_percentage
        )

    def manhattan(self, func):
        return self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.distance.DistanceReducers.nonTimewarpedDtw(
            utils.IObjectDistanceCalculator(func)
        )
