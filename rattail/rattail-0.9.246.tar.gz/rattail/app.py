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
App Handler
"""

from __future__ import unicode_literals, absolute_import

import os
# import re
import tempfile
import warnings
import logging

import six

from rattail.util import (load_object, load_entry_points,
                          OrderedDict, progress_loop, pretty_quantity)
from rattail.files import temp_path
from rattail.mail import send_email
from rattail.config import parse_list
from rattail.core import get_uuid, Object


log = logging.getLogger(__name__)


class AppHandler(object):
    """
    Base class and default implementation for top-level Rattail app handler.

    aka. "the handler to handle all handlers"

    aka. "one handler to bind them all"
    """
    default_autocompleters = {
        'brands': 'rattail.autocomplete.brands:BrandAutocompleter',
        'customers': 'rattail.autocomplete.customers:CustomerAutocompleter',
        'customers.neworder': 'rattail.autocomplete.customers:CustomerNewOrderAutocompleter',
        'customers.phone': 'rattail.autocomplete.customers:CustomerPhoneAutocompleter',
        'employees': 'rattail.autocomplete.employees:EmployeeAutocompleter',
        'departments': 'rattail.autocomplete.departments:DepartmentAutocompleter',
        'people': 'rattail.autocomplete.people:PersonAutocompleter',
        'people.employees': 'rattail.autocomplete.people:PersonEmployeeAutocompleter',
        'people.neworder': 'rattail.autocomplete.people:PersonNewOrderAutocompleter',
        'products': 'rattail.autocomplete.products:ProductAutocompleter',
        'products.all': 'rattail.autocomplete.products:ProductAllAutocompleter',
        'products.neworder': 'rattail.autocomplete.products:ProductNewOrderAutocompleter',
        'vendors': 'rattail.autocomplete.vendors:VendorAutocompleter',
    }

    def __init__(self, config):
        self.config = config

        # app may not use the db layer, but if so we set the model
        try:
            self.model = config.get_model()
        except: # pragma: no cover
            pass

    def get_title(self, default=None):
        """
        Returns the configured title (name) of the app.

        Default logic invokes
        :meth:`rattail.config.RattailConfig.app_title()` to obtain the
        title.

        :param default: Value to be returned if there is no app title
           configured.

        :returns: Title for the app.
        """
        return self.config.app_title(default=default)

    def get_timezone(self, key='default'):
        """
        Returns a configured time zone.

        Default logic invokes :func:`rattail.time.timezone()` to
        obtain the time zone object.

        :param key: Unique key designating which time zone should be
           returned.  Note that most apps have only one ("default"),
           but may have others defined.
        """
        from rattail.time import timezone
        return timezone(self.config, key)

    def localtime(self, *args, **kwargs):
        """
        Produce or convert a timestamp in the default time zone.

        Default logic invokes :func:`rattail.time.localtime()` to
        obtain the timestamp.  All args and kwargs are passed directly
        to that function.

        :returns: A :class:`python:datetime.datetime` object.  Usually
           this will be timezone-aware but this will depend on the
           args and kwargs you specify.
        """
        from rattail.time import localtime
        return localtime(self.config, *args, **kwargs)

    def make_utc(self, *args, **kwargs):
        """
        Produce or convert a timestamp to UTC time zone.

        Default logic invokes :func:`rattail.time.make_utc()` to
        obtain the timestamp.  All args and kwargs are passed directly
        to that function.

        :returns: A :class:`python:datetime.datetime` object.  Usually
           this will be timezone-naive but this will depend on the
           args and kwargs you specify.
        """
        from rattail.time import make_utc
        return make_utc(*args, **kwargs)

    def load_entry_points(self, group, **kwargs): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "util.load_entry_points() function directly",
                      DeprecationWarning)
        return load_entry_points(group, **kwargs)

    def load_object(self, spec):
        """
        Import and/or load and return the object designated by the
        given spec string.

        Default logic invokes :func:`rattail.util.load_object()` to
        obtain the object.

        The syntax of the spec string is not unique to Rattail, but is
        not a universal standard, so deserves a note here.  The spec
        is basically just ``modulepath:objname`` where ``modulepath``
        is the dotted name of the full module where the object
        resides, and ``objname`` is the name of the object within that
        module.  For instance, ``rattail.app:AppHandler`` would be the
        spec for *this* class.

        Note also that the use of the word "object" may be confusing,
        as it does not signify an "instance" but rather an object in
        the generic sense.  Most often a spec will either refer to a
        class or function within the module, although any valid named
        object is possible.

        :param spec: String like ``modulepath:objname`` as described
           above.

        :returns: The object referred to by ``spec``.  If the module
           could not be imported, or did not contain an object of the
           given name, then an error will raise.
        """
        return load_object(spec)

    def next_counter_value(self, session, key, **kwargs):
        """
        Return the next counter value for the given key.

        :param session: Current session for Rattail DB.

        :param key: Unique key indicating the counter for which the
           next value should be fetched.

        :returns: Next value as integer.
        """
        dialect = session.bind.url.get_dialect().name
        if dialect != 'postgresql':
            log.debug("non-postgresql database detected; will use workaround")
            from rattail.db.util import CounterMagic
            magic = CounterMagic(self.config)
            return magic.next_value(session, key)

        # normal (uses postgresql sequence)
        sql = "select nextval('{}_seq')".format(key)
        value = session.execute(sql).scalar()
        return value

    def get_active_stores(self, session, **kwargs):
        """
        Returns the list of "active" stores.  A store is considered
        active if it is *not* marked as archived.

        :param session: Reference to current DB session.

        :returns: Possibly-empty list of
           :class:`~rattail.db.model.stores.Store` records which are
           deemed active.
        """
        import sqlalchemy as sa

        model = self.model
        return session.query(model.Store)\
                      .filter(sa.or_(
                          model.Store.archived == False,
                          model.Store.archived == None))\
                      .order_by(model.Store.id)\
                      .all()

    def get_autocompleter(self, key, **kwargs):
        """
        Returns a new :class:`~rattail.autocomplete.base.Autocompleter`
        instance corresponding to the given key, e.g. ``'products'``.

        The app handler has some hard-coded defaults for the built-in
        autocompleters (see ``default_autocompleters`` in the source
        code).  You can override any of these, and/or add your own
        with custom keys, via config, e.g.:

        .. code-block:: ini

           [rattail]
           autocomplete.products = poser.autocomplete.products:ProductAutocompleter
           autocomplete.otherthings = poser.autocomplete.things:OtherThingAutocompleter

        With the above you can then fetch your custom autocompleter with::

           autocompleter = app.get_autocompleter('otherthings')

        In any case if it can locate the class, it will create an
        instance of it and return that.

        :params key: Unique key for the type of autocompleter you
           need.  Often is a simple string, e.g. ``'customers'`` but
           sometimes there may be a "modifier" with it to get an
           autocompleter with more specific behavior.

           For instance ``'customers.phone'`` would effectively give
           you a customer autocompleter but which searched by phone
           number instead of customer name.

           Note that each key is still a simple string though, and that
           must be "unique" in the sense that only one autocompleter
           can be configured for each key.

        :returns: An :class:`~rattail.autocomplete.base.Autocompleter`
           instance if found, otherwise ``None``.
        """
        spec = self.config.get('rattail', 'autocomplete.{}'.format(key))
        if not spec:
            spec = self.default_autocompleters.get(key)
        if spec:
            return load_object(spec)(self.config)

        raise ValueError("cannot locate autocompleter for key: {}".format(key))

    def get_auth_handler(self, **kwargs):
        """
        Get the configured "auth" handler.

        :returns: The :class:`~rattail.auth.AuthHandler` instance for
           the app.
        """
        if not hasattr(self, 'auth_handler'):
            spec = self.config.get('rattail', 'auth.handler',
                                   default='rattail.auth:AuthHandler')
            factory = load_object(spec)
            self.auth_handler = factory(self.config, **kwargs)
        return self.auth_handler

    def get_batch_handler(self, key, default=None, error=True, **kwargs):
        """
        Get the configured batch handler of the given type.

        :param key: Unique key designating which type of batch handler
           is being requested.

        :param default: Spec string to be used as the default, if no
           handler is configured for the given batch type.  This spec
           string must itself refer to a ``BatchHandler`` class.

        :param error: Flag indicating whether an error should be
           raised if no handler can be found.

        :returns: A :class:`~rattail.batch.handlers.BatchHandler`
           instance of the requested type.  If no such handler can be
           found, and the ``error`` param is false, then ``None`` is
           returned; otherwise an error will raise.
        """
        # spec is assumed to come from config/settings if present,
        # otherwise caller-supplied default is assumed
        spec = self.config.get('rattail.batch', '{}.handler'.format(key),
                               default=default)

        # TODO: this probably should go away?
        # if none of the above gave us a spec, check for common 'importer' type
        if not spec and key == 'importer':
            spec = 'rattail.batch.importer:ImporterBatchHandler'

        if spec:
            Handler = self.load_object(spec)
            return Handler(self.config)

        if error:
            raise ValueError("handler spec not found for batch "
                             "type: {}".format(key))

    def get_board_handler(self, **kwargs):
        """
        Get the configured "board" handler.

        :returns: The :class:`~rattail.board.BoardHandler` instance
           for the app.
        """
        if not hasattr(self, 'board_handler'):
            from rattail.board import get_board_handler
            self.board_handler = get_board_handler(self.config, **kwargs)
        return self.board_handler

    def get_bounce_handler(self, key, **kwargs):
        """
        Get the configured email bounce handler of the given type.

        :param key: Unique key designating which type of bounce
           handler is being requested.

        :returns: A :class:`~rattail.bouncer.handler.BounceHandler`
           instance of the requested type.  If no such handler can be
           found, an error will raise.
        """
        if not hasattr(self, 'bounce_handlers'):
            self.bounce_handlers = {}

        if key not in self.bounce_handlers:
            spec = self.config.get('rattail.bouncer',
                                   '{}.handler'.format(key))
            if not spec and key == 'default':
                spec = 'rattail.bouncer:BounceHandler'
            if not spec:
                raise ValueError("bounce handler spec not found for "
                                 "type: {}".format(key))

            Handler = self.load_object(spec)
            self.bounce_handlers[key] = Handler(self.config, key)

        return self.bounce_handlers[key]

    def get_clientele_handler(self, **kwargs):
        """
        Get the configured "clientele" handler.

        :returns: The :class:`~rattail.clientele.ClienteleHandler`
           instance for the app.
        """
        if not hasattr(self, 'clientele_handler'):
            from rattail.clientele import get_clientele_handler
            self.clientele_handler = get_clientele_handler(self.config, **kwargs)
        return self.clientele_handler

    def get_custorder_handler(self, **kwargs):
        """
        Get the configured "customer order" handler.

        :returns: The :class:`~rattail.custorders.CustomerOrderHandler`
           instance for the app.
        """
        if not hasattr(self, 'custorder_handler'):
            spec = self.config.get('rattail', 'custorders.handler',
                                   default='rattail.custorders:CustomerOrderHandler')
            Handler = self.load_object(spec)
            self.custorder_handler = Handler(self.config)
        return self.custorder_handler

    def get_employment_handler(self, **kwargs):
        """
        Get the configured "employment" handler.

        :returns: The :class:`~rattail.employment.EmploymentHandler`
           instance for the app.
        """
        if not hasattr(self, 'employment_handler'):
            from rattail.employment import get_employment_handler
            self.employment_handler = get_employment_handler(self.config, **kwargs)
        return self.employment_handler

    def get_feature_handler(self, **kwargs):
        """
        Get the configured "feature" handler.

        :returns: The :class:`~rattail.features.handlers.FeatureHandler`
           instance for the app.
        """
        if not hasattr(self, 'feature_handler'):
            from rattail.features import FeatureHandler
            self.feature_handler = FeatureHandler(self.config, **kwargs)
        return self.feature_handler

    def get_email_handler(self, **kwargs):
        """
        Get the configured "email" handler.

        :returns: The :class:`~rattail.mail.EmailHandler` instance for
           the app.
        """
        if not hasattr(self, 'email_handler'):
            from rattail.mail import get_email_handler
            self.email_handler = get_email_handler(self.config, **kwargs)
        return self.email_handler

    def get_mail_handler(self, **kwargs): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "AppHandler.get_email_handler() instead",
                      DeprecationWarning)
        return self.get_email_handler(**kwargs)

    def get_all_import_handlers(self, ignore_errors=True, sort=False,
                                **kwargs):
        """
        Returns *all* Import/Export Handler classes which are known to
        exist, i.e.  all which are registered via ``setup.py`` for the
        various packages installed.

        This means it will include both "designated" handlers as well
        as non-designated.  See
        :meth:`get_designated_import_handlers()` if you only want the
        designated ones.

        Note that this will return the *Handler classes* and not
        *handler instances*.

        :param ignore_errors: Normally any errors which come up during
           the loading process are ignored.  Pass ``False`` here to
           force errors to raise, e.g. if you are not seeing the
           results you expect.

        :param sort: If you like the results can be sorted with a
           simple key based on "Source -> Target" labels.

        :returns: List of all registered Import/Export Handler classes.
        """
        # first load all "registered" Handler classes
        Handlers = load_entry_points('rattail.importing',
                                     ignore_errors=ignore_errors)

        # organize registered classes by spec
        specs = {}
        for Handler in six.itervalues(Handlers):
            spec = '{}:{}'.format(Handler.__module__, Handler.__name__)
            specs[spec] = Handler

        # many handlers may not be registered per se, but may be
        # designated via config.  so try to include those too
        for Handler in six.itervalues(Handlers):
            spec = self.get_designated_import_handler_spec(Handler.get_key())
            if spec and spec not in specs:
                specs[spec] = load_object(spec)

        # flatten back to simple list
        Handlers = list(specs.values())

        if sort:
            Handlers.sort(key=lambda h: (h.get_generic_host_title(),
                                         h.get_generic_local_title()))

        return Handlers

    def get_designated_import_handlers(self, with_alternates=False, **kwargs):
        """
        Returns all "designated" import/export handler instances.

        Each "handler type key" can have at most one Handler class
        which is "designated" in the config.  This method collects all
        registered handlers and then sorts out which one is
        designated, for each type key, ultimately returning only the
        designated ones.

        Note that this will return the *handler instances* and not
        *Handler classes*.

        If you have a type key and just need its designated handler,
        see :meth:`get_import_handler()`.

        See also :meth:`get_all_import_handlers()` if you need all
        registered Handler classes.

        :param with_alternates: If you specify ``True`` here then each
           designated handler returned will have an extra attribute
           named ``alternate_handlers``, which will be a list of the
           other "available" (registered) handlers which match the
           designated handler's type key.

           This is probably most / only useful for the Configuration
           UI, to allow admin to change which is designated.

        :returns: List of all designated import/export handler instances.
        """
        grouped = OrderedDict()
        for Handler in self.get_all_import_handlers(**kwargs):
            key = Handler.get_key()
            grouped.setdefault(key, []).append(Handler)

        def find_designated(key, group):
            spec = self.get_designated_import_handler_spec(key)
            if spec:
                for Handler in group:
                    if Handler.get_spec() == spec:
                        return Handler

            if len(group) == 1:
                return group[0]

        designated = []
        for key, group in six.iteritems(grouped):
            Handler = find_designated(key, group)
            if Handler:
                # nb. we must instantiate here b/c otherwise if we
                # assign the `alternate_handlers` attr onto the class,
                # it can affect subclasses as well.  not so with
                # instances though
                handler = Handler(self.config)
                if with_alternates:
                    handler.alternate_handlers = [H for H in group
                                                  if H is not Handler]
                designated.append(handler)

        return designated

    def get_import_handler(self, key, require=False, **kwargs):
        """
        Return the designated import/export handler instance, per the
        given handler type key.

        See also :meth:`get_designated_import_handlers()` if you want
        the full set of designated handlers.

        :param key: A "handler type key", e.g.
           ``'to_rattail.from_rattail.import'``.

        :param require: Specify ``True`` here if you want an error to
           be raised should no handler be found.

        :returns: The import/export handler instance corresponding to
           the given key.  If no handler can be found, then ``None``
           is returned, unless ``require`` param is true, in which
           case error is raised.
        """
        # first try to fetch the handler per designated spec
        spec = self.get_designated_import_handler_spec(key, **kwargs)
        if spec:
            Handler = self.load_object(spec)
            return Handler(self.config)

        # nothing was designated, so leverage logic which already
        # sorts out which handler is "designated" for given key
        designated = self.get_designated_import_handlers()
        for handler in designated:
            if handler.get_key() == key:
                return handler

        if require:
            raise ValueError("Cannot locate handler for key: {}".format(key))

    def get_designated_import_handler(self, *args, **kwargs): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "AppHandler.get_import_handler() instead",
                      DeprecationWarning)
        return self.get_import_handler(*args, **kwargs)

    def get_designated_import_handler_spec(self, key, require=False, **kwargs):
        """
        Return the designated import handler "spec" string for the
        given type key.

        :param key: Unique key indicating the type of import handler.

        :require: Flag indicating whether an error should be raised if no
           handler is found.

        :returns: Spec string for the designated handler.  If none is
           found, then ``None`` is returned *unless* the ``require``
           param is true, in which case an error is raised.
        """
        spec = self.config.get('rattail.importing',
                               '{}.handler'.format(key))
        if spec:
            return spec

        legacy_setting = self.config.get('rattail.importing',
                                         '{}.legacy_handler_setting'.format(key))
        if legacy_setting:
            legacy_setting = parse_list(legacy_setting)
            if len(legacy_setting) == 2:
                section, option = legacy_setting
                spec = self.config.get(section, option)
                if spec:
                    return spec

        spec = self.config.get('rattail.importing',
                               '{}.default_handler'.format(key))
        if spec:
            return spec

        if require:
            raise ValueError("Cannot locate handler spec for key: {}".format(key))

    def get_label_handler(self, **kwargs):
        """
        Get the configured "label" handler.

        See also :doc:`rattail-manual:base/handlers/other/labels`.

        :returns: The :class:`~rattail.labels.LabelHandler` instance
           for the app.
        """
        if not hasattr(self, 'label_handler'):
            spec = self.config.get('rattail', 'labels.handler',
                                   default='rattail.labels:LabelHandler')
            factory = self.load_object(spec)
            self.label_handler = factory(self.config, **kwargs)
        return self.label_handler

    def get_membership_handler(self, **kwargs):
        """
        Get the configured "membership" handler.

        See also :doc:`rattail-manual:base/handlers/other/membership`.

        :returns: The :class:`~rattail.membership.MembershipHandler`
           instance for the app.
        """
        if not hasattr(self, 'membership_handler'):
            spec = self.config.get('rattail', 'membership.handler',
                                   default='rattail.membership:MembershipHandler')
            factory = load_object(spec)
            self.membership_handler = factory(self.config, **kwargs)
        return self.membership_handler

    def get_people_handler(self, **kwargs):
        """
        Get the configured "people" handler.

        See also :doc:`rattail-manual:base/handlers/other/people`.

        :returns: The :class:`~rattail.people.PeopleHandler` instance
           for the app.
        """
        if not hasattr(self, 'people_handler'):
            spec = self.config.get('rattail', 'people.handler',
                                   default='rattail.people:PeopleHandler')
            factory = load_object(spec)
            self.people_handler = factory(self.config, **kwargs)
        return self.people_handler

    def get_products_handler(self, **kwargs):
        """
        Get the configured "products" handler.

        :returns: The :class:`~rattail.products.ProductsHandler`
           instance for the app.
        """
        if not hasattr(self, 'products_handler'):
            from rattail.products import get_products_handler
            self.products_handler = get_products_handler(self.config, **kwargs)
        return self.products_handler

    def get_report_handler(self, **kwargs):
        """
        Get the configured "reports" handler.

        :returns: The :class:`~rattail.reporting.handlers.ReportHandler`
           instance for the app.
        """
        if not hasattr(self, 'report_handler'):
            from rattail.reporting import get_report_handler
            self.report_handler = get_report_handler(self.config, **kwargs)
        return self.report_handler

    def get_problem_report_handler(self, **kwargs):
        """
        Get the configured "problem reports" handler.

        :returns: The :class:`~rattail.problems.handlers.ProblemReportHandler`
           instance for the app.
        """
        if not hasattr(self, 'problem_report_handler'):
            from rattail.problems import get_problem_report_handler
            self.problem_report_handler = get_problem_report_handler(
                self.config, **kwargs)
        return self.problem_report_handler

    def get_trainwreck_handler(self, **kwargs):
        """
        Get the configured "trainwreck" handler.

        :returns: The :class:`~rattail.trainwreck.handler.TrainwreckHandler`
           instance for the app.
        """
        if not hasattr(self, 'trainwreck_handler'):
            spec = self.config.get('trainwreck', 'handler',
                                   default='rattail.trainwreck.handler:TrainwreckHandler')
            Handler = self.load_object(spec)
            self.trainwreck_handler = Handler(self.config)
        return self.trainwreck_handler

    def get_vendor_handler(self, **kwargs):
        """
        Get the configured "vendor" handler.

        :returns: The :class:`~rattail.vendors.handler.VendorHandler`
           instance for the app.
        """
        if not hasattr(self, 'vendor_handler'):
            spec = self.config.get('rattail', 'vendors.handler',
                                   default='rattail.vendors:VendorHandler')
            factory = self.load_object(spec)
            self.vendor_handler = factory(self.config, **kwargs)
        return self.vendor_handler

    def progress_loop(self, *args, **kwargs):
        """
        Run a given function for a given sequence, and optionally show
        a progress indicator.

        Default logic invokes the :func:`rattail.util.progress_loop()`
        function; see that for more details.
        """
        return progress_loop(*args, **kwargs)

    def make_object(self, **kwargs):
        """
        Create and return a generic object.  All kwargs will be
        assigned as attributes to the object.
        """
        return Object(**kwargs)

    def get_session(self, obj):
        """
        Returns the SQLAlchemy session with which the given object is
        associated.  Simple convenience wrapper around
        :func:`sqlalchemy:sqlalchemy.orm.object_session()`.
        """
        from sqlalchemy import orm

        return orm.object_session(obj)

    def make_session(self, user=None, **kwargs):
        """
        Creates and returns a new SQLAlchemy session for the Rattail DB.

        :param user: A "user-ish" object which should be considered
           responsible for changes made during the session.  Can be
           either a :class:`~rattail.db.model.users.User` object, or
           just a (string) username.  If none is specified then the
           config will be consulted for a default.

        :returns: A :class:`rattail.db.Session` instance.
        """
        from rattail.db import Session

        # always try to set default continuum user if possible
        if 'continuum_user' not in kwargs:
            if not user:
                user = self.config.get('rattail', 'runas.default')
            if user:
                kwargs['continuum_user'] = user

        return Session(**kwargs)

    def cache_model(self, session, model, **kwargs):
        """
        Convenience method which invokes
        :func:`rattail.db.cache.cache_model()` with the given model
        and keyword arguments.
        """
        from rattail.db import cache
        return cache.cache_model(session, model, **kwargs)

    def make_temp_dir(self, **kwargs):
        """
        Create a temporary directory.  This is mostly a convenience
        wrapper around the built-in :func:`python:tempfile.mkdtemp()`.
        However by default it will attempt to place the temp folder
        underneath the configured "workdir", e.g.:

        .. code-block:: ini

           [rattail]
           workdir = /srv/envs/poser/app/work
        """
        if 'dir' not in kwargs:
            workdir = self.config.workdir(require=False)
            if workdir:
                tmpdir = os.path.join(workdir, 'tmp')
                if not os.path.exists(tmpdir):
                    os.makedirs(tmpdir)
                kwargs['dir'] = tmpdir
        return tempfile.mkdtemp(**kwargs)

    def make_temp_file(self, **kwargs):
        """
        Reserve a temporary filename.  This is mostly a convenience
        wrapper around the built-in :func:`python:tempfile.mkstemp()`.
        However by default it will attempt to place the temp file
        underneath the configured "workdir", e.g.:

        .. code-block:: ini

           [rattail]
           workdir = /srv/envs/poser/app/work
        """
        if 'dir' not in kwargs:
            workdir = self.config.workdir(require=False)
            if workdir:
                tmpdir = os.path.join(workdir, 'tmp')
                if not os.path.exists(tmpdir):
                    os.makedirs(tmpdir)
                kwargs['dir'] = tmpdir
        return temp_path(**kwargs)

    def make_uuid(self):
        """
        Generate a new UUID value.

        :returns: UUID value as 32-character string.
        """
        return get_uuid()

    def normalize_phone_number(self, number, **kwargs):
        """
        Normalize the given phone number, to a "common" format that
        can be more easily worked with for sync logic etc.  In
        practice this usually just means stripping all non-digit
        characters from the string.  The idea is that phone number
        data from any system can be "normalized" and thereby compared
        directly to see if they differ etc.

        Default logic will invoke
        :func:`rattail.db.util.normalize_phone_number()`.

        :param number: Raw phone number string e.g. as found in some
           data source.

        :returns: Normalized string.
        """
        from rattail.db.util import normalize_phone_number

        return normalize_phone_number(number)

    def phone_number_is_invalid(self, number):
        """
        This method should validate the given phone number string, and
        if the number is *not* considered valid, this method should
        return the reason.

        :param number: Raw phone number string e.g. as found in some
           data source.

        :returns: String describing reason the number is invalid, or
           ``None`` if the number is deemed valid.
        """
        # strip non-numeric chars, and make sure we have 10 left
        normal = self.normalize_phone_number(number)
        if len(normal) != 10:
            return "Phone number must have 10 digits"

    def format_phone_number(self, number):
        """
        Returns a "properly formatted" string based on the given phone
        number.

        Default logic invokes
        :func:`rattail.db.util.format_phone_number()`.

        :param number: Raw phone number string e.g. as found in some
           data source.

        :returns: Formatted phone number string.
        """
        from rattail.db.util import format_phone_number

        return format_phone_number(number)

    def make_gpc(self, value, **kwargs):
        """
        Make and return a :class:`~rattail.gpc.GPC` instance from the
        given value.

        Default logic will invoke
        :meth:`~rattail.products.ProductsHandler.make_gpc()` of the
        products handler; see also :meth:`get_products_handler()`.
        """
        products_handler = self.get_products_handler()
        return products_handler.make_gpc(value, **kwargs)

    def render_gpc(self, value, **kwargs):
        """
        Returns a human-friendly display string for the given GPC
        value.

        :param value: A :class:`~rattail.gpc.GPC` instance.

        :returns: Display string for the GPC, or ``None`` if the value
           provided is not a GPC.
        """
        if value:
            return value.pretty()

    def render_upc(self, value, **kwargs): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "render_gpc() method instead",
                      DeprecationWarning)
        return self.render_gpc(value, **kwargs)

    def render_currency(self, value, scale=2, **kwargs):
        """
        Must return a human-friendly display string for the given
        currency value, e.g. ``Decimal('4.20')`` becomes ``"$4.20"``.

        :param value: Either a :class:`python:decimal.Decimal` or
           :class:`python:float` value.

        :param scale: Number of decimal digits to be displayed.

        :returns: Display string for the value.
        """
        if value is not None:
            if value < 0:
                fmt = "(${{:0,.{}f}})".format(scale)
                return fmt.format(0 - value)
            fmt = "${{:0,.{}f}}".format(scale)
            return fmt.format(value)

    def render_quantity(self, value, **kwargs):
        """
        Return a human-friendly display string for the given quantity
        value, e.g. ``1.000`` becomes ``"1"``.

        :param value: The quantity to be rendered.

        :returns: Display string for the quantity.
        """
        return pretty_quantity(value, **kwargs)

    def render_cases_units(self, cases, units):
        """
        Render a human-friendly string showing the given number of
        cases and/or units.  For instance::

           >>> app.render_cases_units(1, None)
           '1 case'

           >>> app.render_cases_units(None, 1)
           '1 unit'

           >>> app.render_cases_units(3, 2)
           '3 cases + 2 units'

        :param cases: Number of cases (can be zero or ``None``).

        :param units: Number of units (can be zero or ``None``).

        :returns: Display string for the given values.
        """
        if cases is not None:
            label = "case" if abs(cases) == 1 else "cases"
            cases = "{} {}".format(self.render_quantity(cases), label)

        if units is not None:
            label = "unit" if abs(units) == 1 else "units"
            units = "{} {}".format(self.render_quantity(units), label)

        if cases and units:
            return "{} + {}".format(cases, units)

        return cases or units

    def render_date(self, value, **kwargs):
        """
        Return a human-friendly display string for the given date.

        :param value: A :class:`python:datetime.date` instance.

        :returns: Display string for the date.
        """
        if value is not None:
            return value.strftime('%Y-%m-%d')

    def render_datetime(self, value, **kwargs):
        """
        Return a human-friendly display string for the given datetime.
        """
        if value is not None:
            return value.strftime('%Y-%m-%d %I:%M:%S %p')

    def send_email(self, key, data={}, **kwargs):
        """
        Send an email message of the given type.

        See :func:`rattail.mail.send_email()` for more info.
        """
        send_email(self.config, key, data, **kwargs)


class GenericHandler(object):
    """
    Base class for misc. "generic" feature handlers.

    Most handlers which exist for sake of business logic, should inherit from
    this.
    """

    def __init__(self, config, **kwargs):
        self.config = config
        self.enum = self.config.get_enum()
        self.model = self.config.get_model()
        self.app = self.config.get_app()

    def progress_loop(self, *args, **kwargs): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "AppHandler.progress_loop() method instead",
                      DeprecationWarning)
        return self.app.progress_loop(*args, **kwargs)

    def get_session(self, obj): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "AppHandler.get_session() method instead",
                      DeprecationWarning)
        return self.app.get_session(obj)

    def make_session(self): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "AppHandler.make_session() method instead",
                      DeprecationWarning)
        return self.app.make_session()

    def cache_model(self, session, model, **kwargs): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "AppHandler.cache_model() method instead",
                      DeprecationWarning)
        return self.app.cache_model(session, model, **kwargs)


def make_app(config, **kwargs): # pragma: no cover
    warnings.warn("function is deprecated, please use "
                  "RattailConfig.get_app() method instead",
                  DeprecationWarning)
    return config.get_app()
