"""NanamiLang, allow exporting method"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


import inspect
import functools

from .base import Base


def export():
    """
    NanamiLang export() decorator

    Example usage:

    @export()
    def method(<maybe-dt-args>) -> <some nanamilang dt>:
        ...

    This decorator will lint your data type exportable method
    And in case of success, will mark this method as exported
    But in case of a failure, 'AssertionError' will be raised
    """

    def wrapped(_fn):
        @functools.wraps(_fn)
        def function(*args, **kwargs):

            return _fn(*args, **kwargs)

        signature = inspect.signature(_fn)

        _ret = signature.return_annotation
        _args = map(lambda x: x.annotation, signature.parameters.values())

        assert issubclass(_ret, (Base,)) or \
               len(tuple(filter(lambda x: not issubclass(x, (Base,)), _args))) > 1, (
            'export: unable to export method due to invalid(unspecified) arg/ret type'
        )

        function.exported = True  # <- and we can later check whether exported or not

        return function

    return wrapped
