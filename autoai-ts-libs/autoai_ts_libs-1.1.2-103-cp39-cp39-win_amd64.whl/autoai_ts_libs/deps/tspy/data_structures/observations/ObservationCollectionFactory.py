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

from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries


class Factory:

    def __init__(self, tsc):
        self._tsc = tsc

    def empty(self):
        return BoundTimeSeries(self._tsc)

    def builder(self):
        # j_ts_builder = self._tsc._jvm.com.ibm.research.time_series.core.utils.Observations.newBuilder()
        from autoai_ts_libs.deps.tspy.data_structures.observations.TSBuilder import TSBuilder
        return TSBuilder(self._tsc)

    def of(self, *observations):
        builder = self.builder()
        for obs in observations:
            builder.add(obs)
        return builder.result()
