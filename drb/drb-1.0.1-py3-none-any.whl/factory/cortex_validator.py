import sys

import click
import jsonschema
from drb.factory.item_class import ItemClass


@click.command(name='cortex-validator')
@click.argument('cortex',
                type=click.Path(exists=True, file_okay=True, dir_okay=False))
def validate(cortex):
    try:
        ItemClass.validate(cortex)
    except jsonschema.exceptions.ValidationError as ex:
        print('Invalid schema: ', str(ex), file=sys.stderr)


def main():
    validate()
