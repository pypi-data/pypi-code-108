import typer
from typing import List, Dict, Union, Type
from ehelply_microservice_library.cli import cli_release, cli_update, cli_cryptography, cli_database, cli_service, \
    cli_utils, cli_test, cli_aws
from ehelply_microservice_library.service_bootstrap import ServiceBootstrap
from ehelply_microservice_library.cli.cli_state import CLIState


def make_clis(service: Type[ServiceBootstrap]) -> List[Dict[str, Union[str, typer.Typer]]]:
    CLIState.service = service

    return [
        {
            "name": "release",
            "cli": cli_release.cli
        },
        {
            "name": "update",
            "cli": cli_update.cli
        },
        {
            "name": "cryptography",
            "cli": cli_cryptography.cli
        },
        {
            "name": "database",
            "cli": cli_database.cli
        },
        {
            "name": "service",
            "cli": cli_service.cli
        },
        {
            "name": "utils",
            "cli": cli_utils.cli
        },
        {
            "name": "test",
            "cli": cli_test.cli
        },
        {
            "name": "aws",
            "cli": cli_aws.cli
        }

    ]
