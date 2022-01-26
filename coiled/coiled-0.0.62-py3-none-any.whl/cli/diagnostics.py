import click

from ..core import diagnostics as core_diagnostics
from .utils import CONTEXT_SETTINGS


@click.command(
    context_settings=CONTEXT_SETTINGS,
    help="Run diagnostics related to your local settings and account",
)
def diagnostics():
    """Run diagnostics related to your local settings and account."""
    diagnostics_result = core_diagnostics()
    print(diagnostics_result)
