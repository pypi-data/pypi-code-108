
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

class ForecastingModel:
    """
    An online forecasting model which has the following components:
    1. Wraps a forecasting algorithm (see :class:`~autoai_ts_libs.deps.tspy.forecasters` for algorithms)
    2. Updated in real-time with new scalar data, thereby modifying the underlying components of the forecasting
    algorithm
    3. Provides forecasts based on the most recent model updates

    Attributes
    ----------
    average_interval : float
        Get the average interval across all calls to
        :func:`~autoai_ts_libs.deps.tspy.forecasting.ForecastingModel.ForecastingModel.update_model`.
    error_horizon_length : int
        Get the value of the error horizon length
    initial_time_updated : int
        Get the first time value used to build the forecasting model
    last_time_updated : int
        Get the most recent time value used to build the forecasting model.

    Examples
    --------
    create a forecasting model (auto-forecasting algorithm)

    >>> import autoai_ts_libs.deps.tspy
    >>> model = autoai_ts_libs.deps.tspy.forecasters.auto(10)
    >>> model
    Forecasting Model
      Algorithm: Unitialized.  Min training size=10
    HWSAdditive:HWSAdditive=-1 (aLevel=0, bSlope=0, gSeas=0) uninitialized
    HWSMultiplicative:HWSMultiplicative=-1 (aLevel=0, bSlope=0, gSeas=0) uninitialized
    RegularARIMAAlgorithm:RegularARIMAAlgorithm [armaAlgorithm=RegularARMAAlgorithm [dataHistory=null, errorHistory=null, dataMean=NaN, minTrainingData=80, pMin=0, pMax=5, qMin=0, qMax=5, forceModel=false], differencer=null, minTrainingData=82, diffOrder=-1]
    RegularSegmentedLinear:RegularSegmentedLinear,history=-1,width=1 [ ]
    RegularSegmentedAveraging:RegularSegmentedAveraging,history=-1,width=1 [uninitialized ]
    RegularLinear:RegularLinear [linearFitter=LeastSquaresFitter [yIntercept=0.0, slope=0.0], minTrainingSamples=2]
    RegularLinear:RegularLinear [linearFitter=LeastSquaresFitter [yIntercept=0.0, slope=0.0], minTrainingSamples=2]
    BATSAlgorithm:BATSAlgorithm

    update the model with values

    >>> for i in range(0,10):
        ...model.update_model(i, float(i))
    >>> model
    Forecasting Model
      Algorithm: HWSAdditive:HWSAdditive=1 (aLevel=0.001, bSlope=0.001, gSeas=0.001) level=9.99004488020975, slope=0.9999900896408388, seasonal(amp,per,avg)=(0.0,1, 5,-0.009900448802097483)
    HWSMultiplicative:HWSMultiplicative=1 (aLevel=0.001, bSlope=0.001, gSeas=0.001) level=9.990109117210386, slope=0.9999901537464366, seasonal(amp,per,avg)=(0.0,1, 5,0.9970972695898375)
    RegularARIMAAlgorithm:RegularARIMAAlgorithm [armaAlgorithm=RegularARMAAlgorithm [dataHistory=null, errorHistory=null, dataMean=NaN, minTrainingData=80, pMin=0, pMax=5, qMin=0, qMax=5, forceModel=false], differencer=null, minTrainingData=82, diffOrder=-1]
    RegularSegmentedLinear:RegularSegmentedLinear=1,history=-1,width=1 [(y=1.0*x + 0.0)  ]
    RegularSegmentedAveraging:RegularSegmentedAveraging=1,history=-1,width=1 [(avg=4.5)  ]
    RegularLinear:RegularLinear [linearFitter=LeastSquaresFitter [yIntercept=0.0, slope=1.0], minTrainingSamples=2]
    RegularLinear:RegularLinear [linearFitter=LeastSquaresFitter [yIntercept=0.0, slope=1.0], minTrainingSamples=2]
    BATSAlgorithm:BATSAlgorithm

    forecast at a time in the future

    >>> model.forecast_at(15)
    14.993695899928097
    """
    def __init__(self, jvm, algorithm, j_fm=None):
        self._jvm = jvm
        if j_fm is None:
            self._j_fm = self._jvm.com.ibm.research.time_series.forecasting.models.ForecastingModel(algorithm)
        else:
            self._j_fm = j_fm
        self._time_units = self._jvm.com.ibm.research.time_series.forecasting.timeseries.TimeUnits.Undefined

    def __getstate__(self):
        j_fm_str = self._jvm.com.ibm.research.time_series.transforms.forecastors.PythonConnector.serializeModel(self._j_fm)
        return {'j_fm': j_fm_str}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        tsc = get_or_create()
        self._jvm = tsc._jvm
        self._j_fm = self._jvm.com.ibm.research.time_series.transforms.forecastors.PythonConnector.deserializeModel(d['j_fm'])
        self._time_units = self._jvm.com.ibm.research.time_series.forecasting.timeseries.TimeUnits.Undefined

    def is_initialized(self):
        """
        Returns
        -------
        bool
            True if the model has been initialized and is ready for forecasting
        """
        return self._j_fm.isInitialized()

    def update_model(self, timestamp, value):
        """
        update the model at a given timestamp

        Parameters
        ----------
        timestamp : int
            time corresponding to the given data value
        value : float
            data value to be trained into the model at the given timestamp
        """
        if isinstance(timestamp, list) and isinstance(value, list):
            self._jvm.com.ibm.research.time_series.transforms.forecastors.PythonConnector.bulkTrain(self._j_fm,
                                                                                                    str(timestamp),
                                                                                                    str(value))
        elif isinstance(timestamp, int) and (isinstance(value, float) or isinstance(value, int)):
            self._j_fm.updateModel(self._time_units, timestamp, value)
        else:
            raise TypeError("you must provide either 2 lists or an int and float")

    def forecast_at(self, at):
        """
        compute the forecast at a given time

        Parameters
        ----------
        at : int
            the time at which to compute a forecast

        Returns
        -------
        float
            a valid forecast value
        """
        return self._j_fm.forecastAt(at)

    def bounds_at(self, at, confidence):
        """
        get the lower and upper bounds for the forecast at the given time and the given confidence level

        Parameters
        ----------
        at : int
            the time in the future, for which we want to predict the bounds with the confidence value that corresponds
            to the forecast at that time
        confidence : float
            a number between 0 and 1 representing the confidence required for the return bounds values

        Returns
        -------
        list
            a list of size 2 containing the lower and upper bounds, in this order, such that the actual value is between
            these bounds with probability equal to the given confidence. Never return null, however, if the bounds could
            not be computed, then the lower bound will be negative infinity (min float) and the upper bound will be
            positive infinity (max float)
        """
        return self._j_fm.boundsAt(at, confidence)

    def error_at(self, at):
        """
        compute the error estimate for the forecast at the given point in time

        Parameters
        ----------
        at : int
            time in the future at which error is being requested

        Returns
        -------
        float
            the error estimate. If the underlying algorithm does not support error computation, returns NaN
        """
        return self._j_fm.errorAt(at)

    def reset_model(self):
        """
        reset the model to an uninitialized state
        """
        self._j_fm.resetModel()

    def save(self, path):
        """
        save the model to a file

        Parameters
        ----------
        path : string
            path to file
        """
        self._jvm.com.ibm.research.time_series.transforms.forecastors.PythonConnector.saveForecastingModel(
            self._j_fm,
            path
        )

    @property
    def average_interval(self):
        """
        Returns
        -------
        float
            Get the average interval across all calls to
            :func:`~autoai_ts_libs.deps.tspy.forecasting.ForecastingModel.ForecastingModel.update_model`. Will return -1 if 1 or fewer
            samples have been provided.
        """
        return self._j_fm.getAverageInterval()

    @property
    def error_horizon_length(self):
        """
        Returns
        -------
        int
            Get the value of the error horizon length. Will return 0 if not set.
        """
        return self._j_fm.getErrorHorizonLength()

    @property
    def initial_time_updated(self):
        """
        Returns
        -------
        int
            Get the first time value used to build the forecasting model. Will return a negative value if the model has
            not been initialized
        """
        return self._j_fm.getInitialTimeUpdated()

    @property
    def last_time_updated(self):
        """
        Returns
        -------
        int
            Get the most recent time value used to build the forecasting model. Will return negative value if the model
            is not updated
        """
        return self._j_fm.getLastTimeUpdated()

    def __str__(self):
        return self._j_fm.toString()

    def __repr__(self):
        return self._j_fm.toString()
