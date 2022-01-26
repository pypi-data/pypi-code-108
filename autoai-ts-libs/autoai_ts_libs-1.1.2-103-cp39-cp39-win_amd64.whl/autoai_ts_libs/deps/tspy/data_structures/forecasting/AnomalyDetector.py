
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

class AnomalyDetector:
    """
    A basic anomaly detector which used in conjunction with a
    :class:`~autoai_ts_libs.deps.tspy.forecasting.ForecastingModel.ForecastingModel` can identify anomalies
    """
    def __init__(self, jvm, confidence):
        self._jvm = jvm
        self._j_anomaly_detector = self._jvm.com.ibm.research.time_series.forecasting.anomaly.pointwise.BoundForecastingDetector(confidence)

    def is_anomaly(self, forecasting_model, timestamp, value):
        """
        check for an anomaly given a forecasting model, a timestamp, and a value

        Parameters
        ----------
        forecasting_model : :class:`~autoai_ts_libs.deps.tspy.forecasting.ForecastingModel.ForecastingModel`
            the model against which this request is made
        timestamp : int
            the point in time for which the actual value corresponds
        value : float
            the data value under consideration as an anomaly

        Returns
        -------
        bool
            true if the value is outside of the bounds identified for the given time using the instance's confidence
            level or the value is NaN, otherwise false
        """
        return self._j_anomaly_detector.isAnomaly(forecasting_model._j_fm, timestamp, value)
