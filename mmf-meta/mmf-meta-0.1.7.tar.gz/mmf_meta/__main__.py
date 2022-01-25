import importlib
import json

import click
from mmf_meta.core import scan, get_signature
import sys
import os


@click.group()
def cli():
    sys.path.append(os.getcwd())
    return


@click.option("--out", default="mmf.json")
@cli.command(name="get-meta")
@click.argument(
    "script",
)
def get_meta(script, out):
    module = importlib.import_module(script)
    targets, artifacts = scan()
    signature = {
        "targets": [get_signature(t) for t in targets],
        "artifacts": [get_signature(a) for a in artifacts],
    }
    with open(out, "w") as f:
        json.dump(signature, f, indent=2)


if __name__ == "__main__":
    cli()
