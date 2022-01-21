#  to not break import theming.html, after a Py3 compat induced
# rename of the html.py module into html_tools.py:
import sys


def func_name_of_callable(
    f, key='__name__' if sys.version_info[0] < 3 else '__qualname__'
):
    """Returns the name of a function, e.g. for logs so that the reader knows
    what is being executed, w/o clutter

    e.g. str(f) = "<bound method AXConfiguratorMain.handle_termination_signal of <Products.WPSCommon.TR69.AXConfigurator.AXConfiguratorMain object at 0x7f1a1cfe7f10>>"
    is hard to read while not all callables have .__name__
    while we return just "handle_termination_signal" or "AXConf.handle.." in v3

    Works also for nested partials (but not anonymous lambdas)
    """
    # todo: decorators / wrapped, classname of __call__, ...
    f1 = f
    while hasattr(f1, 'func'):
        f1 = f1.func
    return getattr(f1, key, str(f1))
