###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

__all__ = ["parse_bookkeeping_xml"]

from collections import namedtuple
from datetime import timedelta
from os.path import basename

from lxml import etree

InputFile = namedtuple("InputFile", ["path", "size", "dataset_size"])
OutputFile = namedtuple("OutputFile", ["path", "size", "dataset_size"])


def parse_bookkeeping_xml(fp, expected_input_files):
    """Extract information from the bookkeeping XML

    Parameters
    ----------
    fp : file-like
        File pointer of the XML summary
    expected_input_files : :obj:`list`
        List of object describing the expected input files

    Returns
    -------
    passed : :obj:`bool`
        True to the XML summary reports the job as passed
    """
    xml_bk = etree.parse(fp, base_url="LbAnalysisProductions/data/xml")
    events_processed = int(
        xml_bk.find('.//TypedParameter[@Name="NumberOfEvents"]').attrib["Value"]
    )
    events_requested = int(
        xml_bk.find('.//TypedParameter[@Name="StatisticsRequested"]').attrib["Value"]
    )
    run_time = timedelta(
        seconds=float(xml_bk.find('.//TypedParameter[@Name="CPUTIME"]').attrib["Value"])
    )
    cpu_norm = float(
        xml_bk.find('.//TypedParameter[@Name="WNCPUHS06"]').attrib["Value"]
    )
    input_files = _find_input_files(xml_bk, expected_input_files)
    output_files = _find_output_files(xml_bk, input_files)
    return (
        events_processed,
        events_requested,
        run_time,
        cpu_norm,
        input_files,
        output_files,
    )


def _find_input_files(xml_bk, expected_input_files):
    input_files = []
    for e in xml_bk.findall(".//InputFile"):
        input_file = expected_input_files(e.attrib["Name"])
        # fn = e.attrib["Name"]
        # for input_file in expected_input_files:
        #     if input_file.path == basename(fn):
        #         break
        # else:
        #     raise NotImplementedError(
        #         "Failed to find input file %s in %r" % (fn, expected_input_files)
        #     )
        input_files += [
            InputFile(
                path=input_file.path,
                size=input_file.size,
                dataset_size=input_file.dataset_size,
            )
        ]
    return input_files


def _find_output_files(xml_bk, input_files):
    output_files = []
    for f in xml_bk.findall(".//OutputFile"):
        if f.attrib["TypeName"] == "LOG":
            continue
        fn = basename(f.attrib["Name"])
        size = float(f.find('.//Parameter[@Name="FileSize"]').attrib["Value"])
        if len(set(f.dataset_size for f in input_files)) != 1:
            raise NotImplementedError(
                "This estimation hasn't been implemented for"
                "jobs with multiple input datasets"
            )
        dataset_size = int(
            size * input_files[0].dataset_size / sum(f.size for f in input_files)
        )
        output_files.append(OutputFile(path=fn, size=size, dataset_size=dataset_size))
    return output_files
