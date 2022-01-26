"""CLI for converting between formats"""

import json
import logging
from pathlib import Path

import typer
from pydantic import ValidationError

from cg_hermes.cli.common import get_deliverables
from cg_hermes.config.pipelines import AnalysisType, Pipeline
from cg_hermes.deliverables import Deliverables
from cg_hermes.exceptions import MissingFileError
from cg_hermes.validate import get_deliverables_obj

LOG = logging.getLogger(__name__)

app = typer.Typer()


@app.command(name="deliverables")
def convert_cmd(
    infile: Path,
    pipeline: Pipeline = typer.Option(..., help="Specify the analysis type"),
    analysis_type: AnalysisType = typer.Option(None, help="Specify the analysis type"),
):
    LOG.info(
        "Convert deliverable file %s from pipeline %s to CG format",
        infile,
        pipeline,
    )
    # Read raw file into dict
    deliverables_raw = get_deliverables(infile)
    try:
        deliverables_obj: Deliverables = get_deliverables_obj(
            deliverables=deliverables_raw, pipeline=pipeline, analysis_type=analysis_type
        )
        deliverables_obj.validate_mandatory_files()
    except SyntaxError:
        raise typer.Abort()
    except (ValidationError, MissingFileError) as err:
        LOG.error(err)
        LOG.warning("File %s does not follow the spec", infile)
        raise typer.Abort()

    cg_deliverables = deliverables_obj.convert_to_cg_deliverables()

    typer.echo(json.dumps(cg_deliverables.dict(), indent=2))
