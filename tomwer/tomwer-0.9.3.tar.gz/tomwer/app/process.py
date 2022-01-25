#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import argparse
from ewokscore import load_graph
from ewoksorange.bindings import owsconvert
from tomwer.core.scan.scanfactory import ScanFactory
import tempfile
import os
from pprint import pprint

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def exec_scans(name, ewoks_graph, scans=None, darkref_savedir=None):
    """

    :param ewoks_graph:
    :param scans: list of scan to execute
    :param timeout:
    :return:
    """

    def launch_():
        for scan in scans:
            exec_scan(name=name, ewoks_graph=ewoks_graph, scan=scan, save_dir=save_dir)

    if darkref_savedir is not None:
        if not os.path.exists(darkref_savedir):
            os.makedirs(darkref_savedir)
        launch_()
    else:
        with tempfile.TemporaryDirectory() as save_dir:
            launch_()


def exec_scan(name, ewoks_graph, scan, save_dir):
    # set up workflow
    if len(ewoks_graph.start_nodes()) == 0:
        _logger.warning("no start nodes found. Enable to process")
        return None
    mess = f"start processing {name} with {str(scan)}"
    _logger.info(mess)

    # update scan parameter to start node
    for src_node in ewoks_graph.start_nodes():
        # provide the dataset to be used and save_dir
        # save_dir is used to provide dark ref with a directory to store
        # dark and ref to be copy
        ewoks_graph.graph.nodes[src_node]["default_inputs"].add(
            {({"name": "data", "value": scan})}
        )

    # update node with dark ref
    import tomwer.core.process.reconstruction.darkref.darkrefscopy

    qual_name = ".".join(
        [
            tomwer.core.process.reconstruction.darkref.darkrefscopy.__name__,
            tomwer.core.process.reconstruction.darkref.darkrefscopy.DarkRefsCopy.__qualname__,
        ]
    )
    for src_node in ewoks_graph.graph.nodes:
        # provide save_dir to 'darkref' class
        if ewoks_graph.graph.nodes[src_node]["class"] == qual_name:
            ewoks_graph.graph.nodes[src_node]["default_inputs"].add(
                {({"name": "save_dir", "value": save_dir})}
            )
        # insure all arguments are provided for each link because the scan object is hidding some
        # parameters
        for target_node in ewoks_graph.graph.nodes:
            if src_node == target_node:
                continue
            try:
                ewoks_graph.graph[src_node][target_node]["all_arguments"] = True
                del ewoks_graph.graph[src_node][target_node]["arguments"]
            except KeyError:
                pass

    print(f" start execution of graph {name} ".center(80, "#"))
    taskgraph = load_graph(ewoks_graph)
    pprint(taskgraph.dump())
    print(f" end execution of graph {name} ".center(80, "#"))
    ewoks_graph.execute()


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workflow_file",
        help="Path to the .ows file defining the workflow to process with the"
        "provided scan",
    )
    parser.add_argument(
        "scan_path",
        help="Path to data to be processes (master file if come from an hdf5 "
        "acquisition or EDF files folder if come from an EDF acquisition)",
    )
    parser.add_argument(
        "--entry", default=None, help="An entry should be specify for hdf5 files"
    )
    parser.add_argument(
        "--timeout", default=None, help="Timeout for the workflow execution"
    )
    parser.add_argument(
        "--dkref-save-dir",
        default=None,
        dest="savedir",
        help="You can provide a save dir folder for the dark-ref copy task to"
        "insure persistency between several call of process.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )
    options = parser.parse_args(argv[1:])
    if options.entry is not None:
        scan = ScanFactory.create_scan_object(
            options.scan_path, entry=options.entry, accept_bliss_scan=True
        )
        scans = (scan,)
    else:
        scans = ScanFactory.create_scan_objects(
            options.scan_path, accept_bliss_scan=True
        )
    if len(scans) > 1:
        _logger.info("More than one scan found. Will process every scans")

    # tune the log level
    log_level = logging.INFO
    if options.debug is True:
        log_level = logging.DEBUG

    for log_ in ("tomwer", "ewoks", "ewoksorange", "ewokscore"):
        logging.getLogger(log_).setLevel(log_level)

    scheme = owsconvert.ows_to_ewoks(options.workflow_file)
    exec_scans(
        name=os.path.basename(options.workflow_file),
        ewoks_graph=scheme,
        scans=scans,
        darkref_savedir=options.savedir,
    )


if __name__ == "__main__":
    main(sys.argv)
