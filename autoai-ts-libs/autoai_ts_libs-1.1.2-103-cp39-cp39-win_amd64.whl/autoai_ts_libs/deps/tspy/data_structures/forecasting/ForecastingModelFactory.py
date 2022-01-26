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

from autoai_ts_libs.deps.tspy.data_structures.forecasting import SeasonSelector, ForecastingAlgorithm
from . import ForecastingModel


class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc
        self._jvm = tsc._jvm

    def load(self, path):
        j_fm = self._jvm.com.ibm.research.time_series.transforms.forecastors.PythonConnector.readForecastingModel(path)
        return ForecastingModel.ForecastingModel(self._jvm, None, j_fm)

    def season_selector(self, sub_season_percent_delta=0.0, max_season_length=None):
        j_season_selector = self._jvm.com.ibm.research.time_series.forecasting.util.RegularFFTSeasonSelector(
            sub_season_percent_delta, 0 if max_season_length is None else max_season_length)
        return SeasonSelector.SeasonSelector(self._tsc, j_season_selector)

    def arimax(self, difference_all_data=False, disable_difference=False, diff_eta=False):
        if disable_difference:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXAlgorithm(
                disable_difference
            )
        else:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXAlgorithm(
                difference_all_data, diff_eta
            )
        return ForecastingAlgorithm.ForecastingAlgorithm(self._tsc, arimax_algorithm)

    def arimax_palr(self, difference_all_data=False, disable_difference=False, diff_eta=False):
        if disable_difference:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXPALRAlgorithm(
                disable_difference
            )
        else:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXPALRAlgorithm(
                difference_all_data, diff_eta
            )
        return ForecastingAlgorithm.ForecastingAlgorithm(self._tsc, arimax_algorithm)

    def arimax_rar(self, difference_all_data=False, disable_difference=False, diff_eta=False):
        if disable_difference:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXRARAlgorithm(
                disable_difference
            )
        else:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXRARAlgorithm(
                difference_all_data, diff_eta
            )
        return ForecastingAlgorithm.ForecastingAlgorithm(self._tsc, arimax_algorithm)

    def arimax_rsr(self, difference_all_data=False, disable_difference=False, diff_eta=False):
        if disable_difference:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXRSRAlgorithm(
                disable_difference
            )
        else:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.ARIMAXRSRAlgorithm(
                difference_all_data, diff_eta
            )
        return ForecastingAlgorithm.ForecastingAlgorithm(self._tsc, arimax_algorithm)

    def arimax_dmlr(self, difference_all_data=False, disable_difference=False, diff_eta=False):
        if disable_difference:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.DMLRAlgorithm(
                disable_difference
            )
        else:
            arimax_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arimax.DMLRAlgorithm(
                difference_all_data, diff_eta
            )
        return ForecastingAlgorithm.ForecastingAlgorithm(self._tsc, arimax_algorithm)

    def bats(self, training_sample_size, box_cox_transform=False):
        bats_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.BATS.BATSAlgorithm(
            training_sample_size,
            box_cox_transform
        )
        return ForecastingModel.ForecastingModel(self._jvm, bats_algorithm)

    def hws(self, **kwargs):
        algorithm_type = kwargs.get("algorithm_type", "additive")
        damp = kwargs.get("damp", False)

        if 'samples_per_season' in kwargs and 'initial_training_seasons' in kwargs:
            samples_per_season = kwargs["samples_per_season"]
            initial_training_seasons = kwargs["initial_training_seasons"]
            compute_seasonality = kwargs.get("compute_seasonality", None)
            error_history_length = kwargs.get("error_history_length", 1)
            use_full_error_history = kwargs.get("use_full_error_history", True)

            if compute_seasonality is None:
                compute_seasonality = samples_per_season <= 0
            elif type(compute_seasonality) != bool:
                raise TypeError("compute_seasonality parameter must be a boolean")

            if algorithm_type == "additive":
                algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.HW.HWSAdditive(
                    error_history_length,
                    use_full_error_history,
                    compute_seasonality,
                    samples_per_season,
                    initial_training_seasons,
                    damp
                )
            elif algorithm_type == "multiplicative":
                algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.HW.HWSMultiplicative(
                    error_history_length,
                    use_full_error_history,
                    compute_seasonality,
                    samples_per_season,
                    initial_training_seasons,
                    damp
                )
            else:
                raise ValueError("algorithm_type must be additive or multiplicative")
        elif "is_season_length" in kwargs and "number_of_samples" in kwargs:
            is_season_length = kwargs["is_season_length"]
            number_of_samples = kwargs["number_of_samples"]

            # boolean isSeasonLength, int numberOfSamples
            if algorithm_type == "additive":
                algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.HW.HWSAdditive(
                    is_season_length,
                    number_of_samples,
                    damp
                )
            elif algorithm_type == "multiplicative":
                algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.HW.HWSMultiplicative(
                    is_season_length,
                    number_of_samples,
                    damp
                )
            else:
                raise ValueError("algorithm_type must be additive or multiplicative")
        else:
            raise ValueError("must have samples_per_seasons/initial_training_seasons or is_season_length/number_of_samples set")

        return ForecastingModel.ForecastingModel(self._jvm, algorithm)

    def arima(self, error_horizon_length=1, use_full_error_history=True, force_model=False, min_training_data=-1, p_min=0, p_max=-1, d=-1, q_min=0, q_max=-1):
        arima_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arima.RegularARIMAAlgorithm(
            error_horizon_length,
            use_full_error_history,
            force_model,
            min_training_data,
            p_min,
            p_max,
            d,
            q_min,
            q_max
        )
        return ForecastingModel.ForecastingModel(self._jvm, arima_algorithm)

    def arma(self, min_training_data=-1, p_min=0, p_max=5, q_min=0, q_max=5):
        arma_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.arima.RegularARMAAlgorithm(
            min_training_data,
            p_min,
            p_max,
            q_min,
            q_max
        )
        return ForecastingModel.ForecastingModel(self._jvm, arma_algorithm)

    def auto(self, min_training_data, error_history_length=1):
        auto_algorithm = self._jvm.com.ibm.research.time_series.forecasting.algorithms.selecting.RegularDynamicSelectionAlgorithm(
            error_history_length,
            min_training_data
        )
        return ForecastingModel.ForecastingModel(self._jvm, auto_algorithm)

    def var(self, history_length=1):
        vector_autoregression = self._jvm.com.ibm.research.time_series.transforms.forecastors.Forecasters.var(history_length)
        return vector_autoregression
