import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from profiling.financial import load_financial_configurations, analy_optim_mean_var, loss_portfolio_mean_var
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
from pathlib import Path
import logging

import adutils

adutils.init("logger")
from adutils import setup_logger
from adlearn.engine import get_engine

logger = logging.getLogger(__name__)

engine = get_engine(kind="multiproc", context="spawn", print_percent=None, max_cpus=10)

setup_logger()

(
    path_save_images,
    date,
    common_fee,
    overall_risk_coeff,
    n_iterations,
    step_size,
    alpha,
    all_prices,
) = load_financial_configurations("run_configs.json")


def run(number_isins_cut):
    number_isins, cut = number_isins_cut

    logger.info(f"Starting run with {number_isins} isins and cut={cut}...")

    selected_prices = all_prices.dropna(how="any", axis=1)

    chosen_isins = selected_prices.columns[:number_isins]
    selected_prices = selected_prices[chosen_isins]
    selected_returns = selected_prices.pct_change()

    selected_cov = selected_returns.cov()

    fees = pd.DataFrame(data=np.full(shape=(len(chosen_isins), 1), fill_value=common_fee), index=[chosen_isins])
    weights_day_before = pd.DataFrame(
        data=np.full(shape=(len(chosen_isins), 1), fill_value=(1.0 / number_isins)), index=[chosen_isins]
    )

    analy_opt, cond = analy_optim_mean_var(
        r_np=selected_returns.loc[date].to_numpy().reshape((number_isins, 1)),
        risk_coeff=overall_risk_coeff,
        cov_np=selected_cov.to_numpy(),
        n=len(chosen_isins),
        cut=cut,
        return_cond=True,
    )
    loss_at_min = loss_portfolio_mean_var(
        wt_np=analy_opt,
        wt_1_np=weights_day_before.to_numpy(),
        r_np=selected_returns.loc[date].to_numpy().reshape((number_isins, 1)),
        risk_coeff=overall_risk_coeff,
        eps_np=fees.to_numpy(),
        cov_np=selected_cov.to_numpy(),
        n=len(chosen_isins),
        by_component=True,
    )
    logger.info(f"[{number_isins} - {cut}] : cond={cond}, loss_at_min={loss_at_min}")
    return (cut, number_isins), cond, loss_at_min


if __name__ == "__main__":

    cuts = [float(f"1e-{exp}") for exp in range(1, 16)]
    cuts.append(0)
    isins = list(range(5, 205, 5))

    pairs = [(isin, cut) for isin in isins for cut in cuts]

    results = engine(run, pairs)

    cuts_isins, conds, losses = zip(*results)
    index = pd.MultiIndex.from_tuples(cuts_isins)
    conds = pd.Series(index=index, data=np.log10(conds)).sort_index().unstack().iloc[0]
    losses = pd.Series(index=index, data=losses).sort_index().unstack()

    losses_nocuts = losses.iloc[0]
    losses = losses.iloc[1:]

    fig, axes = plt.subplots(3, 1, figsize=(10, 10))
    axes[0].scatter(conds.index, conds.values)
    colors = ["red" if loss > 0 else "blue" for loss in losses_nocuts]
    axes[2].scatter(losses_nocuts.index, np.log10(abs(losses_nocuts.values)), c=colors)
    im_losses = axes[1].imshow(
        losses, cmap="terrain", extent=[isins[0], isins[-1], np.log10(cuts[0]), np.log10(cuts[-2])], aspect="auto"
    )
    divider = make_axes_locatable(axes[1])
    cax_losses = divider.append_axes("right", size="5%", pad=0.05)
    cbar_losses = fig.colorbar(im_losses, cax=cax_losses, orientation="vertical")
    cbar_losses.set_label("Loss", rotation=270)
    cax_losses.yaxis.labelpad = 15
    axes[2].set_xlabel("Isins")
    axes[0].set_ylabel("$\\log($Condition Number$)$")
    axes[1].set_ylabel("$\\log($cut$)$")
    axes[2].set_ylabel("$\\log($Loss$)$ (no cuts)")
    fig.savefig(Path(path_save_images) / f"analytical_solution.pdf")
