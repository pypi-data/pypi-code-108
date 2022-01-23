import datetime
import json
import logging
import os
import sys
from pathlib import Path

import click
import yaml

from oarepo_model_builder.entrypoints import load_entry_points_dict, create_builder_from_entrypoints, \
    load_included_models_from_entry_points, load_model
from oarepo_model_builder.schema import ModelSchema
from oarepo_model_builder.utils.hyphen_munch import HyphenMunch
from oarepo_model_builder.utils.verbose import log


@click.command()
@click.option('--output-directory',
              help='Output directory where the generated files will be placed. '
                   'Defaults to "."')
@click.option('--package',
              help='Package into which the model is generated. '
                   'If not passed, the name of the current directory, '
                   'converted into python package name, is used.')
@click.option('--set', 'sets',
              help='Overwrite option in the model file. Example '
                   '--set name=value',
              multiple=True)
@click.option('-v', 'verbosity',
              help='Increase the verbosity. This option can be used multiple times.',
              count=True)
@click.option('--config', 'configs',
              help='Load a config file and replace parts of the model with it. '
                   'The config file can be a json, yaml or a python file. '
                   'If it is a python file, it is evaluated with the current '
                   'model stored in the "oarepo_model" global variable and '
                   'after the evaluation all globals are set on the model.',
              multiple=True)
@click.option('--isort/--skip-isort', default=True, help='Call isort on generated sources')
@click.option('--black/--skip-black', default=True, help='Call black on generated sources')
@click.argument('model_filename')
def run(output_directory, package, sets, configs, model_filename, verbosity, isort, black):
    """
    Compiles an oarepo model file given in MODEL_FILENAME into an Invenio repository model.
    """

    # extend system's search path to add script's path in front (so that scripts called from the compiler are taken
    # from the correct virtual environ)
    os.environ['PATH'] = str(Path(sys.argv[0]).parent.absolute()) + os.pathsep + os.environ.get('PATH', '')

    if not output_directory:
        output_directory = os.getcwd()

    # set the logging level, it will be warning - 1 (that is, 29) if not verbose,
    # so that warnings only will be emitted. With each verbosity level
    # it will decrease
    logging.basicConfig(
        level=logging.INFO - verbosity,
        format=''
    )

    Path(output_directory).mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(Path(output_directory) / 'installation.log', 'a')
    handler.setLevel(logging.INFO)
    logging.root.addHandler(handler)

    log.enter(0, '\n\n%s\n\nProcessing model %s into output directory %s',
              datetime.datetime.now(), model_filename, output_directory)

    schema = load_model(model_filename, package, configs, black, isort, sets)
    schema.schema['output-directory'] = output_directory
    builder = create_builder_from_entrypoints()
    builder.build(schema, output_directory)

    log.leave('Done')

    print(f"Log saved to {Path(output_directory) / 'installation.log'}")


if __name__ == '__main__':
    run()
