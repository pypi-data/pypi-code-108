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
Trainwreck model importers
"""

from __future__ import unicode_literals, absolute_import

import datetime

from sqlalchemy import orm

from rattail import importing
from rattail.time import localtime, make_utc
from .util import ToOrFromTrainwreck


class ToTrainwreck(ToOrFromTrainwreck, importing.ToSQLAlchemy):
    """
    Base class for all Trainwreck model importers
    """
    key = 'uuid'


class TransactionImporter(ToTrainwreck):
    """
    Transaction data importer
    """
    @property
    def importing_from_system(self):
        raise NotImplementedError("TODO: please define this for your subclass")

    def get_model_class(self):
        if hasattr(self, 'model_class') and self.model_class:
            return self.model_class
        trainwreck = self.config.get_trainwreck_model()
        return trainwreck.Transaction

    def cache_query(self):
        query = super(TransactionImporter, self).cache_query()
        try:
            system = self.importing_from_system
        except NotImplementedError:
            pass
        else:
            query = query.filter(self.model_class.system == system)
        return query.filter(self.model_class.end_time >= make_utc(self.start_time))\
                    .filter(self.model_class.end_time < make_utc(self.end_time))


class TransactionItemImporter(ToTrainwreck):
    """
    Transaction item data importer
    """

    @property
    def supported_fields(self):
        fields = super(TransactionItemImporter, self).supported_fields
        fields = list(fields)
        fields.extend([
            'transaction_system_id',
        ])
        return fields

    @property
    def importing_from_system(self):
        raise NotImplementedError("TODO: please define this for your subclass")

    def get_model_class(self):
        if hasattr(self, 'model_class') and self.model_class:
            return self.model_class
        trainwreck = self.config.get_trainwreck_model()
        return trainwreck.TransactionItem

    @property
    def transaction_class(self):
        trainwreck = self.config.get_trainwreck_model()
        return trainwreck.Transaction

    def setup(self):
        super(TransactionItemImporter, self).setup()

        if 'transaction_system_id' in self.fields:
            trainwreck = self.config.get_trainwreck_model()
            query = self.session.query(trainwreck.Transaction)
            try:
                system = self.importing_from_system
            except NotImplementedError:
                pass
            else:
                query = query.filter(trainwreck.Transaction.system == system)
            query = query.filter(trainwreck.Transaction.end_time >= make_utc(self.start_time))\
                         .filter(trainwreck.Transaction.end_time < make_utc(self.end_time))
            self.transactions_by_system_id = self.cache_model(trainwreck.Transaction,
                                                              query=query,
                                                              key='system_id')

    def normalize_local_object(self, item):
        data = super(TransactionItemImporter, self).normalize_local_object(item)
        if data:
            if 'transaction_system_id' in self.fields:
                data['transaction_system_id'] = item.transaction.system_id
            return data

    def cache_query(self):
        trainwreck = self.config.get_trainwreck_model()
        query = super(TransactionItemImporter, self).cache_query()
        try:
            system = self.importing_from_system
        except NotImplementedError:
            pass
        else:
            query = query.filter(trainwreck.Transaction.system == system)
        return query.join(trainwreck.Transaction)\
                    .filter(trainwreck.Transaction.end_time >= make_utc(self.start_time))\
                    .filter(trainwreck.Transaction.end_time < make_utc(self.end_time))

    def get_transaction_by_system_id(self, system_id):
        if hasattr(self, 'transactions_by_system_id'):
            return self.transactions_by_system_id.get(system_id)

        trainwreck = self.config.get_trainwreck_model()
        query = self.session.query(trainwreck.Transaction)\
                            .filter(trainwreck.Transaction.system_id == system_id)
        try:
            system = self.importing_from_system
        except NotImplementedError:
            pass
        else:
            query = query.filter(trainwreck.Transaction.system == system)
        try:
            return query.one()
        except orm.exc.NoResultFound:
            pass

    def create_object(self, key, host_data):
        item = super(TransactionItemImporter, self).create_object(key, host_data)
        if item:

            # we may have to explicitly assign the transaction, if that uuid
            # wasn't part of our key
            # TODO: actually we do this if system_id was part of the key and do
            # not really look at uuid.  is there a better way to do or explain?
            # TODO: this also may fail outright if we get a bad system_id etc.
            if 'transaction_system_id' in self.key:
                system_id = host_data['transaction_system_id']
                txn = self.get_transaction_by_system_id(system_id)
                if not txn:
                    raise RuntimeError("transaction not found for system_id: {}".format(system_id))
                item.transaction = txn

            return item
