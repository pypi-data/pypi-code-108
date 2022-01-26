import logging
from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError

from cg_hermes.cli.common import get_deliverables
from cg_hermes.config.balsamic import BALSAMIC_COMMON_TAGS
from cg_hermes.config.fluffy import FLUFFY_COMMON_TAGS
from cg_hermes.config.mip_dna import MIP_DNA_TAGS
from cg_hermes.config.mip_rna import MIP_RNA_TAGS
from cg_hermes.config.mutant import MUTANT_COMMON_TAGS
from cg_hermes.config.pipelines import AnalysisType, Pipeline
from cg_hermes.exceptions import MissingFileError
from cg_hermes.validate import get_deliverables_obj, validate_common_tags, validate_tag_map

LOG = logging.getLogger(__name__)

app = typer.Typer()


@app.command("deliverables")
def validate_deliverables(
    infile: Path,
    pipeline: Pipeline = typer.Option(Pipeline.FLUFFY, help="Specify pipeline"),
    analysis_type: AnalysisType = typer.Option(None, help="Specify the analysis type"),
):
    """Validate a deliverables file"""
    LOG.info("Validating file '%s' from pipeline %s", infile, pipeline)

    # Read raw file into dict
    deliverables = get_deliverables(infile)

    try:
        deliverables_obj = get_deliverables_obj(
            deliverables=deliverables, pipeline=pipeline, analysis_type=analysis_type
        )
        deliverables_obj.validate_mandatory_files()
    except SyntaxError:
        raise typer.Abort()
    except (ValidationError, MissingFileError) as err:
        LOG.error(err)
        LOG.warning("File %s does not follow the spec", infile)
        raise typer.Abort()
    LOG.info("Deliverables file seems to be on correct format")


@app.command("tags")
def validate_tags_cmd(pipeline: Pipeline):
    """Validate the tag maps for one of the definitions"""
    LOG.info("Validating %s common tags", pipeline)
    exit_code = 0

    if pipeline == str(Pipeline.MIP_DNA):
        tag_map = MIP_DNA_TAGS
    elif pipeline == str(Pipeline.MIP_RNA):
        tag_map = MIP_RNA_TAGS
    elif pipeline == str(Pipeline.BALSAMIC):
        tag_map = BALSAMIC_COMMON_TAGS
    elif pipeline == str(Pipeline.FLUFFY):
        tag_map = FLUFFY_COMMON_TAGS
    elif pipeline == str(Pipeline.SARS_COV_2):
        tag_map = MUTANT_COMMON_TAGS
    else:
        LOG.info("Could not find pipeline tags for %s", pipeline)
        raise typer.Exit(code=exit_code)

    try:
        validate_tag_map(tag_map=tag_map)
        LOG.info("Tag map looks fine")
    except ValidationError as err:
        LOG.warning(err)
        exit_code = 1
    raise typer.Exit(code=exit_code)
