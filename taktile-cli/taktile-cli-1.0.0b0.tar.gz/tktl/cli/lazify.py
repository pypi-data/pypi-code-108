import pathlib

import click

from tktl.cli.common import ClickCommand
from tktl.commands.lazify import lazify_file
from tktl.core.config import settings
from tktl.core.t import LazifyType


@click.command(
    "lazify",
    help="Add metadata to parquet file for lazy loading",
    cls=ClickCommand,
    **settings.HELP_COLORS_DICT,
)
@click.option(
    "--no-shap",
    is_flag=True,
    help=(
        "If set, skip calculating background data for shap explanations "
        "and use first non-null occurance value per column, instead."
    ),
)
@click.argument("source_path")
@click.argument("target_path")
@click.pass_context
def lazify(ctx, source_path: str, target_path: str, no_shap: bool):

    source_pathlib_path = pathlib.Path(source_path)
    target_pathlib_path = pathlib.Path(target_path)

    if not source_pathlib_path.is_file():
        raise click.BadParameter(
            f"'{source_path}' does not exist or is not a file", param_hint="source_path"
        )
    if source_pathlib_path.suffix != ".pqt":
        raise click.BadParameter(
            f"'{source_path}' does not seem to be a parquet file",
            param_hint="source_path",
        )

    lazify_type = LazifyType.FIRST_VALID if no_shap else LazifyType.SHAP

    lazify_file(
        source_path=source_pathlib_path,
        target_path=target_pathlib_path,
        data=None,
        lazify_type=lazify_type,
    )
