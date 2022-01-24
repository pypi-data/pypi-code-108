# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for validation and conversion."""
import logging
from typing import Any


class _NoPlotlyFilter(logging.Filter):
    """The filter to remove the errors about forecast visualization."""

    def filter(self, record):
        return not (
            record.getMessage() == 'Importing plotly failed. Interactive plots will not work.' or
            record.getMessage() == 'Importing matplotlib failed. Plotting will not work.')


def import_fbprophet(raise_on_fail: bool = True) -> Any:
    """Import and return the fbprophet module.

    :param raise_on_fail: whether an exception should be raise if import fails, defaults to False
    :type raise_on_fail: bool
    :return: fbprophet module if it's installed, otherwise None
    """
    logger = logging.getLogger('fbprophet')
    logger.addFilter(_NoPlotlyFilter())
    try:
        import fbprophet
        # ensure we can create the model
        fbprophet.Prophet()
        return fbprophet
    except ImportError:
        if raise_on_fail:
            raise
        else:
            return None
    except Exception as e:
        if raise_on_fail:
            raise RuntimeError("Prophet instantiation failed") from e
        else:
            return None
