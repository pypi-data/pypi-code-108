import logging

import click

from tsfaker.generator.foreign_key import ForeignKeyCatalog
from tsfaker.generator.table import TableGenerator
from tsfaker.io.io_arguments import process_input_output_arguments
from tsfaker.io.resources import process_resources, add_schema_to_resources
from tsfaker.io.schema import read_schema, iter_schemas_to_generate
from tsfaker.io.utils import get_logging_level_value


@click.command(help="Generate a csv from table-schema descriptor(s), "
                    "given as a local folder path, local files paths, remote url or on stdin ('-').")
@click.argument('schema_descriptors', type=str, nargs=-1)
@click.option('--output', '-o', default=['-'], type=str, multiple=True,
              help="Output files paths (same number as SCHEMAS_DESCRIPTORS) or stdout ('-' default), "
                   "or existing local folder path if SCHEMAS_DESCRIPTORS are given as a local folder path.")
@click.option('--resources', '-r', type=str, multiple=True,
              help="CSV paths or directory containing CSV, to read foreign keys values.")
@click.option('--nrows', '-n', default=10, type=int, help='Number of rows to generate (default=10).')
@click.option('--separator', type=str, default=',', help='Separator for csv outputs.')
@click.option('--pretty', is_flag=True, help='Get a console-friendly tabular output, instead of csv.')
@click.option('--dry-run', is_flag=True, help='Write logs but do not generate data.')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files.')
@click.option('--ignore-foreign-keys', is_flag=True, help='Ignore foreign keys relationships.')
@click.option('--low-memory', is_flag=True,
              help='Do not store foreign keys values in memory catalog, to use in different tables generation.')
@click.option('--limit-fk', default=None, type=int,
              help='Limit the number of row to read in foreign keys, to increase speed and decrease memory footprint.')
@click.option('--random-seed', '-s', default=42, type=int, help='Random seed to generate data (default=42).')
@click.option('--logging-level', default='INFO', type=str,
              help='Modify the logging level of tsfaker.')
def cli(schema_descriptors, output, resources, nrows, separator, pretty, dry_run, overwrite, ignore_foreign_keys,
        low_memory, limit_fk, random_seed, logging_level):
    logging_level_value = get_logging_level_value(logging_level)

    logging.basicConfig(level=logging_level_value,
                        format='%(asctime)s :: %(levelname)s :: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )

    input_descriptors, output = process_input_output_arguments(schema_descriptors, output)

    schemas = [read_schema(descriptor, output_file, ignore_foreign_keys) for descriptor, output_file in
               zip(input_descriptors, output)]

    resource_name_to_path_or_schema = process_resources(resources)
    add_schema_to_resources(resource_name_to_path_or_schema, schemas)

    foreign_key_catalog = ForeignKeyCatalog(resource_name_to_path_or_schema, low_memory=low_memory, limit_fk=limit_fk)

    for schema in iter_schemas_to_generate(resource_name_to_path_or_schema):
        table_generator = TableGenerator(schema, nrows, resource_name_to_path_or_schema, foreign_key_catalog,
                                         random_seed)
        table_generator.generate_output_csv(dry_run, pretty, overwrite, separator)


if __name__ == '__main__':
    cli()
