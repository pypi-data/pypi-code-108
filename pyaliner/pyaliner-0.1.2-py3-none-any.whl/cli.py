"""
Command Line Interface for sequence comparison API
"""
from typing import Tuple

from click import group, argument, option, Choice, get_current_context

from pyaliner.align import CLASSIC, COMPACT
from pyaliner.compare import PAIRED, INLINED, compare_in_true_pred_from_file, compare_true_pred_from_file, \
    compare_true_pred_from_files, compare_in_true_pred_from_files, compare_true_pred1_pred2_from_file, \
    compare_true_pred1_pred2_from_files

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
ALI_HELP = 'what alignment algorithm to use:\ntoken to token (=classic) or\nmulti-token to multi-token (=compact)'
VIEW_HELP = 'what view to show:' \
            '\nfull line against full line (=paired) or\nsingle line with embedded differences (=inline)'


@group()
def pyaliner(context_settings=CONTEXT_SETTINGS):
    pass


@pyaliner.command(help='compares true and predicted sequences from either 1 paired file or 2 single files')
@argument('paths', nargs=-1)
@option('--alignment', '-a', default=COMPACT, show_default=True, type=Choice([CLASSIC, COMPACT]), help=ALI_HELP)
@option('--view', '-v', default=PAIRED, show_default=True, type=Choice([PAIRED, INLINED]), help=VIEW_HELP)
def tp(paths: Tuple[str, ...], alignment: str, view: str):
    if len(paths) == 1:

        compare_true_pred_from_file(paths[0], alignment, view)

    elif len(paths) == 2:

        compare_true_pred_from_files(*paths, alignment, view)

    else:

        get_current_context() \
            .fail(f'This commands accepts either a single file or two files but [{len(paths)}] paths were given')


@pyaliner.command(help='compares input, true and predicted sequences from either 1 triplet file or 3 single files')
@argument('paths', nargs=-1)
@option('--alignment','-a', default=COMPACT, show_default=True, type=Choice([CLASSIC, COMPACT]), help=ALI_HELP)
def itp(paths: Tuple[str, ...], alignment: str):
    if len(paths) == 1:

        compare_in_true_pred_from_file(paths[0], alignment)

    elif len(paths) == 3:

        compare_in_true_pred_from_files(*paths, alignment)

    else:

        get_current_context() \
            .fail(f'This commands accepts either a single file or three files but [{len(paths)}] were given')


@pyaliner.command(help='compares true, 1st and 2nd predicted from either 1 triplet file or 3 single files')
@argument('paths', nargs=-1)
def tpp(paths: Tuple[str, ...]):
    if len(paths) == 1:

        compare_true_pred1_pred2_from_file(paths[0])

    elif len(paths) == 3:

        compare_true_pred1_pred2_from_files(*paths)

    else:

        get_current_context() \
            .fail(f'This commands accepts either a single file or three files but [{len(paths)}] were given')


if __name__ == '__main__':
    pyaliner()
