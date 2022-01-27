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

"""Copy tree from a file and set it as friend of a tree in another file.

PIDCalib2.ref_calib creates a file with a tree where the efficiency for each
track and event from the user's reference sample is stored. This PID
efficiency information has to be added to the existing event information.
This script is used to copy the efficiency tree to the user's reference file
and set it as a friend of the reference tree. This way one can use the
reference tree as if it had the branches from the efficiency tree.

Example:
    $ python -m pidcalib2.merge_trees eff.root eff_tree ref.root DecayTree
"""

import sys
from pathlib import Path

import ROOT
from logzero import logger as log


def copy_tree_and_set_as_friend(
    source_file_name: str,
    source_tree_name: str,
    dest_file_name: str,
    dest_tree_name: str,
) -> None:
    """Copy tree from a file and set it as friend of a tree in another file.

    Args:
        source_file_name: File from which to copy the tree.
        source_tree_name: Name of the tree to be copied.
        dest_file_name: File to which to copy the tree.
        dest_tree_name: Name of the tree on which to call AddFriend.
    """
    source_file = ROOT.TFile(source_file_name, "read")
    source_tree = source_file.Get(source_tree_name)
    log.info(f"Reading {source_tree_name} from {source_file_name}")
    if not source_tree:
        log.error(f"'{source_tree_name}' not found in '{source_file_name}'.")
        sys.exit(1)

    if not Path(dest_file_name).exists():
        log.error(f"'{dest_file_name}' not found.")
        sys.exit(3)

    dest_file = ROOT.TFile(dest_file_name, "update")
    dest_file.cd()

    log.info(f"Reading {dest_tree_name} from {dest_file_name}")
    dest_tree = dest_file.Get(dest_tree_name)
    if not dest_tree:
        log.error(f"'{dest_tree_name}' not found in '{dest_file_name}'.")
        sys.exit(2)

    log.info(f"Copying {source_tree_name} to {dest_file_name}")
    source_tree.CloneTree().Write()

    dest_tree.AddFriend(source_tree_name)

    # Avoid ROOT adding a new tree with an incremented cycle number
    dest_tree.Write("", ROOT.TObject.kOverwrite)

    dest_file.Close()


def main():
    copy_tree_and_set_as_friend(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


if __name__ == "__main__":
    main()
