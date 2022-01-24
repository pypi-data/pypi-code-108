import os

import matplotlib.pyplot as plt
import arviz as az
import numpy as np
import pymc3 as pm
from theano.compile import shared


def _clean_file_name(file_name):
    return file_name.strip().replace(" ", "_").replace("/", "_")


def apply_linear_regression(df, src_field, src_display, target_field, target_display, a_mean=0, a_std=0.5, folder=None):
    coef_name = "b" + src_field

    b_mean = df[src_field].mean().round(decimals=2)
    b_std = df[src_field].std().round(decimals=2)

    fig, ax = plt.subplots()
    df[[target_field, src_field]].plot.kde(ax=ax)
    if folder is not None:
        fig.savefig(os.path.join(folder, _clean_file_name("Distribution_" + src_display + "_vs_" + target_display + ".png")))

    with pm.Model() as model:
        a = pm.Normal("a", a_mean, a_std)
        b = pm.Normal(coef_name, b_mean, b_std)
        sigma = pm.Exponential("sigma", 1)
        mu = pm.Deterministic("mu", a + b * df[src_field])

        target = pm.Normal(
            target_field, mu=mu, sigma=sigma, observed=df[target_field].values
        )

        prior = pm.sample_prior_predictive()
        trace = pm.sample(tune=2000, draws=10000)
        ppc = pm.sample_posterior_predictive(trace, var_names=["mu", target_field], samples=4000)

        # Plot prior
        fig, ax = plt.subplots()

        x = np.linspace(-2, 2, 50)

        for a, bu in zip(prior["a"][:], prior[coef_name][:]):
            y = a + bu * x
            ax.plot(x, y, c="black", alpha=0.4)

        ax.set_xlabel(src_display)
        ax.set_ylabel(target_display)
        if folder is not None:
            fig.savefig(os.path.join(folder, _clean_file_name("Prior_" + src_display + "_vs_" + target_display + ".png")))

        # Calculate summary
        summary = az.summary(trace, var_names=["a", coef_name, "sigma"], round_to=2)

        # Calculate error
        error = np.abs(ppc[target_field].mean(0) - az.hdi(ppc["mu"], 0.89).T)
        fig, ax = plt.subplots(figsize=(6, 6))
        plt.errorbar(
            df[target_field].values,
            ppc[target_field].mean(0),
            yerr=error,
            fmt="C0o",
        )
        ax.scatter(df[target_field].values, ppc[target_field].mean(axis=0))

        min_x, max_x = df[target_field].min(), df[target_field].max()
        ax.plot([min_x, max_x], [min_x, max_x], "k--")

        ax.set_ylabel("Predicted " + target_display)
        ax.set_xlabel("Observed " + target_display)
        if folder is not None:
            fig.savefig(os.path.join(folder, "Error_" + src_display + "_vs_" + target_display + ".png"))

        # Effect analyse
        shared_val = shared(df[src_field].values)
        with pm.Model() as model_shared:
            sigmaS = pm.Exponential("sigmaS", 1)
            aS = pm.Normal("aS", a_mean, a_std)
            bS = pm.Normal(coef_name + "S", b_mean, b_std)

            muS = pm.Deterministic("muS", aS + bS * shared_val)

            target = pm.Normal(target_field + "S", muS, sigmaS, observed=df[target_field])

            trace_shared = pm.sample(tune=2000, draws=10000)

        data_shared = az.from_pymc3(trace_shared)

        n_items = 20
        x_seq = [-n_items, n_items]
        shared_val.set_value(x_seq)

        with model_shared:
            ppc_shared = pm.sample_prior_predictive()
        fig, ax = plt.subplots()

        for i in range(50):
            ax.plot(x_seq, ppc_shared[target_field + "S"][i], c="black", alpha=0.3)

        ax.set_xlim(x_seq)
        ax.set_ylim(x_seq)
        ax.set_title("a~dnorm(0,2) \n " + coef_name + "~dnorm(0,5)")
        ax.set_xlabel(src_display)
        ax.set_ylabel(target_display)
        if folder is not None:
            fig.savefig(os.path.join(folder, _clean_file_name("Shared_Prior_" + src_display + "_vs_" + target_display + ".png")))

        xseq = np.linspace(df[src_field].min(), df[src_field].max(), 17)
        shared_val.set_value(xseq)

        with model_shared:
            shared_posterior_predictive = pm.sample_posterior_predictive(
                trace_shared, var_names=["muS"], samples=4000
            )

        mu_mean = shared_posterior_predictive["muS"].mean(axis=0)

        fig, ax = plt.subplots()
        ax.plot(xseq, mu_mean, c="black")
        ax.scatter(df[src_field], df[target_field], facecolors="none", edgecolors="b")
        az.plot_hdi(xseq, shared_posterior_predictive["muS"], ax=ax)
        ax.set_xlabel(src_display)
        ax.set_ylabel(target_display)
        if folder is not None:
            fig.savefig(os.path.join(folder, _clean_file_name("Shared_" + src_display + "_on_" + target_display + ".png")))

    return {
        "coef": coef_name,
        "model": model,
        "prior": prior,
        "trace": trace,
        "ppc": ppc,
        "summary": summary,
        "error": error
    }