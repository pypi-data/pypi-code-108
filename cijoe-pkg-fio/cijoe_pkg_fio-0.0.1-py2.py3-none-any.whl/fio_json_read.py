#!/usr/bin/env python3
"""
Extract read metrics (iops, bwps, lat) from fio json data (fio-output* files)
"""

import os
from typing import List

from cij.runner import TestCase
from cij.analyser import to_base_unit
from cij.extractors.util import dump_metrics_to_file, parse_args_load_trun

from cijoe_extractors import fio_json

_MY_NAME = os.path.splitext(os.path.basename(__file__))[0]


def extract_metrics(tcase: TestCase) -> List[dict]:
    """
    Locate testcase fio-output files and parse them.
    Writes metrics to aux_root/metrics.yml and returns them.
    """

    metrics = []

    for fpath in fio_json.get_fio_output_files(tcase):
        pmetric = fio_json.parse_fio_output_file(fpath)
        if not pmetric:
            continue

        for n, job in enumerate(pmetric["jobs"]):
            ctx = fio_json.make_context(
                pmetric,
                extr_name=_MY_NAME,
                fname=os.path.basename(fpath),
                job_id=n,
                evars=tcase.evars,
            )
            name = "/".join(tcase.ident.split("/")[:-1])
            name = "_".join(name.split("_")[:-1])
            ctx["tsuite_name"] = name

            metrics.append({
                "ctx": ctx,
                "iops": to_base_unit(job["read"]["iops_mean"], ""),
                "bwps": to_base_unit(job["read"]["bw_mean"], "KiB"),
                "lat": to_base_unit(job["read"]["lat_ns"]["mean"], "nsec"),
                "stddev": to_base_unit(job["read"]["lat_ns"]["stddev"], ""),
            })

    if metrics:  # Only dump non-empty metrics
        dump_metrics_to_file(metrics, tcase.aux_root)

    return metrics


if __name__ == "__main__":
    """ Extract metrics if invoked directly """
    trun = parse_args_load_trun("fio_json_read")
    for tplan in trun.testplans:
        for tsuite in tplan.testsuites:
            for tcase in tsuite.testcases:
                extract_metrics(tcase)
