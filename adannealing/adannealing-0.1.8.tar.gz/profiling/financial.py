import numpy as np
import logging
import json
import pandas as pd

logger = logging.getLogger(__name__)


def load_financial_configurations(path):
    with open(path) as f:
        configs = json.load(f)
    all_prices = pd.read_parquet(configs["prices_path"])

    # parameters run ++++++++++++++++++++++++++++++++++++++++++++++++
    # Assumptions in the code:
    #   - common fees
    #   - weights_t-1 = equi
    path_save_images = configs["path_save_images"]
    date = configs["date"]
    common_fee = configs["common_fee"]
    overall_risk_coeff = configs["overall_risk_coeff"]
    n_iterations = configs["n_iterations"]
    step_size = configs["step_size"]
    alpha = configs["alpha"]

    date_start = configs["date_start"]
    date_end = configs["date_end"]
    # parameters run ++++++++++++++++++++++++++++++++++++++++++++++++

    all_prices = all_prices[all_prices.index >= pd.Timestamp(date_start)]
    all_prices = all_prices[all_prices.index <= pd.Timestamp(date_end)]
    return path_save_images, date, common_fee, overall_risk_coeff, n_iterations, step_size, alpha, all_prices


def loss_portfolio_score_based():
    pass


def loss_portfolio_mean_var(
    wt_np: np.array,
    wt_1_np: np.array,
    r_np: np.array,
    risk_coeff: float,
    eps_np: np.array,
    cov_np: np.array,
    n: int,
    by_component: bool = False,
) -> float:

    common_shape = (n, 1)
    assert wt_np.shape == common_shape
    assert wt_1_np.shape == common_shape
    assert r_np.shape == common_shape
    assert eps_np.shape == common_shape
    assert cov_np.shape == (n, n)

    return_term = r_np.T.dot(wt_np)
    risk_term = 0.5 * wt_np.T.dot(cov_np.dot(wt_np))
    fees_term = np.abs(wt_np - wt_1_np).T.dot(eps_np)

    if by_component:
        logger.info(f" [LOSS] return term : {return_term}")
        logger.info(f" [LOSS] risk term : {risk_term}")
        logger.info(f" [LOSS] fees term : {fees_term}")

    loss = -return_term + risk_term * risk_coeff + fees_term

    return loss[0][0]


def box(x, point_low, point_high, sharpness, height, speed):

    if point_low >= point_high:
        raise RuntimeError("Box functon: lower boundary is larger-equal to the upper boundary.")

    l_ = -1.0
    r = +1.0
    val = wall(l_, x, point_low, sharpness, height, speed)
    val = val + wall(r, x, point_high, sharpness, height, speed)

    return val


def wall(lr, x, point, sharpness, height, speed):
    val = (lr * speed * (x - point) + height) * sigmoid(lr * (x - point) * sharpness)
    return val


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def analy_optim_mean_var(
    r_np: np.array, risk_coeff: float, cov_np: np.array, n: int, cut: float = None, return_cond: bool = False
):

    common_shape = (n, 1)
    assert r_np.shape == common_shape
    assert cov_np.shape == (n, n)

    cond = np.linalg.cond(cov_np)
    logger.info(f"Condition number: {cond}")
    if cut is not None:
        optimum_w = np.linalg.pinv(cov_np, cut).dot(r_np) / risk_coeff
    else:
        optimum_w = np.linalg.inv(cov_np).dot(r_np) / risk_coeff

    if not return_cond:
        return optimum_w
    else:
        return optimum_w, cond
