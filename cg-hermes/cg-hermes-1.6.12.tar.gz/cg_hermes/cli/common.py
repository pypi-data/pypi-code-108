"""Store common utilities"""
import json
import logging
from json.decoder import JSONDecodeError
from pathlib import Path

import typer
import yaml
from yaml.parser import ParserError

LOG = logging.getLogger(__name__)


def get_deliverables(infile: Path) -> dict:
    """Open file and load into dict

    Try first open yaml, then json.
    """
    with open(infile, "r") as handle:
        try:
            deliverables = yaml.load(handle, Loader=yaml.SafeLoader)
        except ParserError as err:
            LOG.error(err)
            LOG.warning("File %s is not in yaml format", infile)
            try:
                deliverables = json.load(handle)
            except JSONDecodeError as err:
                LOG.error(err)
                LOG.warning("File %s is not in json format", infile)
                LOG.warning("Can not parse file")
                raise typer.Abort()
        return deliverables
