import click

import fnmatch
from quickstats.components import RooInspector
    
@click.command(name='inspect_rfile')
@click.option('-i', '--file_expr', required=True, help='File name expression '
              '(supports wild card, multiple files separated by commas).')
@click.option('-t', '--tree_name', required=True, help='Tree name.')
@click.option('-o', '--output_file', default=None, help='Export output to text file. If None, no output is saved.')
@click.option('--include', 'include_patterns', default=None, 
              help='Match variable names with given patterns (separated by commas).')
@click.option('--exclude', 'exclude_patterns', default=None,
              help='Exclude variable names with given patterns (separated by commas).')
@click.option('-f','--filter', 'filter_expr', default=None, show_default=True,
              help='Apply a filter to the events.')
@click.option('--include', 'include_patterns', default=None, 
              help='Match variable names with given patterns (separated by commas).')
@click.option('--exclude', 'exclude_patterns', default=None,
              help='Exclude variable names with given patterns (separated by commas).')
@click.option('-v', '--verbosity',  default="INFO", show_default=True,
              help='verbosity level ("DEBUG", "INFO", "WARNING", "ERROR")')
def inspect_rfile(file_expr, tree_name, filter_expr=None, output_file=None,
                  include_patterns=None, exclude_patterns=None, verbosity="INFO"):
    '''
        Inspect root files
    '''
    file_expr = file_expr.split(',')
    if include_patterns is not None:
        include_patterns = include_patterns.split(',')
    if exclude_patterns is not None:
        exclude_patterns = exclude_patterns.split(',')
    rinspector = RooInspector(tree_name, file_expr, filter_expr=filter_expr, verbosity=verbosity)
    rinspector.print_summary(include_patterns=include_patterns,
                             exclude_patterns=exclude_patterns,
                             save_as=output_file)