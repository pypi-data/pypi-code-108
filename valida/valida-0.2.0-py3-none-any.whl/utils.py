from inspect import signature


def null_condition_binary_check(cond_1, cond_2):
    """Get the non-null condition of two conditions if one is null, otherwise return
    None."""
    return cond_1 if cond_2.is_null else (cond_2 if cond_1.is_null else None)


def get_func_args_by_kind(func):
    parameters_by_kind = {
        "POSITIONAL_OR_KEYWORD": [],
        "VAR_POSITIONAL": [],
        "VAR_KEYWORD": [],
    }
    for k, v in signature(func).parameters.items():
        try:
            parameters_by_kind[v.kind.name].append(k)
        except KeyError:
            raise NotImplementedError(
                f'Function argument with kind: "{v.kind.name}" is not allowed.'
            )

    return parameters_by_kind


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)
