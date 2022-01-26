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
Data Batch Handlers
"""

from __future__ import unicode_literals, absolute_import

import os
import shutil
import datetime
import warnings
import logging

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.core import Object
from rattail.gpc import GPC
from rattail.barcodes import upce_to_upca
from rattail.db.cache import cache_model
from rattail.time import localtime, make_utc
from rattail.util import progress_loop, load_object


log = logging.getLogger(__name__)


class BatchHandler(object):
    """
    Base class and partial default implementation for batch handlers.  It is
    expected that all batch handlers will ultimately inherit from this base
    class, therefore it defines the implementation "interface" loosely
    speaking.  Custom batch handlers are welcome to supplement or override this
    as needed, and in fact must do so for certain aspects.
    """
    populate_batches = False
    populate_with_versioning = True

    refresh_with_versioning = True
    repopulate_when_refresh = False

    execute_with_versioning = True
    delete_with_versioning = True

    def __init__(self, config):
        self.config = config
        self.app = self.config.get_app()
        self.enum = config.get_enum()
        self.model = config.get_model()

    @property
    def batch_model_class(self):
        """
        Reference to the data model class of the batch type for which this
        handler is responsible,
        e.g. :class:`~rattail.db.model.batch.labels.LabelBatch`.  Each handler
        must define this (or inherit from one that does).
        """
        raise NotImplementedError("You must set the 'batch_model_class' attribute "
                                  "for class '{}'".format(self.__class__.__name__))

    @property
    def batch_key(self):
        """
        The "batch type key" for the handler, e.g. ``'labels'``.  This is not
        meant to uniquely identify the handler itself, but rather the *type* of
        batch which it handles.  Therefore multiple handlers may be defined
        which share the same ``batch_key`` - although in practice usually each
        app will need only one handler per batch type.

        If the handler doesn't define this, it will be obtained from the
        ``batch_key`` attribute of the :attr:`batch_model_class` attribute.
        """
        return self.batch_model_class.batch_key

    def get_model_title(self):
        return self.batch_model_class.get_model_title()

    def allow_versioning(self, action):
        if action == 'populate':
            return self.populate_with_versioning
        if action == 'refresh':
            return self.refresh_with_versioning
        if action == 'execute':
            return self.execute_with_versioning
        if action == 'delete':
            return self.delete_with_versioning
        raise NotImplementedError("unknown batch action: {}".format(action))

    def is_mutable(self, batch):
        """
        Returns a boolean indicating whether or not *any* modifications are to
        be allowed for the given batch.  By default this returns ``False`` if
        the batch is already executed, or has been marked complete; otherwise
        returns ``True``.
        """
        if batch.executed:
            return False
        if batch.complete:
            return False
        return True

    def consume_batch_id(self, session, as_str=False):
        """
        Consumes a new batch ID from the generator, and returns it.

        :param session: Current session for Rattail DB.

        :param as_str: Flag indicating whether the return value should be a
           string, as opposed to the default of integer.

        :returns: Batch ID as integer, or zero-padded string of 8 chars.
        """
        batch_id = self.app.next_counter_value(session, 'batch_id')
        if as_str:
            return '{:08d}'.format(batch_id)
        return batch_id

    def make_basic_batch(self, session, user=None, progress=None, **kwargs):
        """
        Make a new "basic" batch, with no customization beyond what is provided
        by ``kwargs``, which are passed directly to the batch class constructor.

        Note that the new batch instance will be added to the provided session,
        which will also be flushed.

        Callers should use :meth:`make_batch()` instead of this method.
        """
        kwargs.setdefault('rowcount', 0)
        kwargs.setdefault('complete', False)

        # we used just let the postgres sequence auto-generate the id,
        # but now we are trying to support more than just postgres,
        # and so we consume a batch id using shared logic which can
        # accommodate more than just postgres
        if 'id' not in kwargs:
            kwargs['id'] = self.consume_batch_id(session)

        # try to provide default creator
        if user and 'created_by' not in kwargs and 'created_by_uuid' not in kwargs:
            kwargs['created_by'] = user

        batch = self.batch_model_class(**kwargs)
        session.add(batch)
        session.flush()
        return batch

    def make_batch(self, session, progress=None, **kwargs):
        """
        Make and return a new batch instance.

        This is the method which callers should use.  It invokes
        :meth:`make_basic_batch()` to actually create the new batch instance,
        and then :meth:`init_batch()` to perform any extra initialization for
        it.  Note that the batch returned will *not* yet be fully populated.
        """
        batch = self.make_basic_batch(session, progress=progress, **kwargs)
        kwargs['session'] = session
        self.init_batch(batch, progress=progress, **kwargs)
        return batch

    def init_batch(self, batch, progress=None, **kwargs):
        """
        Perform extra initialization for the given batch, in whatever way might
        make sense.  Default of course is to do nothing here; handlers are free
        to override as needed.

        Note that initial population of a batch should *not* happen here; see
        :meth:`populate()` for a place to define that logic.
        """

    def make_row(self, **kwargs):
        """
        Make a new row for the batch.  Note however that the row will **not**
        be added to the batch; that should be done with :meth:`add_row()`.

        :returns: A new row object, which does *not* yet belong to any batch.
        """
        return self.batch_model_class.row_class(**kwargs)

    def add_row(self, batch, row):
        """
        Add the given row to the given batch.  This assumes it is a *new* row
        which does not yet belong to any batch.  This logic performs the
        following steps:

        The row is officially added to the batch, and is immediately
        "refreshed" via :meth:`refresh_row()`.

        The row is then examined to see if it has been marked as "removed" by
        the refresh.  If it was *not* removed then the batch's cached
        ``rowcount`` is incremented, and the :meth:`after_add_row()` hook is
        invoked.
        """
        session = orm.object_session(batch)
        with session.no_autoflush:
            batch.data_rows.append(row)
            self.refresh_row(row)
        if not row.removed:
            batch.rowcount = (batch.rowcount or 0) + 1
            self.after_add_row(batch, row)

    def after_add_row(self, batch, row):
        """
        Event hook, called immediately after the given row has been "properly"
        added to the batch.  This is a good place to update totals for the
        batch, to account for the new row, etc.
        """

    def purge_batches(self, session, before=None, before_days=90,
                      dry_run=False, delete_all_data=None,
                      progress=None, **kwargs):
        """
        Purge all batches which were executed prior to a given date.

        :param before: If provided, must be a timezone-aware datetime object.
           If not provided, it will be calculated from the current date, using
           ``before_days``.

        :param before_days: Number of days before the current date, to be used
           as the cutoff date if ``before`` is not specified.

        :param dry_run: Flag indicating that this is a "dry run" and all logic
           involved should be (made) aware of that fact.

        :param delete_all_data: Flag indicating whether *all* data should be
           deleted for each batch being purged.  This flag is passed along to
           :meth:`delete()`; see that for more info.  NOTE: This flag should
           probably be deprecated, but so far has not been...but ``dry_run``
           should be preferred for readability etc.

        :returns: Integer indicating the number of batches purged.
        """
        if delete_all_data and dry_run:
            raise ValueError("You can enable (n)either of `dry_run` or "
                             "`delete_all_data` but both cannot be True")
        delete_all_data = not dry_run

        if not before:
            before = localtime(self.config).date() - datetime.timedelta(days=before_days)
            before = datetime.datetime.combine(before, datetime.time(0))
            before = localtime(self.config, before)

        log.info("will purge '%s' batches, executed before %s",
                 self.batch_key, before.date())

        old_batches = session.query(self.batch_model_class)\
                             .filter(self.batch_model_class.executed < before)\
                             .options(orm.joinedload(self.batch_model_class.data_rows))\
                             .all()
        log.info("found %s batches to purge", len(old_batches))
        result = Object()
        result.purged = 0

        def purge(batch, i):
            self.do_delete(batch, dry_run=dry_run)
            result.purged += 1
            if i % 5 == 0:
                session.flush()

        self.progress_loop(purge, old_batches, progress,
                           message="Purging old batches")

        session.flush()
        if old_batches:
            log.info("%spurged %s '%s' batches",
                     "(would have) " if dry_run else "",
                     result.purged, self.batch_key)
        return result.purged

    @property
    def root_datadir(self):
        """
        The absolute path of the root folder in which data for this particular
        type of batch is stored.  The structure of this path is as follows:

        .. code-block:: none

           /{root_batch_data_dir}/{batch_type_key}

        * ``{root_batch_data_dir}`` - Value of the 'batch.files' option in the
          [rattail] section of config file.
        * ``{batch_type_key}`` - Unique key for the type of batch it is.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee it.
        """
        return self.config.batch_filedir(self.batch_key)

    def datadir(self, batch):
        """
        Returns the absolute path of the folder in which the batch's source
        data file(s) resides.  Note that the batch must already have been
        persisted to the database.  The structure of the path returned is as
        follows:

        .. code-block:: none

           /{root_datadir}/{uuid[:2]}/{uuid[2:]}

        * ``{root_datadir}`` - Value returned by :meth:`root_datadir()`.
        * ``{uuid[:2]}`` - First two characters of batch UUID.
        * ``{uuid[2:]}`` - All batch UUID characters *after* the first two.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee any such thing.  It
           is typically assumed that the path will have been created by a
           previous call to :meth:`make_batch()` however.
        """
        return os.path.join(self.root_datadir, batch.uuid[:2], batch.uuid[2:])

    def make_datadir(self, batch):
        """
        Returns the data folder specific to the given batch, creating if necessary.
        """
        datadir = self.datadir(batch)
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        return datadir

    # TODO: remove default attr?
    def set_input_file(self, batch, path, attr='filename'):
        """
        Assign the data file found at ``path`` to the batch.  This overwrites
        the given attribute (``attr``) of the batch and places a copy of the
        data file in the batch's data folder.
        """
        datadir = self.make_datadir(batch)
        filename = os.path.basename(path)
        shutil.copyfile(path, os.path.join(datadir, filename))
        setattr(batch, attr, filename)

    def should_populate(self, batch):
        """
        Must return a boolean indicating whether the given batch should be
        populated from an initial data source, i.e. at time of batch creation.
        Override this method if you need to inspect the batch in order to
        determine whether the populate step is needed.  Default behavior is to
        simply return the value of :attr:`populate_batches`.
        """
        return self.populate_batches

    def setup_populate(self, batch, progress=None):
        """
        Perform any setup (caching etc.) necessary for populating a batch.
        """

    def teardown_populate(self, batch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after populating a batch.
        """

    def do_populate(self, batch, user, progress=None):
        """
        Perform initial population for the batch, i.e. fill it with data rows.
        Where the handler obtains the data to do this, will vary greatly.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~populate()` method, but callers should
        *not* use that one directly.
        """
        self.setup_populate(batch, progress=progress)
        self.populate(batch, progress=progress)
        self.teardown_populate(batch, progress=progress)
        self.refresh_batch_status(batch)
        return True

    def populate(self, batch, progress=None):
        """
        Populate the batch with initial data rows.  It is assumed that the data
        source to be used will be known by inspecting various properties of the
        batch itself.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_populate()` method, but callers
        *should* use that one directly.
        """
        raise NotImplementedError("Please implement `{}.populate()` method".format(self.__class__.__name__))

    def refreshable(self, batch):
        """
        This method should return a boolean indicating whether or not the
        handler supports a "refresh" operation for the batch, given its current
        condition.  The default assumes a refresh is allowed unless the batch
        has already been executed.
        """
        if batch.executed:
            return False
        return True

    def progress_loop(self, *args, **kwargs):
        return progress_loop(*args, **kwargs)

    def setup_refresh(self, batch, progress=None):
        """
        Perform any setup (caching etc.) necessary for refreshing a batch.
        """

    def teardown_refresh(self, batch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after refreshing a batch.
        """

    def do_refresh(self, batch, user, progress=None):
        """
        Perform a full data refresh for the batch, i.e. update any data which
        may have become stale, etc.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~refresh()` method, but callers should
        *not* use that one directly.
        """
        self.refresh(batch, progress=progress)
        return True

    def refresh(self, batch, progress=None):
        """
        Perform a full data refresh for the batch.  What exactly this means will
        depend on the type of batch, and specific handler logic.

        Generally speaking this refresh is meant to use queries etc. to obtain
        "fresh" data for the batch (header) and all its rows.  In most cases
        certain data is expected to be "core" to the batch and/or rows, and
        such data will be left intact, with all *other* data values being
        re-calculated and/or reset etc.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_refresh()` method, but callers
        *should* use that one directly.
        """
        session = orm.object_session(batch)
        self.setup_refresh(batch, progress=progress)
        if self.repopulate_when_refresh:
            del batch.data_rows[:]
            batch.rowcount = 0
            session.flush()
            self.populate(batch, progress=progress)
        else:
            batch.rowcount = 0

            def refresh(row, i):
                with session.no_autoflush:
                    self.refresh_row(row)
                if not row.removed:
                    batch.rowcount += 1

            self.progress_loop(refresh, batch.active_rows(), progress,
                               message="Refreshing batch data rows")
        self.refresh_batch_status(batch)
        self.teardown_refresh(batch, progress=progress)
        return True

    def refresh_many(self, batches, user=None, progress=None):
        """
        Refresh a set of batches, with given progress.  Default behavior is to
        simply refresh each batch in succession.  Any batches which are already
        executed are skipped.

        Handlers may have to override this method if "grouping" or other
        special behavior is needed.
        """
        needs_refresh = [batch for batch in batches
                         if not batch.executed]
        if not needs_refresh:
            return

        # TODO: should perhaps try to make the progress indicator reflect the
        # "total" number of rows across all batches being refreshed?  seems
        # like that might be more accurate, for the user.  but also harder.

        for batch in needs_refresh:
            self.do_refresh(batch, user, progress=progress)

    def refresh_row(self, row):
        """
        This method will be passed a row object which has already been properly
        added to a batch, and which has basic required fields already
        populated.  This method is then responsible for further populating all
        applicable fields for the row, based on current data within the
        appropriate system(s).

        Note that in some cases this method may be called multiple times for
        the same row, e.g. once when first creating the batch and then later
        when a user explicitly refreshes the batch.  The method logic must
        account for this possibility.
        """

    def refresh_product_basics(self, row):
        """
        This method will refresh the "basic" product info for a row.  It
        assumes that the row is derived from
        :class:`~rattail.db.model.batch.core.ProductBatchRowMixin` and that
        ``row.product`` is already set to a valid product.
        """
        product = getattr(row, 'product', None)
        if not product:
            return

        row.item_id = product.item_id
        row.upc = product.upc
        row.brand_name = six.text_type(product.brand or "")
        row.description = product.description
        row.size = product.size

        department = product.department
        row.department_number = department.number if department else None
        row.department_name = department.name if department else None

        subdepartment = product.subdepartment
        row.subdepartment_number = subdepartment.number if subdepartment else None
        row.subdepartment_name = subdepartment.name if subdepartment else None

    def quick_entry(self, session, batch, entry):
        """
        Handle a "quick entry" value, e.g. from user input.  Most frequently this
        value would represent a UPC or similar "ID" value for e.g. a product record,
        and the handler's duty would be to either locate a corresponding row within
        the batch (if one exists), or else add a new row to the batch.

        In any event this method can be customized and in fact has no default
        behavior, so must be defined by a handler.

        :param session: Database sesssion.

        :param batch: Batch for which the quick entry is to be handled.  Note that
           this batch is assumed to belong to the given ``session``.

        :param entry: String value to be handled.  This is generally assumed to
           be from user input (e.g. UPC scan field) but may not always be.

        :returns: New or existing "row" object, for the batch.
        """
        raise NotImplementedError

    def locate_product_for_entry(self, session, entry, **kwargs):
        """
        TODO: Deprecated; use ProductsHandler method instead.
        """
        # don't bother if we're given empty "entry" value
        if not entry:
            return

        products_handler = self.app.get_products_handler()
        return products_handler.locate_product_for_entry(session, entry,
                                                         **kwargs)

    def remove_row(self, row):
        """
        Remove the given row from its batch, and update the batch accordingly.
        How exactly the row is "removed" is up to this method.  Default is to
        set the row's ``removed`` flag, then invoke the
        :meth:`refresh_batch_status()` method.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`do_remove_row()` method, but callers
        *should* use that one directly.
        """
        batch = row.batch
        row.removed = True
        self.refresh_batch_status(batch)

    def do_remove_row(self, row):
        """
        Remove the given row from its batch, and update the batch accordingly.
        Uses the following logic:

        If the row's ``removed`` flag is already set, does nothing and returns
        immediately.

        Otherwise, it invokes :meth:`remove_row()` and then decrements the
        batch ``rowcount`` attribute.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`remove_row()` method, but callers should
        *not* use that one directly.
        """
        if row.removed:
            return
        self.remove_row(row)
        batch = row.batch
        if batch.rowcount is not None:
            batch.rowcount -= 1

    def refresh_batch_status(self, batch):
        """
        Update the batch status, as needed.  This method does nothing by
        default, but may be overridden if the overall batch status needs to be
        updated according to the status of its rows.  This method may be
        invoked whenever rows are added, removed, updated etc.
        """

    def write_worksheet(self, batch, progress=None):
        """
        Write a worksheet file, to be downloaded by the user.  Must return the
        file path.
        """
        raise NotImplementedError("Please define logic for `{}.write_worksheet()`".format(
            self.__class__.__name__))

    def update_from_worksheet(self, batch, path, progress=None):
        """
        Save the given file to a batch-specific location, then update the
        batch data from the file contents.
        """
        raise NotImplementedError("Please define logic for `{}.update_from_worksheet()`".format(
            self.__class__.__name__))

    def mark_complete(self, batch, progress=None):
        """
        Mark the given batch as "complete".  This usually is just a matter of
        setting the :attr:`~rattail.db.model.batch.BatchMixin.complete` flag
        for the batch, with the idea that this should "freeze" the batch so
        that another user can verify its state before finally executing it.

        Each handler is of course free to expound on this idea, or to add extra
        logic to this "event" of marking a batch complete.
        """
        batch.complete = True

    def mark_incomplete(self, batch, progress=None):
        """
        Mark the given batch as "incomplete" (aka. pending).  This usually is
        just a matter of clearing the
        :attr:`~rattail.db.model.batch.BatchMixin.complete` flag for the batch,
        with the idea that this should "thaw" the batch so that it may be
        further updated, i.e. it's not yet ready to execute.

        Each handler is of course free to expound on this idea, or to add extra
        logic to this "event" of marking a batch incomplete.
        """
        batch.complete = False

    def why_not_execute(self, batch):
        """
        This method should inspect the given batch and, if there is a reason
        that execution should *not* be allowed for it, the method should return
        a text string indicating that reason.  It should return ``None`` if no
        such reason could be identified, and execution should be allowed.

        Note that it is assumed the batch has not already been executed, since
        execution is globally prevented for such batches.  In other words you
        needn't check for that as a possible reason not to execute.
        """

    def executable(self, batch):
        """
        This method should return a boolean indicating whether or not execution
        should be allowed for the batch, given its current condition.

        While you may override this method, you are encouraged to override
        :meth:`why_not_execute()` instead.  Default logic for this method is as
        follows:

        If the batch is ``None`` then the caller simply wants to know if "any"
        batch may be executed, so we return ``True``.

        If the batch has already been executed then we return ``False``.

        If the :meth:`why_not_execute()` method returns a value, then we assume
        execution is not allowed and return ``False``.

        Finally we will return ``True`` if none of the above rules matched.
        """
        if batch is None:
            return True
        if batch.executed:
            return False
        if self.why_not_execute(batch):
            return False
        return True

    def auto_executable(self, batch):
        """
        Must return a boolean indicating whether the given bath is eligible for
        "automatic" execution, i.e. immediately after batch is created.
        """
        return False

    def describe_execution(self, batch, **kwargs):
        """
        This method should essentially return some text describing briefly what
        will happen when the given batch is executed.

        :param batch: The batch in question, which is a candidate for
           execution.

        :returns: String value describing the batch execution.
        """

    def do_execute(self, batch, user, progress=None, **kwargs):
        """
        Perform final execution for the batch.  What that means for any given
        batch, will vary greatly.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~execute()` method, but callers should
        *not* use that one directly.
        """
        # make sure we declare who's responsible, if we can
        session = orm.object_session(batch)
        session.set_continuum_user(user)

        result = self.execute(batch, user=user, progress=progress, **kwargs)
        if not result:
            return False
        batch.executed = make_utc()
        batch.executed_by = user
        return result

    def get_effective_rows(self, batch):
        """
        Should return the set of rows from the given batch which are
        considered "effective" - i.e. when the batch is executed,
        these rows should be processed whereas the remainder should
        not.

        :param batch: A
           :class:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatch`
           instance.

        :returns: List of
           :class:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatchRow`
           instances.
        """
        return batch.active_rows()

    def execute(self, batch, progress=None, **kwargs):
        """
        Execute the given batch, according to the given kwargs.  This is really
        where the magic happens, although each handler must define that magic,
        since the default logic does nothing at all.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_execute()` method, but callers
        *should* use that one directly.
        """

    def execute_many(self, batches, progress=None, **kwargs):
        """
        Execute a set of batches, with given progress and kwargs.  Default
        behavior is to simply execute each batch in succession.  Any batches
        which are already executed are skipped.

        Handlers may have to override this method if "grouping" or other
        special behavior is needed.
        """
        now = make_utc()
        for batch in batches:
            if not batch.executed:
                self.execute(batch, progress=progress, **kwargs)
                batch.executed = now
                batch.executed_by = kwargs['user']
        return True

    def do_delete(self, batch, dry_run=False, progress=None, **kwargs):
        """
        Totally delete the given batch.  This includes deleting the batch
        itself, any rows and "extra" data such as files.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~delete()` method, but callers should
        *not* use that one directly.
        """
        session = orm.object_session(batch)

        if 'delete_all_data' in kwargs:
            warnings.warn("The 'delete_all_data' kwarg is not supported for "
                          "this method; please use 'dry_run' instead",
                          DeprecationWarning)
        kwargs['delete_all_data'] = not dry_run

        self.delete(batch, progress=progress, **kwargs)
        session.delete(batch)

    def delete(self, batch, delete_all_data=True, progress=None, **kwargs):
        """
        Delete all data for the batch, including any related (e.g. row)
        records, as well as files on disk etc.  This method should *not* delete
        the batch itself however.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_delete()` method, but callers
        *should* use that one directly.

        :param delete_all_data: Flag indicating whether *all* data should be
           deleted.  You should probably set this to ``False`` if in dry-run
           mode, since deleting *all* data often implies deleting files from
           disk, which is not transactional and therefore can't be rolled back.
        """
        if delete_all_data:
            self.delete_extra_data(batch, progress=progress)

        # delete all rows from batch, one by one.  maybe would be nicer if we
        # could delete all in one fell swoop, but sometimes "extension" row
        # records might exist, and can get FK constraint errors
        # TODO: in other words i don't even know why this is necessary.  seems
        # to me that one fell swoop should not incur FK errors
        if hasattr(batch, 'data_rows'):
            session = orm.object_session(batch)

            def delete(row, i):
                session.delete(row)
                if i % 200 == 0:
                    session.flush()

            self.progress_loop(delete, batch.data_rows, progress,
                               message="Deleting rows from batch")
            session.flush()

            # even though we just deleted all rows, we must also "remove" all
            # rows explicitly from the batch; otherwise when the batch itself
            # is deleted, SQLAlchemy may complain about an unexpected number of
            # rows being deleted
            del batch.data_rows[:]

    def delete_extra_data(self, batch, progress=None, **kwargs):
        """
        Delete all "extra" data for the batch.  This method should *not* bother
        trying to delete the batch itself, or rows thereof.  It typically is
        only concerned with deleting extra files on disk, related to the batch.
        """
        path = self.config.batch_filepath(self.batch_key, batch.uuid)
        if os.path.exists(path):
            shutil.rmtree(path)

    def setup_clone(self, oldbatch, progress=None):
        """
        Perform any setup (caching etc.) necessary for cloning batch.  Note
        that the ``oldbatch`` arg is the "old" batch, i.e. the one from which a
        clone is to be created.
        """

    def teardown_clone(self, newbatch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after cloning a batch.
        Note that the ``newbatch`` arg is the "new" batch, i.e. the one which
        was just created by cloning the old batch.
        """

    def clone(self, oldbatch, created_by, progress=None):
        """
        Clone the given batch as a new batch, and return the new batch.
        """
        self.setup_clone(oldbatch, progress=progress)
        batch_class = self.batch_model_class
        batch_mapper = orm.class_mapper(batch_class)

        newbatch = batch_class()
        newbatch.created_by = created_by
        newbatch.rowcount = 0
        for name in batch_mapper.columns.keys():
            if name not in ('uuid', 'id', 'created', 'created_by_uuid', 'rowcount', 'executed', 'executed_by_uuid'):
                setattr(newbatch, name, getattr(oldbatch, name))

        session = orm.object_session(oldbatch)
        session.add(newbatch)
        session.flush()

        row_class = newbatch.row_class
        row_mapper = orm.class_mapper(row_class)

        def clone_row(oldrow, i):
            newrow = self.clone_row(oldrow)
            self.add_row(newbatch, newrow)

        self.progress_loop(clone_row, oldbatch.data_rows, progress,
                           message="Cloning data rows for new batch")

        self.refresh_batch_status(newbatch)
        self.teardown_clone(newbatch, progress=progress)
        return newbatch

    def clone_row(self, oldrow):
        row_class = self.batch_model_class.row_class
        row_mapper = orm.class_mapper(row_class)
        newrow = row_class()
        for name in row_mapper.columns.keys():
            if name not in ('uuid', 'batch_uuid', 'sequence'):
                setattr(newrow, name, getattr(oldrow, name))
        return newrow

    def cache_model(self, session, model, **kwargs):
        return cache_model(session, model, **kwargs)


def get_batch_types(config):
    """
    Returns the list of available batch type keys.
    """
    model = config.get_model()

    keys = []
    for name in dir(model):
        if name == 'BatchMixin':
            continue
        obj = getattr(model, name)
        if isinstance(obj, type):
            if issubclass(obj, model.Base):
                if issubclass(obj, model.BatchMixin):
                    keys.append(obj.batch_key)

    keys.sort()
    return keys


def get_batch_handler(config, batch_key, default=None, error=True): # pragma: no cover
    warnings.warn("function is deprecated; please use "
                  "`app.get_batch_handler() instead",
                  DeprecationWarning)
    app = config.get_app()
    return app.get_batch_handler(batch_key, default=default, error=error)
