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

"""Module to make plots of LHCb PID calibration sample variables.

Examples:
    Create plots of the variables DLLK and P using 1 calibration file::

        $ python -m src.pidcalib2.plot_calib_distributions --sample=Turbo18 \
            --magnet=up --particle=Pi --bin-var=DLLK --bin-var=P \
            --output-dir=pidcalib_output --max-files=1

    Create PDF plots of variable P with 95 uniform bins using 1 calib. file::

        $ python -m src.pidcalib2.plot_calib_distributions --sample=Turbo18 \
            --magnet=up --particle=Pi --bin-var=P  --output-dir=pidcalib_output \
            --max-files=1 --format=pdf --force-uniform --bins=95

    Create plots of variable P using custom binning and 1 calib. file::

        $ python -m src.pidcalib2.plot_calib_distributions --sample=Turbo18 \
            --magnet=up --particle=Pi --bin-var=P  --output-dir=pidcalib_output \
            --max-files=1 --format=png --binning-file=my_binning.json
"""

import argparse
import logging
import pathlib
import pickle
import sys
from typing import Dict

import boost_histogram as bh
import logzero
import matplotlib
import mplhep
import numpy as np
from logzero import logger as log
from matplotlib import pyplot as plt
from tqdm import tqdm

from . import argparse_actions, binning, pid_data, utils

try:
    from .version import version  # type: ignore
except ImportError:
    version = "N/A"

# Avoid matplotlib trying to use QT based backends
matplotlib.use("agg")


def decode_arguments(args):
    """Decode CLI arguments."""
    parser = argparse.ArgumentParser(
        allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-s",
        "--sample",
        help="calibration sample (Turbo18, Electron16, ...)",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-m",
        "--magnet",
        help="magnet polarity",
        required=True,
        choices=["up", "down"],
    )
    parser.add_argument(
        "-p",
        "--particle",
        help="particle type; see pidcalib2.plot_calib_distributions --list configs",
        required=True,
    )
    parser.add_argument(
        "-b",
        "--bin-var",
        dest="bin_vars",
        help="variable to plot (-b can be specified multiple times)",
        action="append",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="directory where to save output files",
        default="pidcalib_output",
    )
    parser.add_argument(
        "-r",
        "--format",
        help="format of the plots",
        choices=["png", "pdf"],
        default="png",
    )
    parser.add_argument(
        "-g",
        "--binning-file",
        help="file where new/alternative binnings are defines",
    )
    parser.add_argument(
        "-a",
        "--samples-file",
        help="(debug) read calibration sample lists from a custom file",
    )
    parser.add_argument(
        "-i",
        "--bins",
        help="number of uniform bins to use when no binning exists",
        default=50,
        type=int,
    )
    parser.add_argument(
        "-u",
        "--force-uniform",
        help="force the usage of uniform binning even if other binning exists",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--cut",
        dest="cuts",
        help=(
            "arbitrary cut string, e.g., 'Dst_IPCHI2 < 10.0' (-c can be used multiple "
            "times for multiple cuts)."
        ),
        action="append",
    )
    parser.add_argument(
        "-l",
        "--list",
        action=argparse_actions.ListValidAction,
        help="list all [configs, aliases]",
    )
    parser.add_argument(
        "-f",
        "--file-list",
        help="(debug) read calibration file paths from a text file",
    )
    parser.add_argument(
        "-n",
        "--max-files",
        type=int,
        help="(debug) a max number of files to read",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="(debug) increase verbosity",
    )
    parser.add_argument("-V", "--version", action="version", version=version)
    return parser.parse_args(args)


def plot_calib_distributions(config: Dict) -> None:
    """Create, plot, and save histograms of a calibration sample.

    The specified calibration sample is processed with cuts taken into account.
    The requested variables are histogrammed, possibly with custom binning
    (specified in the same way as for make_eff_hists).

    Args:
        config: A configuration dictionary. See decode_arguments(args) for
            details.
    """
    if config["verbose"]:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    config["version"] = version
    log.info("Running PIDCalib2 plot_calib_distributions with the following config:")
    utils.log_config(config)

    output_dir = pathlib.Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

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
    tree_paths = pid_data.get_tree_paths(config["particle"], config["sample"])
    log.debug(f"Trees to be read: {tree_paths}")

    # If there are hard-coded cuts, the variables must be included in the
    # branches to read.
    cuts = config["cuts"]
    if "cuts" in calib_sample:
        if cuts is None:
            cuts = []
        cuts += calib_sample["cuts"]

    branch_names = pid_data.get_relevant_branch_names([], config["bin_vars"], cuts)
    log.info(f"Branches to be read: {branch_names}")
    log.info(
        f"{len(calib_sample['files'])} calibration files from EOS will be processed"
    )
    for path in calib_sample["files"]:
        log.debug(f"  {path}")

    if config["binning_file"]:
        binning.load_binnings(config["binning_file"])

    if config["force_uniform"]:
        log.info("Deleting binnings to force uniform binning")
        binning.binnings = {}

    all_hists = create_plot_histograms(config, calib_sample, tree_paths, branch_names)
    total_hists = utils.add_hists(list(all_hists.values()))

    save_histograms(total_hists, output_dir)
    save_plots(total_hists, output_dir, config["format"])


def create_plot_histograms(
    config, calib_sample, tree_paths, branch_names
) -> Dict[str, Dict[str, bh.Histogram]]:
    """Create histograms for plotting.

    A separate set of histograms is created for each file in the calib_sample.
    The set comprises histograms for each variable in branch_names.

    Args:
        config: A configuration dictionary. See decode_arguments(args) for
            details.
        calib_sample: Calibration sample - files, cuts, etc.
        tree_paths: List of internal ROOT paths to relevant trees in the files.
        branch_names: Dict of branch names {user-level name: branch name}.

    Returns:
        A dictionary {file: {var: histogram}}.
    """
    bin_vars_without_binnings = []
    binning_range_cuts = []
    for bin_var in config["bin_vars"]:
        try:
            bin_edges = binning.get_binning(
                config["particle"], bin_var, verbose=True, quiet=True
            )
            binning_range_cuts.append(
                f"{bin_var} > {bin_edges[0]} and {bin_var} < {bin_edges[-1]}"
            )
        except KeyError:
            log.warning(
                (
                    f"No '{bin_var}' binning defined for particle "
                    f"{config['particle']}; will use {config['bins']} uniform bins"
                )
            )
            bin_vars_without_binnings.append(bin_var)

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

            utils.apply_all_cuts(
                df,
                cut_stats,
                binning_range_cuts,
                calib_sample["cuts"] if "cuts" in calib_sample else [],
                config["cuts"] if "cuts" in config else [],
            )

            # If no binning
            for var in bin_vars_without_binnings:
                range = df[var].max() - df[var].min()  # type: ignore
                min = df[var].min() - 0.1 * range
                max = df[var].max() + 0.1 * range
                binning.set_binning(
                    config["particle"],
                    var,
                    list(np.linspace(min, max, config["bins"] + 1)),
                )
            # Empty the list to avoid redefining the binning in each step
            bin_vars_without_binnings = []

            hists = {
                var: utils.make_hist(df, config["particle"], [var])
                for var in config["bin_vars"]
            }

            all_hists[path] = hists

    log.info(f"Processed {len(all_hists)}/{len(calib_sample['files'])} files")
    utils.print_cut_summary(cut_stats)

    return all_hists


def save_plots(
    total_hists: Dict[str, bh.Histogram], output_dir: pathlib.Path, format: str
) -> None:
    """Create and save plots of the supplied 1D histograms.

    Args:
        total_hists: A dictionary of the histograms to be plotted.
        output_dir: Directory to which to save the plots.
        format: Image format, e.g., png.
    """
    try:
        # New mplhep style setting
        mplhep.style.use("LHCb2")
    except AttributeError:
        # Fallback to old mplhep style setting
        mplhep.set_style("LHCb2")

    for var, hist in total_hists.items():
        plt.hist(
            hist.axes[0].edges[:-1],
            bins=hist.axes[0].edges,
            weights=hist.values(),
            histtype="step",
        )
        plt.ylabel("Events")
        plt.xlabel(var)
        plt.tight_layout()
        path = output_dir / pathlib.Path(var + "." + format)
        log.info(f"Saving plot {path}")
        plt.savefig(path, dpi=100)
        plt.close()


def save_histograms(
    total_hists: Dict[str, bh.Histogram], output_dir: pathlib.Path
) -> None:
    """Pickle histograms and save them to a file.

    Args:
        total_hists: A dictionary of the histograms to be plotted.
        output_dir: Directory to which to save the histograms.
    """
    path = output_dir / pathlib.Path("plot_calib_distributions.pkl")
    log.info(f"Saving histograms to {path}")
    with open(path, "wb") as f:
        for hist in total_hists.values():
            pickle.dump(hist, f)


def main():
    config = vars(decode_arguments(sys.argv[1:]))
    plot_calib_distributions(config)


if __name__ == "__main__":
    main()
