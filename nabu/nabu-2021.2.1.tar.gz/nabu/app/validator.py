#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import h5py
import tomoscan.validator
from tomoscan.esrf.hdf5scan import HDF5TomoScan
from tomoscan.esrf.edfscan import EDFTomoScan


def get_scans(path, entries: str):
    path = os.path.abspath(path)
    res = []
    if EDFTomoScan.is_tomoscan_dir(path):
        res.append(EDFTomoScan(scan=path))
    elif HDF5TomoScan.is_tomoscan_dir(path):
        if entries == "__all__":
            entries = HDF5TomoScan.get_valid_entries(path)
        for entry in entries:
            res.append(HDF5TomoScan(path, entry))
    else:
        raise TypeError(
            f"{path} does not looks like a folder containing .EDF or a valid nexus file "
        )
    return res


def main():
    argv = sys.argv
    parser = argparse.ArgumentParser(
        description="Check if provided scan(s) seems valid to be reconstructed."
    )
    parser.add_argument("path", help="Data to validate (h5 file, edf folder)")
    parser.add_argument(
        "entries", help="Entries to be validated (in the case of a h5 file)", nargs="*"
    )
    parser.add_argument(
        "--ignore-dark",
        help="Do not check for dark",
        default=True,
        action="store_false",
        dest="check_dark",
    )
    parser.add_argument(
        "--ignore-flat",
        help="Do not check for flat",
        default=True,
        action="store_false",
        dest="check_flat",
    )
    parser.add_argument(
        "--no-phase-retrieval",
        help="Check scan energy, distance and pixel size",
        dest="check_phase_retrieval",
        default=True,
        action="store_false",
    )
    parser.add_argument(
        "--check-nan",
        help="Check frames if contains any nan.",
        dest="check_nan",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--skip-links-check",
        "--no-link-check",
        help="Check frames dataset if have some broken links.",
        dest="check_vds",
        default=True,
        action="store_false",
    )
    parser.add_argument(
        "--all-entries",
        help="Check all entries of the files (for HDF5 only for now)",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--extend",
        help="By default it only display items with issues. Extend will display them all",
        dest="only_issues",
        default=True,
        action="store_false",
    )

    options = parser.parse_args(argv[1:])
    if options.all_entries is True:
        entries = "__all__"
    else:
        if len(options.entries) == 0 and h5py.is_hdf5(options.path):
            entries = "__all__"
        else:
            entries = options.entries

    scans = get_scans(path=options.path, entries=entries)
    if len(scans) == 0:
        raise ValueError(
            f"No scan found from file:{options.path}, entries:{options.entries}"
        )
    for scan in scans:
        validator = tomoscan.validator.ReconstructionValidator(
            scan=scan,
            check_phase_retrieval=options.check_phase_retrieval,
            check_values=options.check_nan,
            check_vds=options.check_vds,
            check_dark=options.check_dark,
            check_flat=options.check_flat,
        )
        sys.stdout.write(validator.checkup(only_issues=options.only_issues))


if __name__ == "__main__":
    main()
