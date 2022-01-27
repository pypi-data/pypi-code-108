from inspect import getfullargspec, signature, Parameter
from functools import wraps
import copy

from fsos import fs_manager as fsm

BUCKET_ARGNAME = "bucket_name"
ROOT_ARGNAME = "root_path"


def _get_default_args(func):
    sign = signature(func)
    return {
        k: v.default
        for k, v in sign.parameters.items()
        if v.default is not Parameter.empty
    }


def fsos_init_checker(func):
    """check fsos initalization status before running fsos function"""
    argspec = getfullargspec(func)
    root_index = argspec.args.index(ROOT_ARGNAME)

    @wraps(func)
    def pre_check(*args, **kwargs):
        dwargs = _get_default_args(func)
        dwargs.update(kwargs)
        if root_index < len(args):
            root_value = args[root_index]
        elif ROOT_ARGNAME in kwargs.keys():
            root_value = kwargs[ROOT_ARGNAME]
        else:
            root_value = dwargs[ROOT_ARGNAME]
        if not fsm._check_fsos(ROOT_PATH=root_value):
            fsm._create_fsos(ROOT_PATH=root_value)
        return func(*args, **kwargs)

    return pre_check


def os_failure_checker(func):
    """check fsos initalization status before running fsos function"""
    argspec = getfullargspec(func)
    root_index = argspec.args.index(ROOT_ARGNAME)

    @wraps(func)
    def exception(*args, **kwargs):
        dwargs = _get_default_args(func)
        dwargs.update(kwargs)
        if root_index < len(args):
            root_value = args[root_index]
        elif ROOT_ARGNAME in kwargs.keys():
            root_value = kwargs[ROOT_ARGNAME]
        else:
            root_value = dwargs[ROOT_ARGNAME]
        try:
            db = copy.deepcopy(fsm._get_db())
            ret = func(*args, **kwargs)
        except:
            fsm._set_db(db)
            raise RuntimeError("Failed to run os manager. roll backed fs db")
        fsm._update_fsos(root_value)

        return ret

    return exception
