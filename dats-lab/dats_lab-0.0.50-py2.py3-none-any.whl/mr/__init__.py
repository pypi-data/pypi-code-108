import os

import matplotlib.pyplot as plt
import arviz as az
import numpy as np
import pymc3 as pm
from theano.compile import shared


def _clean_file_name(file_name):
    return file_name.strip().replace(" ", "_").replace("/", "_")


def apply_multilinear_regression(df, src_fields, src_displays, target_field, target_display, a_mean=0, a_std=0.5,
                                 folder=None):
    src_display = ""
    for src_field in src_fields:
        src_display += src_field
        src_display += " "
    coef_names = {}

    for src_field in src_fields:
        coef_names[src_field] = "b" + src_field

        fig, ax = plt.subplots()
        df[[target_field, src_field]].plot.kde(ax=ax)
        if folder is not None:
            fig.savefig(os.path.join(folder, _clean_file_name(
                "Distribution_" + src_display + "_vs_" + target_display + ".png")))

    with pm.Model() as model:
        a = pm.Normal("a", a_mean, a_std)
        bs = {}
        for src_field in src_fields:
            b_mean = df[src_field].mean().round(decimals=2)
            b_std = df[src_field].std().round(decimals=2)
            bs[src_field] = pm.Normal(coef_names[src_field], b_mean, b_std)

        sigma = pm.Exponential("sigma", 1)

        calc_mu = a
        for src_field in src_fields:
            calc_mu += (bs[src_field] * df[src_field])

        mu = pm.Deterministic("mu", calc_mu)

        target = pm.Normal(
            target_field, mu=mu, sigma=sigma, observed=df[target_field].values
        )

        prior = pm.sample_prior_predictive()
        trace = pm.sample(tune=2000, draws=10000)
        ppc = pm.sample_posterior_predictive(trace, var_names=["mu", target_field], samples=4000)

        # Plot prior
        fig, ax = plt.subplots()

        x = np.linspace(-2, 2, 50)

        priors = [prior["a"][:]]
        for src_field in src_fields:
            priors.append(prior[coef_names[src_field]][:])

        for coefs in zip(*priors):
            coefs = list(coefs)
            for i in range(len(coefs)):
                if i == 0:
                    y = coefs[i]
                else:
                    y += (coefs[i] * x)
            ax.plot(x, y, c="black", alpha=0.4)

        ax.set_xlabel(src_display)
        ax.set_ylabel(target_display)
        if folder is not None:
            fig.savefig(
                os.path.join(folder, _clean_file_name("Prior_" + src_display + "_vs_" + target_display + ".png")))

        # Calculate summary
        field_names = ["a", "sigma"]
        for src_field in src_fields:
            field_names.append(coef_names[src_field])
        summary = az.summary(trace, var_names=field_names, round_to=2)

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

    return {
        "coef": coef_names,
        "model": model,
        "prior": prior,
        "trace": trace,
        "ppc": ppc,
        "summary": summary,
        "error": error
    }


def apply_multilinear_regression_shared_peer(df, src_fields, target_field, shared_src_field,
                                        shared_src_display, shared_target_field, shared_target_display, a_mean=0,
                                        a_std=0.5, folder=None):
    src_display = ""
    for src_field in src_fields:
        src_display += src_field
        src_display += " "

    coef_names = {}

    for src_field in src_fields:
        coef_names[src_field] = "b" + src_field

    shared_vals = {}
    for src_field in src_fields:
        shared_vals[src_field] = shared(df[src_field].values)

    with pm.Model() as model:
        a = pm.Normal("a", a_mean, a_std)
        bs = {}
        for src_field in src_fields:
            b_mean = df[src_field].mean().round(decimals=2)
            b_std = df[src_field].std().round(decimals=2)
            bs[src_field] = pm.Normal(coef_names[src_field], b_mean, b_std)

        sigma = pm.Exponential("sigma", 1)

        calc_mu = a
        for src_field in src_fields:
            calc_mu += (bs[src_field] * shared_vals[src_field])

        mu = pm.Deterministic("mu", calc_mu)

        target = pm.Normal(
            target_field, mu=mu, sigma=sigma, observed=df[target_field].values
        )

        aX = pm.Normal("aX", 0, 0.2)
        b_mean = df[shared_src_field].mean().round(decimals=2)
        b_std = df[shared_src_field].std().round(decimals=2)
        bX = pm.Normal(coef_names[shared_src_field] + "X", b_mean, b_std)
        sigmaX = pm.Exponential("sigmaX", 1)

        muX = pm.Deterministic("muX", aX + bX * shared_vals[shared_src_field])
        shared_target = pm.Normal(shared_target_field, muX, sigmaX, observed=df[shared_target_field])

        trace = pm.sample(tune=2000, draws=10000)
        data = az.from_pymc3(trace)

        # Calculate summary
    field_names = ["a", "sigma", coef_names[shared_src_field] + "X"]
    summary = az.summary(trace, var_names=field_names, round_to=2)

    n_items = int(df.describe()[shared_src_field]["count"])

    xseq = np.linspace(df[shared_src_field].min(), df[shared_src_field].max(), n_items)
    for src_field in src_fields:
        if src_field == shared_src_field:
            shared_vals[src_field].set_value(xseq)
        elif src_field == shared_target_field:
            print("skip")
        else:
            shared_vals[src_field].set_value(np.zeros(n_items))

    with model:
        ppc = pm.sample_posterior_predictive(trace, var_names=["muX"], samples=4000)

    mu_mean = ppc["muX"].mean(axis=0)

    fig, ax = plt.subplots()
    ax.plot(xseq, mu_mean, c="black")
    az.plot_hdi(xseq, ppc["muX"], ax=ax)

    ax.set_ylabel(shared_target_display)
    ax.set_xlabel(shared_src_display)
    fig.savefig(os.path.join(folder, _clean_file_name("Shared_" + shared_src_display + "_on_" + shared_target_display + ".png")))

    return {
        "coef": coef_names,
        "model": model,
        "trace": trace,
        "summary": summary
    }