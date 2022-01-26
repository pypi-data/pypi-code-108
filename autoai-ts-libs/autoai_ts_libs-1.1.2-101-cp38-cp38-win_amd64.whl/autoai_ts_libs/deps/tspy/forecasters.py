"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`
"""

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

def load(path):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.load(path)


def bats(training_sample_size, box_cox_transform=False):
    """
    Build a BATS model

    Parameters
    ----------
    training_sample_size: int

    box_cox_transform: bool, optional

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.bats(training_sample_size, box_cox_transform)


# def hws(samples_per_season, initial_training_seasons, algorithm_type="additive", compute_seasonality=None,
#         error_history_length=1, use_full_error_history=True):
#     from autoai_ts_libs.deps.tspy.context import get_or_create
#     tsc = get_or_create()
#     return tsc.forecasters.hws(samples_per_season, initial_training_seasons, algorithm_type, compute_seasonality, error_history_length, use_full_error_history)
def hws(**kwargs):
    """
    Build a Holt-Winters model

    Parameters
    ----------
    sample_per_season: int

    initial_training_season:

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.hws(**kwargs)



def arima(error_horizon_length=1, use_full_error_history=True, force_model=False, min_training_data=-1, p_min=0,
          p_max=-1, d=-1, q_min=0, q_max=-1):
    """
    Build a ARIMA model

    Parameters
    ----------
    error_horizon_length: int, optional (1)

    use_full_error_history: bool, optional (True)
    force_model: bool, optional (False)

    min_training_data: int, optional (1)

    p_min: int, optional (0)
    p_max: int, optional (-1)
    d: int, optional (-1)
    q_min: int, optional (0)
    q_max: int, optional (-1)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arima(error_horizon_length, use_full_error_history, force_model, min_training_data, p_min, p_max, d, q_min, q_max)


def arma(min_training_data=-1, p_min=0, p_max=5, q_min=0, q_max=5):
    """
    Build a ARMA model

    Parameters
    ----------
    min_training_data: int, optional (1)

    p_min: int, optional (0)
    p_max: int, optional (5)
    q_min: int, optional (0)
    q_max: int, optional (5)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arma(min_training_data, p_min, p_max, q_min, q_max)


def auto(min_training_data, error_history_length=1):
    """
    Build a AUTO model

    Parameters
    ----------
    min_training_data: int

    error_history_length: int, optional (1)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.auto(min_training_data, error_history_length)


def anomaly_detector(confidence):
    """
    Build a AnomalyDetector model

    Parameters
    ----------
    confidence: float

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.AnomalyDetector.AnomalyDetector`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.anomaly_detector(confidence)

def season_selector(sub_season_percent_delta=0.0, max_season_length=None):
    """
    Build a SeasonSelector model

    Parameters
    ----------
    sub_season_percent_delta: float, optional (0.0)
    max_season_length: int, optional (None)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.SeasonSelector.SeasonSelector`

    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.season_selector(sub_season_percent_delta, max_season_length)

def var(history_length=1):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.var(history_length)

def arimax(difference_all_data=False, disable_difference=False, diff_eta=False):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arimax(difference_all_data, disable_difference, diff_eta)


def arimax_palr(difference_all_data=False, disable_difference=False, diff_eta=False):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arimax_palr(difference_all_data, disable_difference, diff_eta)


def arimax_rar(difference_all_data=False, disable_difference=False, diff_eta=False):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arimax_rar(difference_all_data, disable_difference, diff_eta)

def arimax_rsr(difference_all_data=False, disable_difference=False, diff_eta=False):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arimax_rsr(difference_all_data, disable_difference, diff_eta)

def arimax_dmlr(difference_all_data=False, disable_difference=False, diff_eta=False):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.forecasters.arimax_dmlr(difference_all_data, disable_difference, diff_eta)
