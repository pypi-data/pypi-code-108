# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Trainwreck Handler
"""

from __future__ import unicode_literals, absolute_import

import warnings

from rattail.app import GenericHandler
from rattail.util import OrderedDict


class TrainwreckHandler(GenericHandler):
    """
    Handler for Trainwreck data and databases.
    """
    
    def get_trainwreck_engines(self, include_hidden=True):
        """
        Return an "ordered" dict with configured trainwreck DB
        engines.  Keys of the dict will correspond to the config keys
        for each DB, values will be the engines.

        :param include_hidden: Flag indicating whether the result
           should include engines which are marked as hidden.  Note
           that hidden engines *are* included by default.

        :returns: An :class:`~rattail.util.OrderedDict` instance.
        """
        engines = OrderedDict(self.config.trainwreck_engines)

        if not include_hidden:
            for key in self.get_hidden_engine_keys():
                engines.pop(key, None)

        return engines

    def get_hidden_engine_keys(self):
        """
        Return a list of database engine keys which are configured to
        be hidden from the user interface.
        """
        hidden = self.config.getlist('trainwreck.db', 'hide',
                                     default=None)
        if hidden is None:
            hidden = self.config.getlist('tailbone', 'engines.trainwreck.hidden', 
                                         default=None)
            if hidden is not None:
                warnings.warn("[tailbone] 'engines.trainwreck.hidden' is a "
                              "deprecated setting, please use "
                              "[trainwreck.db] 'hide' instead",
                              DeprecationWarning)

        return hidden or []

    def engine_is_hidden(self, key):
        """
        Returns a boolean indicating if the given Trainwreck database
        engine is configured to be hidden from the user interface.
        """
        hidden = self.get_hidden_engine_keys()
        return key in hidden

    def get_oldest_transaction_date(self, session):
        """
        Query a Trainwreck database to determine the date of the
        "oldest" transaction it contains.

        :param session: SQLAlchemy session for a Trainwreck database.

        :return: A :class:`python:datetime.date` instance representing
           the oldest transaction date contained by the database.
        """
        trainwreck = self.config.get_trainwreck_model()
        txn = session.query(trainwreck.Transaction)\
                     .order_by(trainwreck.Transaction.end_time)\
                     .first()
        if txn:
            return self.app.localtime(txn.end_time, from_utc=True).date()

    def get_newest_transaction_date(self, session):
        """
        Query a Trainwreck database to determine the date of the
        "newest" transaction it contains.

        :param session: SQLAlchemy session for a Trainwreck database.

        :return: A :class:`python:datetime.date` instance representing
           the newest transaction date contained by the database.
        """
        trainwreck = self.config.get_trainwreck_model()
        txn = session.query(trainwreck.Transaction)\
                     .order_by(trainwreck.Transaction.end_time.desc())\
                     .first()
        if txn:
            return self.app.localtime(txn.end_time, from_utc=True).date()
