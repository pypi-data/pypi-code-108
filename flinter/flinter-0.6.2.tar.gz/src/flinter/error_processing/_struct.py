

def get_statements_errors(size, max_lines=50, errors=None):
    if errors is None:
        errors = {}

    _get_too_many_lines_errors(errors, size, max_lines)

    return errors


def _get_too_many_lines_errors(errors, size, max_lines):
    if size > max_lines:
        errors['too-many-lines'] = {'num_lines': size, 'max_allowed': max_lines}


def get_vars_errors(var_list, max_declared_locals=12, min_var_len=3,
                    max_var_len=20, errors=None):
    if errors is None:
        errors = {}

    # too many locals
    _get_too_many_locals_errors(errors, var_list, max_declared_locals)

    # var size
    _get_var_size_errors(errors, var_list, min_var_len, max_var_len)

    return errors


def _get_too_many_locals_errors(errors, var_list, max_declared_locals):
    lstat = len(var_list)
    if lstat > max_declared_locals:
        errors['too-many-locals'] = {'num_locals': lstat,
                                     'max_allowed': max_declared_locals}


def _get_var_size_errors(errors, var_list, min_var_len, max_var_len):
    short_vars, long_vars = _get_short_long_names(var_list, min_var_len, max_var_len)

    if short_vars:
        errors['short-varnames'] = {'names': short_vars,
                                    'min_len_allowed': min_var_len}

    if long_vars:
        errors['long-varnames'] = {'names': long_vars,
                                   'max_len_allowed': max_var_len}


def get_nesting_errors(depth, max_depth=3, errors=None):
    if errors is None:
        errors = {}

    if depth > max_depth:
        errors['too-many-levels'] = {'depth': depth, 'max_allowed': max_depth}

    return errors


def get_args_errors(arg_list, max_arguments=4, min_arg_len=3,
                    max_arg_len=20, errors=None):

    if errors is None:
        errors = {}

    _get_too_many_arguments(errors, arg_list, max_arguments)
    _get_var_size_errors(errors, arg_list, min_arg_len, max_arg_len)


def _get_too_many_arguments(errors, arg_list, max_arguments):
    larg = len(arg_list)

    if larg > max_arguments:
        errors['too-many-arguments'] = {'num_args': larg,
                                        'max_allowed': max_arguments}


def _get_args_size_errors(errors, arg_list, min_arg_len, max_arg_len):
    short_vars, long_vars = _get_short_long_names(arg_list, min_arg_len, max_arg_len)

    if short_vars:
        errors['short-argnames'] = {'names': short_vars,
                                    'min_len_allowed': min_arg_len}

    if long_vars:
        errors['long-varnames'] = {'names': long_vars,
                                   'max_len_allowed': max_arg_len}


def _get_short_long_names(name_list, min_len, max_len):
    short_names = []
    long_names = []
    for name in name_list:
        if len(name) < min_len:
            short_names.append(name)

        elif len(name) > max_len:
            long_names.append(name)

    return list(set(short_names)), list(set(long_names))
