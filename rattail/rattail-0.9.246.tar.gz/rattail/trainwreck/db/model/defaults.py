# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Trainwreck *default* data models
"""

from __future__ import unicode_literals, absolute_import

from rattail.trainwreck.db import model


# TODO: this is here for sake of "full" compatibility, e.g. so caller can do:
# from rattail.trainwreck.db.model import defaults as trainwreck_model
Base = model.Base


class Transaction(model.TransactionBase, model.Base):
    """
    Represents a POS (or similar?) transaction.
    """


class TransactionItem(model.TransactionItemBase, model.Base):
    """
    Represents a line item within a transaction.
    """
    __txn_class__ = Transaction
