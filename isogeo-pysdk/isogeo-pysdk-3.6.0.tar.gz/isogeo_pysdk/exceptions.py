# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo Python SDK - Custom exceptions

    See: https://docs.python.org/fr/3/tutorial/errors.html#user-defined-exceptions
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class IsogeoSdkError(Exception):
    """Base class for exceptions in Isogeo Python SDK package."""

    pass


class AlreadyExistError(IsogeoSdkError):
    """An object with similar properties already exists in Isogeo database."""

    pass
