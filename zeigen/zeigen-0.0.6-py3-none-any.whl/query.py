# -*- coding: utf-8 -*-
"""Query PDB for structures."""
# standard library imports
import datetime
import operator
import time
from functools import reduce
from pathlib import Path
from typing import Optional
from typing import Union

from loguru import logger
from rcsbsearch import Attr as RCSBAttr  # type: ignore
from rcsbsearch import rcsb_attributes  # type: ignore
from rcsbsearch.search import Terminal  # type: ignore
from statsdict import Stat

from .common import APP
from .common import STATS
from .rcsb_attributes import rcsb_attr_list

# import pandas as pd
# from .common import read_conf_file

OPERATOR_DICT = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}


@APP.command()
def rcsb_attributes_to_py() -> None:
    """Write RCSB attributes list as python code."""
    outfile = "rcsb_attributes.py"
    logger.info(f'Writing RCSB attributes list to "{outfile}".')
    with Path(outfile).open("w") as fp:
        date = datetime.date.today()
        fp.write(f'"""List of RCSB attributes as of {date}."""\n')
        fp.write("rcsb_attr_list = [\n")
        for attrib in rcsb_attributes:
            fp.write(f'    "{attrib.attribute}",\n')
        fp.write("]\n")


def rcsb_query(
    query_str: str, op_str: str, val: Union[int, float, str]
) -> Terminal:
    """Convert query specifiers to queries."""
    if query_str not in rcsb_attr_list:
        raise ValueError(f'Unrecognized RCSB query field "{query_str}"')
    try:
        op = OPERATOR_DICT[op_str]
    except KeyError:
        raise ValueError(
            f'Unrecognized RCSB operator string "{op_str}"'
        ) from None
    return op(RCSBAttr(query_str), val)


@APP.command()
@STATS.auto_save_and_report
def query(
    toml_file: Path,
    neutron: Optional[bool] = False,
) -> None:
    """Query PDB for X-ray or neutron structures."""
    if not neutron:
        expt_type = "xray"
        method = "X-RAY DIFFRACTION"
        resolution = 1.1
    else:
        expt_type = "neutron"
        method = "NEUTRON DIFFRACTION"
        resolution = 1.5
    query_list = [
        rcsb_query("exptl.method", "==", method),
        rcsb_query(
            "rcsb_entry_info.diffrn_resolution_high.value", "<=", resolution
        ),
        rcsb_query(
            "rcsb_accession_info.has_released_experimental_data", "==", "Y"
        ),
    ]
    logger.info(
        f"Querying RCSB for {expt_type} structures <= {resolution} Å resolution "
        + "with structure factors."
    )
    combined_query = reduce(operator.iand, query_list)
    start_time = time.time()
    results = list(combined_query())
    n_results = len(results)
    elapsed_time = round(time.time() - start_time, 1)
    logger.info(
        f"RCSB returned {n_results} {expt_type} structures in {elapsed_time} s."
    )
    STATS[f"{expt_type}_structures"] = Stat(n_results)
    STATS[f"{expt_type}_min_resolution"] = Stat(resolution, units="Å")
