# -*- coding: utf-8 -*-
"""Find hydrated waters in structure."""
# standard library imports
from pathlib import Path

import pandas as pd
from loguru import logger
from statsdict import Stat

from .common import APP
from .common import read_conf_file
from .common import STATS


@APP.command()
@STATS.auto_save_and_report
def find(toml_file: Path) -> None:
    """Find hydrated waters in structure file."""
    conf = read_conf_file(toml_file, "configuration_file", "none")
    find_params = conf["find"]
    logger.info(f"find params={find_params}")
    output = "hydrated_waters.tsv"
    logger.info(f"writing file {output}")
    df = pd.DataFrame({"A": [1, 2, 3]})
    df.to_csv(output, sep="\t")
    STATS["n"] = Stat(1)
