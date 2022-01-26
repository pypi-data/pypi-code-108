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

from autoai_ts_libs.deps.tspy.data_structures.io.PullStreamMultiTimeSeriesReader import PullStreamMultiTimeSeriesReader


class PythonQueueStreamMultiTimeSeriesReader(PullStreamMultiTimeSeriesReader):
    def __init__(self, py_queue):
        super().__init__()
        self._py_queue = py_queue

    def parse(self, message):
        return message

    def poll(self):
        res = []
        for i in range(0, self._py_queue.qsize()):
            (key, py_obs) = self._py_queue.get(block=False)
            j_pair = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(key, py_obs._j_observation)
            res.append(j_pair)
        return res
