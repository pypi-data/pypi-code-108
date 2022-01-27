import argh
from circe import (
    serve,
    start_workers,
    make_api_access,
    remove_api_access,
    list_api_access,
    list_transformations,
    run,
)
import sys
import os

sys.path.insert(0, os.getcwd())


def run_cli():
    parser = argh.ArghParser()
    parser.add_commands(
        [
            serve,
            start_workers,
            make_api_access,
            remove_api_access,
            list_api_access,
            list_transformations,
            run,
        ]
    )
    parser.dispatch()


if __name__ == "__main__":
    run_cli()
