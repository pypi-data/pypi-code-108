# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).

__widgets_version__ = "1.30.0"
# __version__ needs to be set before anything else because it is used internally
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound


def ignore_selected_warnings():
    """Swallows warnings that are only annoying to the user."""
    import warnings

    # deactivate all warnings globally e.g. also sklearn and pandas warnings that wont go away with a simplefilter
    def warn(*args, **kwargs):
        pass

    warnings.warn = warn

    # fixes numpy warning https://stackoverflow.com/questions/34709576/runtimewarning-invalid-value-encountered-in-long-scalars
    warnings.simplefilter(action="ignore", category=RuntimeWarning)

    # Notes:
    # - we might enable the user to disable this via a config in the future
    # - we might want to only locally deactivate warnings e.g. via context managers
    # - the logic above might not work within threads e.g. during background license checks??
    #   in this case, we could add a context manager around the threaded code


ignore_selected_warnings()

del ignore_selected_warnings


# matplotlib 3.3.1 raises "DLL load failed" error on Windows 10. Users can fix this issue
# by installing a different matplotlib version
# https://stackoverflow.com/questions/24251102/from-matplotlib-import-ft2font-importerror-dll-load-failed-the-specified-pro
# We require seaborn which uses matplotlib
# NOTE: you can think about removing this if we require matplotlib>3.3.1
try:
    import seaborn
except ImportError as import_error:
    if "DLL load failed" in str(import_error):
        import textwrap

        raise ImportError(
            textwrap.dedent(
                """
                Importing matplotlib failed. This most likely happens on Windows with matplotlib version 3.3.1, which seems to be buggy.
                Please up- or downgrade matplotlib.

                You can run the following code in your Anaconda prompt:

                pip uninstall matplotlib
                pip install matplotlib==3.0.3
                """
            )
        )
    else:
        raise import_error


# Expose functions to user
from bamboolib.datasets.get_datasets import (
    titanic_csv,
    sales_csv,
    get_titanic_df,
    get_1mio_rows_titanic_df,
    get_ports_df,
    get_sales_df,
)
from bamboolib.setup import test_setup
from bamboolib.setup.import_ import enable, disable, _enable_rich_pandas_df
from bamboolib.helper import activate_license, set_license
from bamboolib.config import set_option, get_option, reset_options

try:
    from bamboolib.wrangler import show
except ImportError:
    from bamboolib.helper import file_logger

    if get_option("global.log_errors"):
        file_logger.exception("ImportError during bamboolib setup")

    raise ImportError(
        "There was an ImportError which is most likely caused by (Ana)conda. The error only happens during the first import of a new package. Please restart your Jupyter kernel and execute the cell again. Afterwards, the error should be fixed. Otherwise, please restart the computer. If neither does help, please contact us via support@8080labs.com"
    )

# Attention: when adding a function here, make sure it is decorated
from bamboolib.edaviz.__modules__ import (
    plot,
    glimpse,
    columns,
    bivariate_plot,
    predictors,
    patterns,
    correlations,
)


# Sometimes, plotly auto-detects the vscode renderer although the user is in the notebook
# ... this is due to the fact that the vscode detection is not specific enough
# then, plotly plots won't show. therefore, we correct this bug and add the notebook renderer
# this correction does not harm vscode, because the plotly_mimetype+notebook works in vscode, too
import plotly.io as pio

if pio.renderers.default == "vscode":
    pio.renderers.default = "plotly_mimetype+notebook"


def _jupyter_nbextension_paths():
    """Ensures Jupyter Notebook puts the nbextensions to the right place."""
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "bamboolib",
            "require": "bamboolib/extension",
        }
    ]


def fix_trailets_bug():
    """
    Traitlets checks whether Widget modules are functions. For that, it uses
    inspect.isfunction(), which doesn't allow cython functions out of the box.
    Thus, we extend inspect.isfunction() to also accept cython functions.
    """

    def extended_inspect_isfunction(object):
        from bamboolib._types import CyFunctionType
        from types import FunctionType

        """Return true if the object is a user-defined function OR cyfunction."""
        return isinstance(object, (FunctionType, CyFunctionType))

    import inspect

    inspect.isfunction = extended_inspect_isfunction


fix_trailets_bug()
del fix_trailets_bug


from bamboolib.setup.ipython_display import extend_pandas_ipython_display

extend_pandas_ipython_display()
del extend_pandas_ipython_display


def full_width():
    """Makes the Jupyter Notebook code and output cells full width."""
    from IPython.display import display, HTML

    display(
        HTML(
            (
                "<style>"
                "div#notebook-container    { width: 99%; }"
                "div#menubar-container     { width: 75%; }"
                "div#maintoolbar-container { width: 99%; }"
                "</style>"
            )
        )
    )


# setup plugins via importing them
import bamboolib.loaders as _loader_plugins


# ATTENTION: this needs to be the last logic within init
from bamboolib.setup.module_view import setup_module_view

# __name__ enables whitelabeling of the library name. Usually its value is "bamboolib"
setup_module_view(__name__)
