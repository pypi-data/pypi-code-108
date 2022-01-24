import logging

import click

from tktl.commands.init import init_project
from tktl.core.t import TemplateT

_logger = logging.getLogger("root")


@click.command(help="Creates project scaffolding")
@click.option(
    "--name", help="Name of the project", default="tktl-serving", required=True
)
@click.option(
    "--path", help="Directory where the new project will be created", required=False
)
@click.option(
    "--template",
    help="Initial template of the new project",
    type=click.Choice(TemplateT.list(), case_sensitive=False),
    default="repayment",
)
def init(path: str, name: str, template: TemplateT) -> None:
    """Creates a new project with the necessary scaffolding.

    Creates the supporting files needed. The directory structure of a new
    project , and the files within it will look like this:

        .dockerignore
        .gitattributes
        .gitignore
        .buildfile
        README.md
        assets              # Where your ML models and test data live
        requirements.txt    # User-specified requirements
        src                 # Source code for endpoint definitions
        tests               # User-specified tests
        tktl.yaml           # Taktile configuration options

    """
    init_project(path=path, name=name, template=TemplateT[template.upper()])
