###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import difflib
import re
import sys
from typing import Any, Dict, List, Tuple, Union

import boost_histogram as bh
import numpy as np
import pandas as pd
from logzero import logger as log
from tqdm import tqdm

from . import binning, pid_data


def make_hist(df: pd.DataFrame, particle: str, bin_vars: List[str]) -> bh.Histogram:
    """Create a histogram of sWeighted events with appropriate binning

    Args:
        df: DataFrame from which to histogram events.
        particle: Particle type (K, Pi, etc.).
        bin_vars: Binning variables in the user-convention, e.g., ["P", "ETA"].
    """
    axis_list = []
    vals_list = []

    # Loop over bin dimensions and define the axes
    for bin_var in bin_vars:
        bin_edges = binning.get_binning(particle, bin_var)
        axis_list.append(bh.axis.Variable(bin_edges, metadata={"name": bin_var}))
        vals = df[bin_var].values
        vals_list.append(vals)

    # Create boost-histogram with the desired axes, and fill with sWeight applied
    hist = bh.Histogram(*axis_list, storage=bh.storage.Weight())
    hist.fill(*vals_list, weight=df["sWeight"])

    return hist


def create_eff_histograms(hists: Dict[str, bh.Histogram]) -> Dict[str, bh.Histogram]:
    """Create efficiency histograms for all supplied PID cuts.

    Args:
        hists: A dictionary with total and passing histograms.

    Returns:
        A dictionary with all the efficiency histograms, with the PID cuts as
        keys.
    """
    zero_bins = np.count_nonzero(hists["total"].values(flow=False) == 0)
    if zero_bins:
        log.warning(
            (
                f"There are {zero_bins} empty bins in the total histogram! "
                "You might want to change the binning."
            )
        )
        log.debug(hists["total"].values(flow=False))

        # Replace zeros with NaNs which suppresses duplicate Numpy warnings
        hist_total_nan = hists["total"].values()
        hist_total_nan[hist_total_nan == 0] = np.nan
        hists["total"].view().value = hist_total_nan  # type: ignore

    for name in list(hists):
        if name.startswith("passing_"):
            eff_name = name.replace("passing_", "eff_", 1)
            hists[eff_name] = hists[name].copy()
            hists[eff_name].view().value = hists[name].values(flow=False) / hists[  # type: ignore # noqa
                "total"
            ].values(
                flow=False
            )
            hists[eff_name].view().variance = np.square(  # type: ignore
                binomial_uncertainty(
                    hists[name].values(flow=False),
                    hists["total"].values(flow=False),
                    hists[name].variances(flow=False),  # type: ignore
                    hists["total"].variances(flow=False),  # type: ignore
                )
            )
            log.debug(f"Created '{eff_name}' histogram")

            negative_bins = np.count_nonzero(hists[eff_name].values(flow=False) < 0)
            if negative_bins:
                log.warning(
                    (
                        f"There are {negative_bins} negative bins in the '{eff_name}' "
                        "efficiency histogram! You might want to change the binning."
                    )
                )
                log.debug(hists[eff_name].values(flow=False))

    if zero_bins:
        # Return the zeros that were temporarily replaced by NaNs
        hists["total"].view().value = np.nan_to_num(  # type:ignore
            hists["total"].view().value  # type:ignore
        )

    return hists


def log_config(config: dict) -> None:
    """Pretty-print a config/dict."""
    longest_key = len(max(config, key=len))
    log.info("=" * longest_key)
    for entry, value in config.items():
        if value is not None:
            log.info(f"{entry:{longest_key}}: {value}")
    log.info("=" * longest_key)


def add_bin_indices(
    df: pd.DataFrame,
    prefixes: List[str],
    bin_vars: Dict[str, str],
    eff_hists: Dict[str, Dict[str, bh.Histogram]],
) -> pd.DataFrame:
    """Return a DataFrame with added indices of bins for each event.

    The binnings of binning variables are taken from efficiency histograms.
    Each event falls into a certain bin in each binning variable. This bin's
    index is added to the DataFrame. The same procedure is repeated for each
    variable. Finally, a global index of the N-dimensional bin of the
    efficiency histogram where the event belongs is added. Multiple
    efficiency histograms can be specified since the total PID efficiency for
    the event can depend on multiple particles.

    Args:
        df: Input dataframe.
        prefixes: Branch prefixes of the particles in the reference sample.
        bin_vars: Variables used for binning.
        eff_hists: Efficiency histograms for each prefix/particle.
    """
    df_new = df.copy()
    for prefix in prefixes:
        eff_histo = eff_hists[prefix]["eff"]
        axes = [
            pid_data.get_reference_branch_name(
                prefix, axis.metadata["name"], bin_vars[axis.metadata["name"]]
            )
            for axis in eff_histo.axes
        ]
        for bin_var, branch_name in bin_vars.items():
            ref_branch_name = pid_data.get_reference_branch_name(
                prefix, bin_var, branch_name
            )
            bins = []
            for axis in eff_histo.axes:
                if axis.metadata["name"] == bin_var:
                    bins = axis.edges
            df_new[f"{ref_branch_name}_PIDCalibBin"] = pd.cut(
                df_new[ref_branch_name],
                bins,
                labels=False,
                include_lowest=True,
                right=False,
                precision=0,
            )

        df_nan = df_new[df_new.isna().any(axis=1)]  # type: ignore
        df_new.dropna(inplace=True)
        index_names = [f"{axis}_PIDCalibBin" for axis in axes]
        indices = np.ravel_multi_index(
            df_new[index_names].transpose().to_numpy().astype(int),
            eff_histo.axes.size,
        )
        df_new[f"{prefix}_PIDCalibBin"] = indices
        df_new = pd.concat([df_new, df_nan]).sort_index()  # type: ignore
    log.debug("Bin indices assigned")
    return df_new  # type: ignore


def add_efficiencies(
    df: pd.DataFrame,
    prefixes: List[str],
    eff_hists: Dict[str, Dict[str, bh.Histogram]],
    compatibility: bool = False,
) -> pd.DataFrame:
    """Return a DataFrame with added efficiencies for each event.

    Each particle correspondig to a prefix is assigned an efficiency. The
    total event efficiency is the product of individual efficiencies.

    Args:
        df: Input dataframe.
        prefixes: Branch prefixes of the particles in the reference sample.
        eff_hists: Efficiency histograms for each prefix/particle.
        compatibility: Treat empty efficiency histogram bins as PIDCalib1 did
    """
    df_new = df.copy()

    # We separate the dataframe into two parts: one where all the events have
    # PID indices (events inside the PID binning) and those that don't.
    # Efficiency is added only for events inside the PID binning.
    df_nan = df_new[df_new.isna().any(axis=1)]  # type: ignore
    df_new.dropna(inplace=True)

    df_new["PIDCalibEff"] = 1
    df_new["PIDCalibRelErr2"] = 0

    for prefix in prefixes:
        efficiency_table = eff_hists[prefix]["eff"].values().flatten()
        error_table = np.sqrt(eff_hists[prefix]["eff"].variances().flatten())  # type: ignore # noqa

        # The original PIDCalib assigned bins with no events in the total
        # histogram an efficiency of zero. This should not come up often and the
        # user should be warned about it. In any case it does not seem right -
        # we assign the bin a NaN. This might cause slightly different results
        # when using a sample and binning that lead to such empty bins.
        if compatibility:
            np.nan_to_num(efficiency_table, copy=False)  # Replicate PIDCalib1 behavior

        # Assign efficiencies by taking the efficiency value from the relevant bin
        df_new[f"{prefix}_PIDCalibEff"] = np.take(
            efficiency_table, df_new[f"{prefix}_PIDCalibBin"]
        )
        # Assign errors by taking the error value from the relevant bin
        df_new[f"{prefix}_PIDCalibErr"] = np.take(
            error_table, df_new[f"{prefix}_PIDCalibBin"]
        )
        df_new["PIDCalibEff"] *= df_new[f"{prefix}_PIDCalibEff"]
        df_new["PIDCalibRelErr2"] += (
            df_new[f"{prefix}_PIDCalibErr"] / df_new[f"{prefix}_PIDCalibEff"]
        ) ** 2

    df_new["PIDCalibErr"] = np.sqrt(df_new["PIDCalibRelErr2"])  # type: ignore
    for prefix in prefixes:
        # The absolute value is so that we match PIDCalib1. However if any of
        # the efficiencies are negative the overall efficiency and error are
        # meaningless.
        df_new["PIDCalibErr"] *= df_new[f"{prefix}_PIDCalibEff"]  # type: ignore
    df_new.drop(columns=["PIDCalibRelErr2"], inplace=True)

    # Assign -999 to events where any track has negative efficiency; this
    # behavior is different to the original PIDCalib
    negative_mask = df_new.eval(
        "|".join(f"{prefix}_PIDCalibEff<0" for prefix in prefixes)
    )

    if any(negative_mask):
        df_new.loc[negative_mask, ["PIDCalibEff"]] = -999
        df_new.loc[negative_mask, ["PIDCalibErr"]] = -999
        log.warning(
            (
                f"{np.count_nonzero(negative_mask)} events include tracks with "
                "negative efficiencies; assigning -999"
            )
        )

    df_new = pd.concat([df_new, df_nan]).sort_index()
    log.debug("Particle efficiencies assigned")

    num_outside_range = len(df_nan.index)
    num_outside_range_frac = len(df_nan.index) / len(df_new.index)
    log.warning(
        (
            "Events out of binning range: "
            f"{num_outside_range} ({num_outside_range_frac:.2%})"
        )
    )
    return df_new


def create_hist_filename(
    sample: str, magnet: str, particle: str, pid_cut: str, bin_vars: List[str]
) -> str:
    """Return effhists filename corresponding to parameters.

    Args:
        sample: Data sample name (Turbo18, etc.).
        magnet: Magnet polarity (up, down).
        particle: Particle type (K, Pi, etc.).
        pid_cut: Simplified user-level cut, e.g., "DLLK < 4".
        bin_vars: Variables used for binning.
    """
    whitespace = re.compile(r"\s+")
    cut = re.sub(whitespace, "", pid_cut)

    return f"effhists-{sample}-{magnet}-{particle}-{cut}-{'.'.join(bin_vars)}.pkl"


def binomial_uncertainty(
    num_pass: Union[float, np.ndarray],
    num_total: Union[float, np.ndarray],
    err_pass_sq: Union[float, np.ndarray],
    err_tot_sq: Union[float, np.ndarray],
) -> float:
    """Return the uncertainty of binomial experiments.

    The parameters can be either floats or numpy arrays.

    The uncertainty is calculated the way ROOT does it in TH1::Divide() when
    binomial errors are specified. This approach has known problems when
    num_pass == num_total or 0. We use this approach to ensure compatibility
    with the original PIDCalib, and because these edge-cases are unlikely to
    occur.

    Args:
        num_pass: Number of passing events.
        num_total: Total number of events.
        err_pass_sq: Squared uncertainty on the number of passing events (sum
            of squares of the event weights).
        err_tot_sq: Squared uncertainty on the number of total events (sum of
            squares of the event weights).
    """
    prob = num_pass / num_total
    prob_sq = prob ** 2  # type: ignore
    num_total_sq = num_total ** 2  # type: ignore
    return np.sqrt(  # type: ignore
        abs(((1 - 2 * prob) * err_pass_sq + err_tot_sq * prob_sq) / num_total_sq)
    )


def create_error_histogram(eff_hists: Dict[str, bh.Histogram]) -> bh.Histogram:
    uncertainty = binomial_uncertainty(
        eff_hists["passing"].view(flow=False),  # type: ignore
        eff_hists["total"].view(flow=False),  # type: ignore
        eff_hists["passing_sumw2"].view(flow=False),  # type: ignore
        eff_hists["total_sumw2"].view(flow=False),  # type: ignore
    )

    err_histo = eff_hists["passing"].copy()
    err_histo[...] = uncertainty
    return err_histo


def apply_cuts(df: pd.DataFrame, cuts: List[str]) -> Tuple[int, int]:
    cut_string = " and ".join(cuts)
    num_before = df.shape[0]
    df.query(cut_string, inplace=True)
    num_after = df.shape[0]
    log.debug(
        f"{num_after}/{num_before} ({num_after/num_before:.1%}) events passed cuts"
    )
    return num_before, num_after


def extract_variable_names(expression: str) -> List[str]:
    """Extract variable names from simple math expressions.

    This is useful to extract var names from PID cuts

    Args:
        expression: The expression to parse.

    Returns:
        A list of variable names found in the expression.
    """
    parts = re.split(r"<|>|==|!=|\(|\)|\*|/|\+|-|\^|&", expression)
    var_names = [part for part in parts if not is_float(part) and part != ""]
    # Check that the user uses valid variable names in cuts
    for var_name in var_names:
        if not re.match("^[A-Za-z0-9_]+$", var_name):
            if "=" in var_name:
                log.error("A single '=' used in a cut. Did you mean '=='?")
                raise SyntaxError
            else:
                log.error(f"'{var_name}' is not a valid variable name")
                raise KeyError
    return var_names


def is_float(entity: Any) -> bool:
    """Check if an entity can be converted to a float.

    Args:
        entity: Could be string, int, or many other things.
    """
    try:
        float(entity)
        return True
    except ValueError:
        return False


def find_similar_strings(
    comparison_string: str, list_of_strings: List[str], ratio: float
) -> List[str]:
    """Return a list of strings similar to the comparison string.

    Args:
        comparison_string: The string against which to compare.
        list_of_strings: List of strings to search.
        ratio: Minimal SequenceMatcher similarity ratio.
    """
    similar_strings = {}
    for string in list_of_strings:
        string_ratio = difflib.SequenceMatcher(
            None, comparison_string.lower(), string.lower()
        ).ratio()
        if string_ratio > ratio:
            similar_strings[string] = string_ratio

    sorted_similar_strings = sorted(
        similar_strings.items(), key=lambda x: x[1], reverse=True
    )

    return [string for string, ratio in sorted_similar_strings]


def add_hists(all_hists: List[Dict[str, bh.Histogram]]) -> Dict[str, bh.Histogram]:
    """Add a list of histograms in dictionaries.

    Args:
        all_hists: List of dictionaries with histograms to add.

    Returns:
        A dictionary of histograms with the same structure as any
        single dictionary that went into the merge.
    """
    total_hists = all_hists[0]
    for hist_dict in all_hists[1:]:
        for name in total_hists:
            total_hists[name] += hist_dict[name]
    return total_hists


def create_histograms(config):
    calib_sample = {}
    if config["file_list"]:
        with open(config["file_list"]) as f_list:
            calib_sample["files"] = f_list.read().splitlines()
    else:
        calib_sample = pid_data.get_calibration_sample(
            config["sample"],
            config["magnet"],
            config["particle"],
            config["samples_file"],
            config["max_files"],
        )
    tree_paths = pid_data.get_tree_paths(
        config["particle"],
        config["sample"],
        calib_sample["tuple_names"] if "tuple_names" in calib_sample else None,
    )
    log.debug(f"Trees to be read: {tree_paths}")

    # If there are hard-coded cuts, the variables must be included in the
    # branches to read.
    cuts = config["cuts"]
    if "cuts" in calib_sample:
        if cuts is None:
            cuts = []
        cuts += calib_sample["cuts"]

    branch_names = pid_data.get_relevant_branch_names(
        config["pid_cuts"], config["bin_vars"], cuts
    )
    log.info(f"Branches to be read: {branch_names}")
    log.info(
        f"{len(calib_sample['files'])} calibration files from EOS will be processed"
    )
    for path in calib_sample["files"]:
        log.debug(f"  {path}")

    binning_range_cuts = []
    for bin_var in config["bin_vars"]:
        bin_edges = binning.get_binning(config["particle"], bin_var, verbose=True)
        binning_range_cuts.append(
            f"{bin_var} >= {bin_edges[0]} and {bin_var} < {bin_edges[-1]}"
        )

    cut_stats = {
        "binning range": {"before": 0, "after": 0},
        "hard-coded": {"before": 0, "after": 0},
        "user": {"before": 0, "after": 0},
    }
    all_hists = {}

    for path in (
        tqdm(calib_sample["files"], leave=False, desc="Processing files")
        if sys.stderr.isatty()  # Use tqdm only when running interactively
        else calib_sample["files"]
    ):
        df = pid_data.root_to_dataframe(
            path, tree_paths, list(branch_names.values()), True
        )
        if df is not None:
            # Rename colums of the dataset from branch names to simple user-level
            # names, e.g., probe_PIDK -> DLLK.
            inverse_branch_dict = {val: key for key, val in branch_names.items()}
            df = df.rename(columns=inverse_branch_dict)  # type: ignore

            apply_all_cuts(
                df,
                cut_stats,
                binning_range_cuts,
                calib_sample["cuts"] if "cuts" in calib_sample else [],
                config["cuts"] if "cuts" in config else [],
            )

            hists = {"total": make_hist(df, config["particle"], config["bin_vars"])}
            hists_passing = create_passing_histograms(
                df,
                cut_stats,
                config["particle"],
                config["bin_vars"],
                config["pid_cuts"],
            )

            # Merge dictionaries
            hists = {**hists, **hists_passing}
            all_hists[path] = hists

    log.info(f"Processed {len(all_hists)}/{len(calib_sample['files'])} files")
    print_cut_summary(cut_stats)
    return all_hists


def create_histograms_from_local_dataframe(config):
    branch_names = pid_data.get_relevant_branch_names(
        config["pid_cuts"], config["bin_vars"], config["cuts"]
    )
    df = pid_data.dataframe_from_local_file(
        config["local_dataframe"], list(branch_names)
    )
    if config["cuts"]:
        log.debug(f"Applying user cuts: '{config['cuts']}'")
        num_before, num_after = apply_cuts(df, config["cuts"])

    particle = config["particle"]
    bin_vars = config["bin_vars"]
    pid_cuts = config["pid_cuts"]

    hists = {"total": make_hist(df, particle, bin_vars)}
    for i, pid_cut in enumerate(pid_cuts):
        log.info(f"Processing '{pid_cuts[i]}' cut")
        df_passing = df.query(pid_cut)
        hists[f"passing_{pid_cut}"] = make_hist(df_passing, particle, bin_vars)
        log.debug("Created 'passing' histogram")

    return hists


def apply_all_cuts(
    df: pd.DataFrame,
    cut_stats: Dict[str, Dict[str, int]],
    binning_range_cuts: List[str],
    hardcoded_cuts: List[str],
    user_cuts: List[str],
) -> Dict[str, Dict[str, int]]:

    if binning_range_cuts:
        log.debug(f"Applying binning range cuts: {binning_range_cuts}'")
        num_before, num_after = apply_cuts(df, binning_range_cuts)
        cut_stats["binning range"]["before"] += num_before
        cut_stats["binning range"]["after"] += num_after

    if hardcoded_cuts:
        log.debug(f"Applying hard-coded cuts: {hardcoded_cuts}'")
        num_before, num_after = apply_cuts(df, hardcoded_cuts)
        cut_stats["hard-coded"]["before"] += num_before
        cut_stats["hard-coded"]["after"] += num_after

    if user_cuts:
        log.debug(f"Applying user cuts: '{user_cuts}'")
        num_before, num_after = apply_cuts(df, user_cuts)
        cut_stats["user"]["before"] += num_before
        cut_stats["user"]["after"] += num_after

    return cut_stats


def create_passing_histograms(df, cut_stats, particle, bin_vars, pid_cuts):
    hists = {}
    num_total = len(df.index)
    for i, pid_cut in enumerate(pid_cuts):
        log.debug(f"Processing '{pid_cuts[i]}' cut")
        df_passing = df.query(pid_cut)
        hists[f"passing_{pid_cut}"] = make_hist(df_passing, particle, bin_vars)
        log.debug("Created 'passing' histogram")
        if f"'{pid_cut}'" not in cut_stats:
            cut_stats[f"'{pid_cut}'"] = {"before": 0, "after": 0}
        cut_stats[f"'{pid_cut}'"]["after"] += len(df_passing.index)
        cut_stats[f"'{pid_cut}'"]["before"] += num_total
    return hists


def print_cut_summary(cut_stats: Dict[str, Dict[str, int]]):
    for name, cut_stat in cut_stats.items():
        num_after = cut_stat["after"]
        num_before = cut_stat["before"]
        if num_before != 0:
            log.info(
                (
                    f"{num_after}/{num_before} "
                    f"({num_after/num_before:.1%}) events passed {name} cut"
                )
            )
