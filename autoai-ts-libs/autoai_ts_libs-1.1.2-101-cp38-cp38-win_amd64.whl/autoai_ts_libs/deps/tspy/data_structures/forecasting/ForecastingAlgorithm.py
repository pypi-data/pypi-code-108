class ForecastingAlgorithm:

    def __init__(self, tsc, j_algorithm):
        self._tsc = tsc
        self._j_algorithm = j_algorithm

    def reset_model(self):
        self._j_algorithm.resetModel()

    def forecast_ahead(self, steps_ahead, exogenous_variables=None):
        if exogenous_variables is None:
            return self._j_algorithm.forecastAhead(steps_ahead)
        else:
            from py4j.java_collections import ListConverter
            java_array_ex = self._tsc._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.PythonConnector \
                .createArrayFromList(ListConverter().convert(exogenous_variables, self._tsc._gateway._gateway_client))
            return self._j_algorithm.forecastAhead(steps_ahead, java_array_ex)

    def is_initialized(self):
        return self._j_algorithm.isInitialized()

    def update_model(self, y, exogenous_variables=None):
        from py4j.java_collections import ListConverter
        java_array_y = self._tsc._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.PythonConnector \
            .createArrayFromList(ListConverter().convert(y, self._tsc._gateway._gateway_client))

        if exogenous_variables is None:
            self._j_algorithm.updateModel(java_array_y)
        else:
            java_list_ex = []
            for i in range(len(exogenous_variables)):
                java_list_ex.append(ListConverter().convert(exogenous_variables[i], self._tsc._gateway._gateway_client))

            java_list_ex_all = ListConverter().convert(java_list_ex, self._tsc._gateway._gateway_client)

            java_array_ex = self._tsc._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.PythonConnector\
                .create2dArrayFromList(java_list_ex_all)

            self._j_algorithm.updateModel(java_array_y, java_array_ex)

    def __getstate__(self):
        j_algorithm_str = self._tsc._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.PythonConnector.serializeAlgorithm(self._j_algorithm)
        return {'j_algorithm': j_algorithm_str}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        tsc = get_or_create()
        self._tsc = tsc
        self._j_algorithm = self._tsc._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.PythonConnector.deserializeAlgorithm(d['j_algorithm'])
