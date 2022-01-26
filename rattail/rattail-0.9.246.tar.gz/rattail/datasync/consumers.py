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
DataSync Consumers
"""

from __future__ import unicode_literals, absolute_import

import warnings

from rattail import importing
from rattail.db import Session
from rattail.config import parse_list
from rattail.util import load_object


class DataSyncConsumer(object):
    """
    Base class for all DataSync consumers.
    """
    delay = 1 # seconds
    retry_attempts = 1
    retry_delay = 1 # seconds

    def __init__(self, config, key, dbkey=None, runas=None, watcher=None):
        self.config = config
        self.key = key
        self.dbkey = dbkey
        self.runas_username = runas
        self.watcher = watcher
        self.model = config.get_model()
        self.enum = config.get_enum()
        self.app = config.get_app()

    def setup(self):
        """
        This method is called when the consumer thread is first started.
        """

    def begin_transaction(self):
        """
        Called just before the consumer is asked to process changes, possibly
        via multiple batches.
        """

    def pre_process_changes(self, session, changes):
        """
        Implement any "pre-processing" logic here.

        Common example would be to establish DB connection to some
        external system(s).

        In some rare cases you may also need to "sort" the changes, to
        ensure they are processed in a particular sequence.

        :returns: If you needed to modify the list of changes, you can
           return the new list.  If this method returns ``None``
           (which the default logic does) then the original set of
           changes will be processed.
        """

    def process_changes(self, session, changes):
        """
        Process (consume) a batch of changes.
        """

    def post_process_changes(self, session, changes):
        """
        Implement any "post-processing" logic here.

        Common example would be to close DB connection for external
        system(s).
        """

    def rollback_transaction(self):
        """
        Called when any batch of changes failed to process.
        """

    def commit_transaction(self):
        """
        Called just after the consumer has successfully finished processing
        changes, possibly via multiple batches.
        """


class DataSyncImportConsumer(DataSyncConsumer):
    """
    Base class for any DataSync Consumer which leverages an Import
    Handler (and ultimately its Importers) to do the heavy lifting.
    See :doc:`rattail-manual:data/importing/index` for more about
    Importers etc.

    .. attribute:: handler

       Reference to the import/export handler to be leveraged by this
       datasync consumer.

       The handler is automatically instantiated when the consumer is
       instantiated, usually based on :attr:`handler_key`.

    .. attribute:: handler_key

       This should be the "key" of the import handler to be leveraged
       by the datasync consumer.  This will be a string designating
       the data target/source/direction, for example
       ``'to_rattail.from_corepos_api.import'``.

       The handler itself is obtained by invoking
       :meth:`rattail.app.AppHandler.get_import_handler()`.

       Note that for now, ``handler_key`` is not strictly required, as
       :attr:`handler_spec` will be used as a fallback.  But
       eventually that will likely change, with ``handler_spec`` being
       deprecated altogether and ``handler_key`` becoming required
       (unless you override :meth:`get_handler()`).

    .. attribute:: handler_spec

       This attribute should be considered deprecated; please use
       :attr:`handler_key` instead.

       If this attribute is used, it should be a "spec" string
       referencing the import handler class from which the importers
       should be obtained.

    .. attribute:: default_importers_only

       Flag indicating whether the consumer should *only* use "default"
       importers from the handler, vs. using "all" importers, when processing
       changes.  This flag is ``True`` by default, meaning only "default"
       importers will be used.

    .. attribute:: model_map

       This is a dictionary which may be used to map model names (importer
       "keys") between the host and local systems.  Keys of the dictionary
       should be the model name as it comes from the host system, in the form
       of :attr:`rattail.db.model.DataSyncChange.payload_type`.  Values of the
       dictionary should be the model name as it is found in the import
       handler, i.e. in its ``importer_keys()`` return value.

    .. attribute:: skip_local_models

       This is a list of model names, as they are found in the import handler.
    """
    handler_key = None

    # TODO: deprecate / remove this
    handler_spec = None

    default_importers_only = True
    model_map = {}
    skip_local_models = []

    def __init__(self, *args, **kwargs):
        super(DataSyncImportConsumer, self).__init__(*args, **kwargs)

        spec = kwargs.pop('handler_spec', None)
        self.handler = self.get_handler(spec)
        self.importers = self.get_importers()

    def get_handler(self, spec=None):
        """
        Return the appropriate import handler instance.

        If ``spec`` is provided, handler will conform to that.
        Otherwise the "designated" handler is got according to
        :attr:`handler_key`, by invoking
        :meth:`rattail.app.AppHandler.get_import_handler()`.  Or if
        ``handler_key`` is not set, then for now, :attr:`handler_spec`
        may be used as fallback.

        An error of some sort will be raised if no handler can be got.

        :returns: The import handler instance.
        """
        if not spec:
            if self.handler_key:
                return self.app.get_import_handler(self.handler_key,
                                                   require=True)
            spec = self.handler_spec
        factory = self.app.load_object(spec)
        return factory(self.config)

    def get_importers(self):
        """
        Returns a dictionary, keys of which are "model" names
        (e.g. ``'Product'``) and values of which are
        :class:`~rattail.importing.importers.Importer` instances.

        .. note::
           The keys must ultimately align with the
           :attr:`~rattail.db.model.datasync.DataSyncChange.payload_type`
           values, coming from the host system.  Or at least that's what will
           make life easy for the :meth:`invoke_importer()` method.
        """
        importers = self.get_importers_from_handler(
            self.handler, default_only=self.default_importers_only)

        for host_name, local_name in self.model_map.items():
            if local_name in importers:
                importers[host_name] = importers[local_name]

        if self.skip_local_models:
            for name in list(importers):
                if name in self.skip_local_models:
                    del importers[name]

        return importers

    def get_importers_from_handler(self, handler, default_only=True):
        if default_only:
            keys = handler.get_default_keys()
        else:
            keys = handler.get_importer_keys()

        importers = dict([(key, handler.get_importer(key))
                          for key in keys])
        return importers

    def process_changes(self, session, changes):
        """
        Process all changes, leveraging importer(s) as much as possible.
        """
        result = self.pre_process_changes(session, changes)
        if result is not None:
            changes = result

        if self.runas_username:
            session.set_continuum_user(self.runas_username)

        # Update all importers with current Rattail session.
        for importer in self.importers.values():
            importer.session = session

        for change in changes:
            self.invoke_importer(session, change)

        self.post_process_changes(session, changes)

    def invoke_importer(self, session, change):
        """
        For the given change, invoke the default importer behavior, if one is
        available.
        """
        importer = self.importers.get(change.payload_type)
        if importer:
            if not change.deletion:
                return self.process_change(session, importer, change)
            elif importer.allow_delete:
                return self.process_deletion(session, importer, change)

    def process_change(self, session, importer, change=None, host_object=None, host_data=None):
        """
        Invoke the importer to process the given change / host record.
        """
        if host_data is None:
            if host_object is None:
                host_object = self.get_host_object(session, change)
                if host_object is None:
                    return
            host_data = importer.normalize_host_object(host_object)
            if host_data is None:
                return
        key = importer.get_key(host_data)
        local_object = self.get_local_object(importer, key, host_data)
        if local_object:
            if importer.allow_update:
                local_data = importer.normalize_local_object(local_object)
                if importer.data_diffs(local_data, host_data) and importer.allow_update:
                    local_object = importer.update_object(local_object, host_data, local_data)
            return local_object
        elif importer.allow_create:
            return importer.create_object(key, host_data)

    def process_deletion(self, session, importer, change):
        """
        Attempt to invoke the importer, to delete a local record according to
        the change involved.
        """
        key = self.get_deletion_key(session, change)
        if key is not None:
            local_object = importer.get_local_object(key)
            if local_object and importer.allow_delete:
                return importer.delete_object(local_object)
        return False

    def get_deletion_key(self, session, change):
        return (change.payload_key,)

    def get_host_object(self, session, change):
        """
        You must override this, to return a host object from the given
        ``DataSyncChange`` instance.  Note that the host object need *not* be
        normalized, as that will be done by the importer.  (This is effectively
        the only part of the processing which is not handled by the importer.)
        """
        raise NotImplementedError

    def get_local_object(self, importer, key, host_data):
        """
        Fetch the "local" (destination) object for the given key.
        """
        return importer.get_local_object(key)


class NewDataSyncImportConsumer(DataSyncImportConsumer):

    def __init__(self, *args, **kwargs):
        super(NewDataSyncImportConsumer, self).__init__(*args, **kwargs)
        warnings.warn("class is deprecated, please use "
                      "DataSyncImportConsumder instead",
                      DeprecationWarning)


class FromRattailConsumer(DataSyncImportConsumer):
    """
    Base class for consumers which get their data from Rattail.
    """

    def get_host_object(self, session, change):
        model = self.model
        return session.query(getattr(model, change.payload_type))\
                      .get(change.payload_key)


class NullTestConsumer(DataSyncConsumer):
    """
    Consumer which simply does ignores changes, letting DataSync think they
    were processed okay.
    """

    def process_changes(self, session, changes):
        pass


class ErrorTestConsumer(DataSyncConsumer):
    """
    Consumer which always raises an error when processing changes.  Useful for
    testing error handling etc.
    """

    def process_changes(self, session, changes):
        raise RuntimeError("Fake exception, to test error handling")
