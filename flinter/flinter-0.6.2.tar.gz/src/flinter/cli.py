"""Command line interface.
"""


import os
import click

from flinter._cli_utils import get_database
from flinter.nesting_utils import get_subtree


_db_kw = "--database"
_db_kw_short = "-b"
_db_option = click.option(_db_kw, _db_kw_short, type=click.Path(exists=True),
                          help="A flinter database")
_db_option_flag = click.option(_db_kw, _db_kw_short, is_flag=True,
                               help="Indicates if path refers to database")

_user_rules_option = click.option("--flintrc", "-r", type=str, default=None,
                                  help="Custom rules file(s)", multiple=True)


def _check_path_exists(path):
    if not os.path.exists(path):
        raise Exception(f'{path} does not exist')


def _get_database_no_flag(database, path, user_rc_list):
    if database is None:  # creates new db
        _check_path_exists(path)
        db = get_database(path=path, user_rc_list=user_rc_list)

    else:
        db = get_database(database=database)
        db = get_subtree(db, path)

        if not db:
            raise KeyError(f'Cannot find {path}')

    return db


def _get_database_with_flag(db_flag, path, user_rc_list):

    if db_flag:
        db = get_database(database=path)
    else:
        db = get_database(path=path, user_rc_list=user_rc_list)

    return db


def add_options(options):
    # https://stackoverflow.com/a/40195800/11011913
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group()
def main_cli():
    """--------------------    FLINT  ---------------------

.      - Flint, because our code stinks... -


You are now using the command line interface of Flint,
a Fortran linter created at CERFACS (https://cerfacs.fr),
for the EXCELLERAT center of excellence (https://www.excellerat.eu/).

This is a python package currently installed in your python environment.

"""
    pass


@click.command()
@click.argument("path", type=str, required=True)
@add_options([_db_option, _user_rules_option])
@click.option("--output-filename", "-o", type=str, default='db.json')
def database(path, database, flintrc, output_filename):
    """Create database.
    """
    from flinter._cli_utils import dump_file

    db = _get_database_no_flag(database, path, flintrc)

    dump_file(output_filename, db, verbose=1)


main_cli.add_command(database)


@click.command()
@click.argument("path", type=str, required=True)
@add_options([_db_option_flag, _user_rules_option])
@click.option("--depth", "-d", type=int, default=3,
              help="Depth of stats [1-10000]")
@click.option("--verbose", "-v", is_flag=True,
              help="Print detailed information")
def score(path, database, flintrc, depth, verbose):
    """Score the formatting of a database, file, or folder (recursive).
    """
    from flinter._cli_utils import score_cli
    from flinter.post_processing import count_errors

    db = _get_database_with_flag(database, path, flintrc)

    count_dict = count_errors(db)
    max_lvl = depth if verbose else 0
    score_cli(count_dict, max_lvl=max_lvl)


main_cli.add_command(score)


@click.command()
@click.argument("path", type=str, required=True)
@add_options([_db_option_flag, _user_rules_option])
@click.option("--minrate", "-m", type=int, default=-10,
              help="Minimum rate allowed")
@click.option("--norate", is_flag=True,
              help="Only structure, no rates")
def tree(path, database, flintrc, minrate, norate):
    """Visual representation of the score with circular packing.
    """
    from flinter.post_processing import count_errors
    from flinter.nobvisual import visualfort

    db = _get_database_with_flag(database, path, flintrc)
    count_dict = count_errors(db)

    visualfort(count_dict, minrate=minrate, norate=norate)


main_cli.add_command(tree)


@click.command()
@click.argument("path", type=str, required=True)
@add_options([_db_option_flag, _user_rules_option])
def struct(path, database, flintrc):
    """Print structure of the database, directory, or file.
    """
    from flinter._lizard import NodePrinter

    db = _get_database_with_flag(database, path, flintrc)

    node_printer = NodePrinter(
        lambda node: node["name"],
        lambda node: node["children"],
        lambda node: [(arg, node[arg])
                      for arg in node if arg in ("path", "type", "start_line", "end_line", "size")],
    )

    node_printer(db)


main_cli.add_command(struct)


@click.command()
@click.argument("path", type=str, required=True)
@add_options([_db_option_flag, _user_rules_option])
@click.option("--dump", "-o", type=str,
              help='Dumps error counts to file')
@click.option("--nested", "-n", is_flag=True,
              help="With nested file contents")
@click.option("--quantity", '-q', type=int, default=5,
              help="Number of errors to show")
def stats(path, database, flintrc, dump, nested, quantity):
    """Dump stats to file.
    """
    from flinter._cli_utils import dump_file
    from flinter.post_processing import count_errors
    from flinter.post_processing import get_most_common_errors
    from flinter.post_processing import order_by_key
    from flinter.nesting_utils import unnest_to_file_level
    from flinter.nesting_utils import flatten

    tab = '  '

    nested_db = _get_database_with_flag(database, path, flintrc)
    unnested_db = unnest_to_file_level(nested_db, fully=False)
    unnested_count = count_errors(unnested_db)

    # get worst rated files
    sorted_files = order_by_key(unnested_count, key='rate')
    print("Worst rated files:")
    for child in sorted_files[:quantity]:
        print(f"{tab}{child['path']}: {child['rate']:.2f}")

    # get worst rated functions
    fully_unnested_count = flatten(unnested_count,
                                   not_append_types=('folder', 'file'))
    sorted_functions = order_by_key(fully_unnested_count, key='rate')
    print("\nWorst rated functions:")
    for child in sorted_functions[:quantity]:
        print(f"{tab}{child['path']}: {child['rate']:.2f}")

    # get most commont errors
    regexp_errors, struct_errors = get_most_common_errors(nested_db)

    # print worst errors
    if regexp_errors:
        print('\nRegexp most common errors:')
        for error_name, nb_errors in regexp_errors[:quantity]:
            print(f'{tab}{error_name}: {nb_errors}')

    if struct_errors:
        print('\nStruct most common errors:')
        for error_name, nb_errors in struct_errors[:quantity]:
            print(f'{tab}{error_name}: {nb_errors}')

    # dumps counts to file
    if dump:
        if not nested:  # inside because depends on nested
            unnested_db = unnest_to_file_level(nested_db, fully=True)
            unnested_count = count_errors(unnested_db)

        print('\n')
        dump_file(dump, unnested_count, verbose=1)


main_cli.add_command(stats)


@click.command()
@click.argument("path", type=str, required=True)
@add_options([_db_option, _user_rules_option])
def lint(path, database, flintrc):
    """Prints detailed file linting info.
    """
    from flinter._cli_utils import _build_pretty_table_for_regexp
    from flinter.nesting_utils import unnest_to_file_level

    if os.path.isdir(path):
        print('Directories are not accepted.')
        return

    # reads db or creates data
    nested_db = _get_database_no_flag(database, path, flintrc)

    # unnested data
    file_info = unnest_to_file_level(nested_db, fully=True)[0]

    # create tables
    tables = {key: _build_pretty_table_for_regexp(rules_info)
              for key, rules_info in file_info['regexp_rules'].items()}

    for key, table in tables.items():
        print(f'\n{key}')
        print(table)


main_cli.add_command(lint)


@click.command()
@click.argument("languages", type=click.Choice(['fortran', 'python', 'cpp']),
                nargs=-1, required=False)
def config(languages):
    """Copy the default rule files locally.
    """
    from flinter.utils import copy_default_rule

    if len(languages) == 0:
        languages = ['fortran']

    copied_filenames = []
    for language in languages:
        filename = copy_default_rule(language)
        copied_filenames.append(filename)

    print(f"Copied the following flinter default rules: {', '.join(copied_filenames)}")


main_cli.add_command(config)
