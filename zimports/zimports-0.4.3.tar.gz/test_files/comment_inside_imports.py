# engine/base.py
# Copyright (C) 2005-2018 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
from __future__ import with_statement

"""Defines :class:`.Connection` and :class:`.Engine`.

"""


import sys
from .. import exc, util, log, interfaces
from ..sql import util as sql_util
from ..sql import schema
from .interfaces import Connectable, ExceptionContext
from .util import _distill_params
import contextlib


class Connection(Connectable):
    """Provides high-level functionality for a wrapped DB-API connection.

    """

    schema_for_object = schema._schema_getter(None)
