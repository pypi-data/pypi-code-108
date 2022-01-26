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

from autoai_ts_libs.deps.tspy.data_structures.ml.clustering.TimeSeriesClusteringModel import TimeSeriesClusteringModel


class KShapeModel(TimeSeriesClusteringModel):

    def __init__(self, tsc, j_model):
        super().__init__(tsc, j_model)

    def save(self, path):
        if isinstance(path, str):
            self._j_model.save(self._tsc._jvm.java.io.FileOutputStream(path))
        else:
            self._j_model.save(path)

    def __getstate__(self):
        j_model_str = self._tsc._jvm.com.ibm.research.time_series.ml.clustering.PythonConnector.serializeKShapeModel(self._j_model)
        return {'j_model': j_model_str}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        tsc = get_or_create()
        j_model = tsc._jvm.com.ibm.research.time_series.ml.clustering.PythonConnector.deserializeKShapeModel(d['j_model'])
        super().__init__(tsc, j_model)
