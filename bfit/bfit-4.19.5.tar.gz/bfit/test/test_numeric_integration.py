#!/usr/bin/python3

# Test of the numeric integration used when calculating the pulsed stretched
# exponential function. Specifically, check how well the result converges to the
# analytic solution when the stretching exponent beta = 1.

# Ryan M. L. McFadden
# 2021-02-22

from numpy.testing import *
import numpy as np
import pandas as pd
import bdata as bd
from bfit.fitting.functions import pulsed_strexp, pulsed_exp


# tolerance = upper limit for an acceptable absolute deviation between results
# n_samples = number of points to use in each array in the simulation
# print_summary = print a summary of simulation results to stdout
def test_numeric_integration(tolerance=1e-5, n_samples=50, print_summary=False):

    # constants appropriate for most β-NMR data taken at TRIUMF
    nuclear_lifetime = bd.life["Li8"]
    pulse_duration = 3.0 * nuclear_lifetime

    # create the SLR functions
    fcn_exp = pulsed_exp(nuclear_lifetime, pulse_duration)
    fcn_strexp = pulsed_strexp(nuclear_lifetime, pulse_duration)

    # generate random values for the SLR fit function parameters that are uniformly
    # distributed between typical bounds for real data
    relaxation_rates = np.random.uniform(
        1e-2 * nuclear_lifetime, 1e2 * nuclear_lifetime, n_samples
    )
    amplitudes = np.random.uniform(0.00, 0.15, n_samples)

    # stretching exponent
    beta = 1.0

    # machine precision for floating point values
    epsilon = np.finfo(float).eps

    # create an empty DataFrame to hold all of the results
    df = pd.DataFrame(
        columns=[
            "Time (s)",
            "Amplitude",
            "Rate (1/s)",
            "Difference",
            "Absolute Difference",
            "Tolerance",
            "Tolerance Exceeded",
            "Epsilon",
            "Epsilon Exceeded",
        ]
    )

    # loop over the random function parameters
    for rate, amplitude in zip(relaxation_rates, amplitudes):

        # generate series of random times to evaluate the SLR fit functions that are
        # uniformly distributed between typical bounds for real data
        time = np.random.uniform(0.0, pulse_duration + 10 * nuclear_lifetime, n_samples)

        # evaluate the difference
        difference = fcn_exp(time, rate, amplitude) - fcn_strexp(
            time, rate, beta, amplitude
        )

        # fill the DataFrame row-by-row
        # https://stackoverflow.com/a/42837693
        for t, d in zip(time, difference):
            df = df.append(
                {
                    "Time (s)": t,
                    "Amplitude": amplitude,
                    "Rate (1/s)": rate,
                    "Difference": d,
                    "Absolute Difference": np.abs(d),
                    "Tolerance": tolerance,
                    "Tolerance Exceeded": np.abs(d) > tolerance,
                    "Epsilon": epsilon,
                    "Epsilon Exceeded": np.abs(d) < epsilon,
                },
                ignore_index=True,
            )

    # optionally print a summary of the results
    if print_summary:
        print("")
        print("-------")
        print("Summary of `test_numeric_integration()`")
        print("-------")
        print("")
        print("Tolerance        = %g" % tolerance)
        print("Machine Epsilon  = %g" % epsilon)
        print("")
        print("Absolute Difference:")
        print(" - Max  = %g" % df["Absolute Difference"].max())
        print(" - Min  = %g" % df["Absolute Difference"].min())
        print(" - Mean = %g" % df["Absolute Difference"].mean())
        print("")
        print("Column Data:")
        print("")
        print(df["Tolerance Exceeded"].value_counts())
        print("")
        print(df["Epsilon Exceeded"].value_counts())
        print("")

    # finally, check all values and raise an error if the tolerance is exceeded
    for i in df.index:
        if df["Tolerance Exceeded"][i]:
            raise AssertionError(
                "Absolute difference greater than tolerance!\n\n"
                + "\t|%.4e| > %.4e\n\n" % (df["Difference"][i], tolerance)
                + "\ttime      = %.4e s\n" % df["Time (s)"][i]
                + "\tamplitude = %.4e\n" % df["Amplitude"][i]
                + "\trate      = %.4e 1/s" % df["Rate (1/s)"][i]
            )
