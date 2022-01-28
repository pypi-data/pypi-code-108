import logging
import string
from typing import List, Dict

logger = logging.getLogger(__name__)


def is_arg_name(name) -> bool:
    if not name:
        return False
    if name[0] not in string.ascii_letters:
        return False
    if any(v not in string.ascii_letters + string.digits + '_' for v in name):
        return False
    return True


def parse_other_args(args: List[str]) -> Dict:
    '''
    Capture command-line arguments that are not specified for `argparse`.
    Use case is to pass on all arguments that are not recognized
    by the current script.

    Example:
        args = ArgumentParser()
        args.add_argument('model_cls_name')
        args.add_argument('data_version')
        args.add_argument('--version-tag', help='information')
        args.add_argument('--log-level', default='info')
        args, otherargs = args.parse_known_args()
        otherargs = parse_other_args(otherargs)

    Return a dict. For example, if unknown args are

        '--age 38 --title engineer --print-details'

    then the returned dict is

        {'age': 38, 'title': 'engineer', 'print_details': True}
    '''
    if not args:
        return dict()
    result = {}
    next_arg = None
    for x in args:
        if next_arg is None:
            assert x.startswith('-')
            next_arg = x.lstrip('-').replace('-', '_')
            assert is_arg_name(next_arg)
        else:
            if x.startswith('-'):
                # The last arg does not have a value,
                # while a new arg is starting.
                # Treat the last arg as a `True` flag.
                result[next_arg] = True
                next_arg = x.lstrip('-').replace('-', '_')
                assert is_arg_name(next_arg)
            else:
                try:
                    v = int(x)
                    result[next_arg] = v
                except ValueError:
                    try:
                        v = float(x)
                        result[next_arg] = v
                    except ValueError:
                        v = str(x)
                        if v.lower() in ('true', 'yes'):
                            v = True
                        elif v.lower() in ('false', 'no'):
                            v = False
                        result[next_arg] = v
                next_arg = None
    if next_arg:
        result[next_arg] = True
    return result
