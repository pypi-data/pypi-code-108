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

"""Module that calculates the LHCb PID efficiency of a reference sample.

This module uses the histograms created by make_eff_hists to assign
efficiency to events in a reference sample supplied by the user. Adding of
efficiency to the user-supplied file requires PyROOT and is optional.

The module works in two steps:

1. Calculate the efficiency and save it as a TTree in a separate file.
2. Optionally copy the efficiency TTree to the reference file and make it a friend of
   the user's TTree.

The second step is an efficient way of "adding" the efficiency branches to
the user's TTree. The step must be requested by specifying --merge on the
command line.

Examples:
    Evaluate efficiency of a single PID cut and add it to the reference file::

        $ python -m src.pidcalib2.ref_calib --sample=Turbo18 --magnet=up \
            --ref-file=data/user_ntuple.root --output-dir=pidcalib_output \
            --bin-vars='{"P": "mom", "ETA": "Eta", "nSPDHits": "nSPDhits"}' \
            --ref-pars='{"Bach": ["K", "DLLK > 4"]}'


    Evaluate efficiency of a single PID cut and save it to
    user_ntuple_PID_eff.root without adding it to user_ntuple.root::

        $ python -m src.pidcalib2.ref_calib --sample=Turbo18 --magnet=up \
            --ref-file=data/user_ntuple.root --output-dir=pidcalib_output \
            --bin-vars='{"P": "mom", "ETA": "Eta", "nSPDHits": "nSPDhits"}' \
            --ref-pars='{"Bach": ["K", "DLLK > 4"]}'

    Evaluate efficiency of multiple PID cuts and add them to the reference
    file::

        $ python -m src.pidcalib2.ref_calib --sample=Turbo18 --magnet=up \
            --ref-file=data/user_ntuple.root --output-dir=pidcalib_output \
            --bin-vars='{"P": "P", "ETA": "ETA", "nSPDHits": "nSPDHits"}' \
            --ref-pars='{"Bach": ["K", "DLLK > 4"], "SPi": ["Pi", "DLLK < 0"]}'
"""

import argparse
import ast
import logging
import pathlib
import sys
import time
from typing import Dict

import logzero
from logzero import logger as log

from . import argparse_actions, merge_trees, pid_data, utils

try:
    from .version import version  # type: ignore
except ImportError:
    version = "N/A"


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
        "-b",
        "--bin-vars",
        help=(
            "dictionary of binning variables (keys) and their associated names in "
            "the reference sample (values)"
        ),
        default="{'P' : 'P', 'ETA' : 'ETA', 'nTracks' : 'nTracks'}",
        dest="bin_vars",
    )
    parser.add_argument(
        "-i",
        "--histo-dir",
        default="pidcalib_output",
        help="directory where efficiency histograms are located",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="ROOT filename into which to save the PID efficiency tree",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--ref-file",
        help="reference sample file",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--ref-tree",
        help="reference sample tree name",
        default="DecayTree",
    )
    parser.add_argument(
        "-p",
        "--ref-pars",
        help=(
            "JSON dictionary of particles from reference sample to apply "
            "cuts to, where the keys represent the particle branch name prefix, "
            "and the values passed are a list containing particle type and "
            "PID cut e.g. \"{'D0_K' : ['K','DLLK>4'], 'D0_Pi' : ['Pi','DLLK<4']}\""
        ),
        required=True,
    )
    parser.add_argument(
        "-r",
        "--merge",
        help="merge the PID efficiency tree with the reference file",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--compatibility",
        action="store_true",
        help="(debug) treat empty efficiency histogram bins as PIDCalib1 did",
    )
    parser.add_argument(
        "-l",
        "--list",
        action=argparse_actions.ListValidAction,
        help="list all [configs, aliases]",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="(debug) increase verbosity",
    )
    parser.add_argument("-V", "--version", action="version", version=version)
    return parser.parse_args(args)


def ref_calib(config: Dict) -> float:
    """Assign efficiency to tracks and events in a user-supplied dataset.

    Each track that falls within the phasespace covered by the efficiency
    histogram is assigned efficiency of the bin it falls into. The overall
    event efficiency is a product of all the track efficiencies. The
    resulting efficiency columns/branches are saved to a TTree in a file
    <reference_filename>_PID_eff.root. The TTree is then copied to the
    reference (user) file and made a friend TTree of the original TTree
    specified by the user. This allows the user to treat their original TTree
    as if it itself had the efficiency branches.

    Args:
        config: A configuration dictionary. See decode_arguments(args) for
            details.

    Returns:
        Average efficiency of all the events.
    """
    if config["verbose"]:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    config["version"] = version
    log.info("Running PIDCalib2 ref_calib with the following config:")
    utils.log_config(config)

    try:
        bin_vars = ast.literal_eval(config["bin_vars"])
        if not isinstance(bin_vars, dict):
            raise SyntaxError
    except SyntaxError:
        log.error("The --bin-vars string is not a valid Python dict")
        raise

    try:
        ref_pars = ast.literal_eval(config["ref_pars"])
        if not isinstance(ref_pars, dict):
            raise SyntaxError
    except SyntaxError:
        log.error("The --ref-pars string is not valid Python dict")
        raise

    eff_histos = pid_data.get_calib_hists(
        config["histo_dir"], config["sample"], config["magnet"], ref_pars, bin_vars
    )

    log.info(f"Loading reference sample '{config['ref_file']}' ...")
    ref_branches = pid_data.get_reference_branch_names(ref_pars, bin_vars)
    df_ref = pid_data.root_to_dataframe(
        config["ref_file"], [config["ref_tree"]], ref_branches
    )
    log.debug(
        f"Reference sample '{config['ref_file']}' with {len(df_ref.index)} events loaded"  # noqa
    )

    start = time.perf_counter()
    df_ref = utils.add_bin_indices(df_ref, list(ref_pars), bin_vars, eff_histos)
    df_ref = utils.add_efficiencies(df_ref, list(ref_pars), eff_histos)
    end = time.perf_counter()
    log.debug(f"Efficiency calculation took {end-start:.2f}s")

    # Calculate average of the per-event effs
    # Use only data with valid eff values (those events falling inside the
    # calibration hist)
    avg_eff = df_ref["PIDCalibEff"].dropna().mean()
    log.info(f"Average per-event PID efficiency: {avg_eff:.2%}")

    output_path = pathlib.Path(config["output_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pid_data.save_dataframe_as_root(
        df_ref[[key for key in df_ref.keys() if key not in ref_branches]],
        "PIDCalibTree",
        str(output_path),
    )

    if config["merge"]:
        merge_trees.copy_tree_and_set_as_friend(
            str(output_path), "PIDCalibTree", config["ref_file"], config["ref_tree"]
        )

    return avg_eff  # type: ignore


def main():
    config = vars(decode_arguments(sys.argv[1:]))
    ref_calib(config)


if __name__ == "__main__":
    main()
