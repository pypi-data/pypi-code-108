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
Model Master View
"""

from __future__ import unicode_literals, absolute_import

import os
import csv
import datetime
import shutil
import tempfile
import logging

import json
import six
import sqlalchemy as sa
from sqlalchemy import orm
import sqlalchemy_continuum as continuum
from sqlalchemy_utils.functions import get_primary_keys, get_columns

from rattail.db import model, Session as RattailSession
from rattail.db.continuum import model_transaction_query
from rattail.util import prettify, OrderedDict, simple_error
from rattail.time import localtime
from rattail.threads import Thread
from rattail.csvutil import UnicodeDictWriter
from rattail.files import temp_path
from rattail.excel import ExcelWriter
from rattail.gpc import GPC

import colander
import deform
from pyramid import httpexceptions
from pyramid.renderers import get_renderer, render_to_response, render
from pyramid.response import FileResponse
from webhelpers2.html import HTML, tags
from webob.compat import cgi_FieldStorage

from tailbone import forms, grids, diffs
from tailbone.views import View
from tailbone.db import Session
from tailbone.config import global_help_url


log = logging.getLogger(__name__)


class EverythingComplete(Exception):
    pass


class MasterView(View):
    """
    Base "master" view class.  All model master views should derive from this.
    """
    filterable = True
    pageable = True
    checkboxes = False

    # set to True to allow user to click "anywhere" in a row in order
    # to toggle its checkbox
    clicking_row_checks_box = False

    # set to True in order to encode search values as utf-8
    use_byte_string_filters = False

    # set to True if all timestamps are "local" instead of UTC
    has_local_times = False

    listable = True
    sortable = True
    results_downloadable = False
    results_downloadable_csv = False
    results_downloadable_xlsx = False
    results_rows_downloadable = False
    creatable = True
    show_create_link = True
    viewable = True
    editable = True
    deletable = True
    delete_requires_progress = False
    delete_confirm = 'full'
    bulk_deletable = False
    set_deletable = False
    supports_autocomplete = False
    supports_set_enabled_toggle = False
    populatable = False
    mergeable = False
    downloadable = False
    cloneable = False
    touchable = False
    executable = False
    execute_progress_template = None
    execute_progress_initial_msg = None
    supports_prev_next = False
    supports_import_batch_from_file = False
    has_input_file_templates = False
    configurable = False

    # set to True to add "View *global* Objects" permission, and
    # expose / leverage the ``local_only`` object flag
    secure_global_objects = False

    # quickie (search)
    supports_quickie_search = False

    # set to True to declare model as "contact"
    is_contact = False

    listing = False
    creating = False
    creates_multiple = False
    viewing = False
    editing = False
    deleting = False
    executing = False
    cloning = False
    has_pk_fields = False
    has_image = False
    has_thumbnail = False

    # can set this to true, and set type key as needed, and implement some
    # other things also, to get a DB picker in the header for all views
    supports_multiple_engines = False
    engine_type_key = 'rattail'
    SessionDefault = None
    SessionExtras = {}

    row_attrs = {}
    cell_attrs = {}

    grid_index = None
    use_index_links = False

    has_versions = False
    help_url = None

    labels = {'uuid': "UUID"}

    product_key_fields = {}

    # ROW-RELATED ATTRS FOLLOW:

    has_rows = False
    model_row_class = None
    rows_pageable = True
    rows_sortable = True
    rows_filterable = True
    rows_viewable = True
    rows_creatable = False
    rows_editable = False
    rows_editable_but_not_directly = False
    rows_deletable = False
    rows_deletable_speedbump = True
    rows_bulk_deletable = False
    rows_default_pagesize = 20
    rows_downloadable_csv = False
    rows_downloadable_xlsx = False

    row_labels = {}

    @property
    def Session(self):
        """
        Which session we return may depend on user's "current" engine.
        """
        if self.supports_multiple_engines:
            dbkey = self.get_current_engine_dbkey()
            if dbkey != 'default' and dbkey in self.SessionExtras:
                return self.SessionExtras[dbkey]

        if self.SessionDefault:
            return self.SessionDefault

        from tailbone.db import Session
        return Session

    def make_isolated_session(self):
        """
        This method should return a newly-created SQLAlchemy Session instance.
        The use case here is primarily for secondary threads, which may be
        employed for long-running processes such as executing a batch.  The
        session returned should *not* have any web hooks to auto-commit with
        the request/response cycle etc.  It should just be a plain old session,
        "isolated" from the rest of the web app in a sense.

        So whereas ``self.Session`` by default will return a reference to
        ``tailbone.db.Session``, which is a "scoped" session wrapper specific
        to the current thread (one per request), this method should instead
        return e.g. a new independent ``rattail.db.Session`` instance.
        """
        return RattailSession()

    @classmethod
    def get_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'grid_factory', grids.Grid)

    @classmethod
    def get_row_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        row grid instances.
        """
        return getattr(cls, 'row_grid_factory', grids.Grid)

    @classmethod
    def get_version_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        version grid instances.
        """
        return getattr(cls, 'version_grid_factory', grids.Grid)

    def set_labels(self, obj):
        labels = self.collect_labels()
        for key, label in six.iteritems(labels):
            obj.set_label(key, label)

    def collect_labels(self):
        """
        Collect all labels defined within the master class hierarchy.
        """
        labels = {}
        hierarchy = self.get_class_hierarchy()
        for cls in hierarchy:
            if hasattr(cls, 'labels'):
                labels.update(cls.labels)
        return labels

    def get_class_hierarchy(self):
        hierarchy = []

        def traverse(cls):
            if cls is not object:
                hierarchy.append(cls)
                for parent in cls.__bases__:
                    traverse(parent)

        traverse(self.__class__)
        hierarchy.reverse()
        return hierarchy

    def set_row_labels(self, obj):
        labels = self.collect_row_labels()
        for key, label in six.iteritems(labels):
            obj.set_label(key, label)

    def collect_row_labels(self):
        """
        Collect all row labels defined within the master class hierarchy.
        """
        labels = {}
        hierarchy = self.get_class_hierarchy()
        for cls in hierarchy:
            if hasattr(cls, 'row_labels'):
                labels.update(cls.row_labels)
        return labels

    def has_perm(self, name):
        """
        Convenience function which returns boolean which should indicate
        whether the current user has been granted the named permission.  Note
        that this method actually assembles the permission name, using the
        ``name`` provided, but also :meth:`get_permission_prefix()`.
        """
        return self.request.has_perm('{}.{}'.format(
            self.get_permission_prefix(), name))

    def has_any_perm(self, *names):
        for name in names:
            if self.has_perm(name):
                return True
        return False

    @classmethod
    def get_config_url(cls):
        if hasattr(cls, 'config_url'):
            return cls.config_url
        return '{}/configure'.format(cls.get_url_prefix())

    ##############################
    # Available Views
    ##############################

    def index(self):
        """
        View to list/filter/sort the model data.

        If this view receives a non-empty 'partial' parameter in the query
        string, then the view will return the rendered grid only.  Otherwise
        returns the full page.
        """
        self.listing = True
        grid = self.make_grid()
        use_buefy = self.get_use_buefy()

        # If user just refreshed the page with a reset instruction, issue a
        # redirect in order to clear out the query string.
        if self.request.GET.get('reset-to-default-filters') == 'true':
            return self.redirect(self.request.current_route_url(_query=None))

        # Stash some grid stats, for possible use when generating URLs.
        if grid.pageable and hasattr(grid, 'pager'):
            self.first_visible_grid_index = grid.pager.first_item

        # return grid only, if partial page was requested
        if self.request.params.get('partial'):
            if use_buefy:
                # render grid data only, as JSON
                return render_to_response('json', grid.get_buefy_data(),
                                          request=self.request)
            else: # just do traditional thing, render grid HTML
                self.request.response.content_type = str('text/html')
                self.request.response.text = grid.render_grid()
                return self.request.response

        context = {
            'grid': grid,
        }

        if self.results_downloadable and self.has_perm('download_results'):
            route_prefix = self.get_route_prefix()
            context['download_results_path'] = self.request.session.pop(
                '{}.results.generated'.format(route_prefix), None)
            available = self.download_results_fields_available()
            context['download_results_fields_available'] = available
            context['download_results_fields_default'] = self.download_results_fields_default(available)

        if self.has_rows and self.results_rows_downloadable and self.has_perm('download_results_rows'):
            route_prefix = self.get_route_prefix()
            context['download_results_rows_path'] = self.request.session.pop(
                '{}.results_rows.generated'.format(route_prefix), None)
            available = self.download_results_fields_available()
            context['download_results_rows_fields_available'] = available
            context['download_results_rows_fields_default'] = self.download_results_rows_fields_default(available)

        self.before_render_index()
        return self.render_to_response('index', context)

    def before_render_index(self):
        """
        Perform any needed logic just prior to rendering the index
        response.  Note that this logic is invoked only when rendering
        the main index page, but *not* invoked when refreshing partial
        grid contents etc.
        """

    def make_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new grid instance
        """
        if factory is None:
            factory = self.get_grid_factory()
        if key is None:
            key = self.get_grid_key()
        if data is None:
            data = self.get_data(session=kwargs.get('session'))
        if columns is None:
            columns = self.get_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_grid(grid)
        grid.load_settings()
        return grid

    def get_effective_data(self, session=None, **kwargs):
        """
        Convenience method which returns the "effective" data for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        if session is None:
            session = self.Session()
        kwargs.setdefault('pageable', False)
        grid = self.make_grid(session=session, **kwargs)
        return grid.make_visible_data()

    def get_grid_columns(self):
        """
        Returns the default list of grid column names.  This may return
        ``None``, in which case the grid will generate its own default list.
        """
        if hasattr(self, 'grid_columns'):
            return self.grid_columns

    def make_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new grid instances.
        """
        checkboxes = kwargs.get('checkboxes', self.checkboxes)
        if not checkboxes and self.mergeable and self.has_perm('merge'):
            checkboxes = True
        if not checkboxes and self.supports_set_enabled_toggle and self.has_perm('enable_disable_set'):
            checkboxes = True
        if not checkboxes and self.set_deletable and self.has_perm('delete_set'):
            checkboxes = True

        defaults = {
            'model_class': getattr(self, 'model_class', None),
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'width': 'full',
            'filterable': self.filterable,
            'use_byte_string_filters': self.use_byte_string_filters,
            'sortable': self.sortable,
            'pageable': self.pageable,
            'extra_row_class': self.grid_extra_class,
            'url': lambda obj: self.get_action_url('view', obj),
            'checkboxes': checkboxes,
            'checked': self.checked,
            'clicking_row_checks_box': self.clicking_row_checks_box,
            'assume_local_times': self.has_local_times,
        }
        if 'main_actions' not in kwargs and 'more_actions' not in kwargs:
            main, more = self.get_grid_actions()
            defaults['main_actions'] = main
            defaults['more_actions'] = more
        defaults.update(kwargs)
        return defaults

    def configure_grid(self, grid):
        """
        Perform "final" configuration for the main data grid.
        """
        self.set_labels(grid)

        # hide "local only" grid filter, unless global access allowed
        if self.secure_global_objects:
            if not self.has_perm('view_global'):
                grid.remove('local_only')
                grid.remove_filter('local_only')

        self.configure_column_product_key(grid)

    def grid_extra_class(self, obj, i):
        """
        Returns string of extra class(es) for the table row corresponding to
        the given object, or ``None``.
        """

    def quickie(self):
        raise NotImplementedError

    def get_quickie_url(self):
        route_prefix = self.get_route_prefix()
        return self.request.route_url('{}.quickie'.format(route_prefix))

    def get_quickie_perm(self):
        permission_prefix = self.get_permission_prefix()
        return '{}.quickie'.format(permission_prefix)

    def get_quickie_placeholder(self):
        pass

    def make_row_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Make and return a new (configured) rows grid instance.
        """
        instance = kwargs.pop('instance', None)
        if not instance:
            instance = self.get_instance()

        if factory is None:
            factory = self.get_row_grid_factory()
        if key is None:
            key = self.get_row_grid_key()
        if data is None:
            data = self.get_row_data(instance)
        if columns is None:
            columns = self.get_row_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_row_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_row_grid(grid)
        grid.load_settings()
        return grid

    def get_row_grid_columns(self):
        if hasattr(self, 'row_grid_columns'):
            return self.row_grid_columns

    def make_row_grid_kwargs(self, **kwargs):
        """
        Return a dict of kwargs to be used when constructing a new rows grid.
        """
        defaults = {
            'model_class': self.model_row_class,
            'width': 'full',
            'filterable': self.rows_filterable,
            'use_byte_string_filters': self.use_byte_string_filters,
            'sortable': self.rows_sortable,
            'pageable': self.rows_pageable,
            'default_pagesize': self.rows_default_pagesize,
            'extra_row_class': self.row_grid_extra_class,
            'url': lambda obj: self.get_row_action_url('view', obj),
        }

        if self.has_rows and 'main_actions' not in defaults:
            actions = []
            use_buefy = self.get_use_buefy()

            # view action
            if self.rows_viewable:
                icon = 'eye' if use_buefy else 'zoomin'
                actions.append(self.make_action('view', icon=icon, url=self.row_view_action_url))

            # edit action
            if self.rows_editable and self.has_perm('edit_row'):
                icon = 'edit' if use_buefy else 'pencil'
                actions.append(self.make_action('edit', icon=icon, url=self.row_edit_action_url))

            # delete action
            if self.rows_deletable and self.has_perm('delete_row'):
                actions.append(self.make_action('delete', icon='trash', url=self.row_delete_action_url))
                defaults['delete_speedbump'] = self.rows_deletable_speedbump

            defaults['main_actions'] = actions

        defaults.update(kwargs)
        return defaults

    def configure_row_grid(self, grid):
        # super(MasterView, self).configure_row_grid(grid)
        self.set_row_labels(grid)

        self.configure_column_product_key(grid)

    def row_grid_extra_class(self, obj, i):
        """
        Returns string of extra class(es) for the table row corresponding to
        the given row object, or ``None``.
        """

    def make_version_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new version grid instance
        """
        instance = kwargs.pop('instance', None)
        if not instance:
            instance = self.get_instance()

        if factory is None:
            factory = self.get_version_grid_factory()
        if key is None:
            key = self.get_version_grid_key()
        if data is None:
            data = self.get_version_data(instance)
        if columns is None:
            columns = self.get_version_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_version_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_version_grid(grid)
        grid.load_settings()
        return grid

    def get_version_grid_columns(self):
        if hasattr(self, 'version_grid_columns'):
            return self.version_grid_columns
        # TODO
        return [
            'issued_at',
            'user',
            'remote_addr',
            'comment',
        ]

    def make_version_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when
        constructing a new version grid.
        """
        use_buefy = self.get_use_buefy()
        instance = kwargs.get('instance') or self.get_instance()
        route = '{}.version'.format(self.get_route_prefix())
        defaults = {
            'model_class': continuum.transaction_class(self.get_model_class()),
            'width': 'full',
            'pageable': True,
            'url': lambda txn: self.request.route_url(route, uuid=instance.uuid, txnid=txn.id),
        }
        if 'main_actions' not in kwargs:
            url = lambda txn, i: self.request.route_url(route, uuid=instance.uuid, txnid=txn.id)
            defaults['main_actions'] = [
                self.make_action('view', icon='eye' if use_buefy else 'zoomin', url=url),
            ]
        defaults.update(kwargs)
        return defaults

    def configure_version_grid(self, g):
        g.set_sort_defaults('issued_at', 'desc')
        g.set_renderer('comment', self.render_version_comment)
        g.set_label('issued_at', "Changed")
        g.set_label('user', "Changed by")
        g.set_label('remote_addr', "IP Address")

        g.set_link('issued_at')
        g.set_link('user')
        g.set_link('comment')

    def render_version_comment(self, transaction, column):
        return transaction.meta.get('comment', "")

    def create(self, form=None, template='create'):
        """
        View for creating a new model record.
        """
        self.creating = True
        if form is None:
            form = self.make_form(self.get_model_class())
        if self.request.method == 'POST':
            if self.validate_form(form):
                # let save_create_form() return alternate object if necessary
                obj = self.save_create_form(form)
                self.after_create(obj)
                self.flash_after_create(obj)
                return self.redirect_after_create(obj)
        context = {'form': form}
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response(template, context)

    def save_create_form(self, form):
        uploads = self.normalize_uploads(form)
        self.before_create(form)
        with self.Session().no_autoflush:
            obj = self.objectify(form, self.form_deserialized)
            self.before_create_flush(obj, form)
        self.Session.add(obj)
        self.Session.flush()
        self.process_uploads(obj, form, uploads)
        return obj

    def normalize_uploads(self, form, skip=None):
        uploads = {}
        for node in form.schema:
            if isinstance(node.typ, deform.FileData):
                if skip and node.name in skip:
                    continue
                # TODO: does form ever *not* have 'validated' attr here?
                if hasattr(form, 'validated'):
                    filedict = form.validated.get(node.name)
                else:
                    filedict = self.form_deserialized.get(node.name)
                if filedict:
                    tempdir = tempfile.mkdtemp()
                    filepath = os.path.join(tempdir, filedict['filename'])
                    tmpinfo = form.deform_form[node.name].widget.tmpstore.get(filedict['uid'])
                    tmpdata = tmpinfo['fp'].read()
                    with open(filepath, 'wb') as f:
                        f.write(tmpdata)
                    uploads[node.name] = {
                        'tempdir': tempdir,
                        'temp_path': filepath,
                    }
        return uploads

    def process_uploads(self, obj, form, uploads):
        pass

    def import_batch_from_file(self, handler_factory, model_name,
                               delete=False, schema=None, importer_host_title=None):

        handler = handler_factory(self.rattail_config)
        use_buefy = self.get_use_buefy()

        if not schema:
            schema = forms.SimpleFileImport().bind(request=self.request)
        form = forms.Form(schema=schema, request=self.request, use_buefy=use_buefy)
        form.save_label = "Upload"
        form.cancel_url = self.get_index_url()
        if form.validate(newstyle=True):

            uploads = self.normalize_uploads(form)
            filepath = uploads['filename']['temp_path']
            batches = handler.make_batches(model_name,
                                           delete=delete,
                                           # tdc_input_path=filepath,
                                           # source_csv_path=filepath,
                                           source_data_path=filepath,
                                           runas_user=self.request.user)
            batch = batches[0]
            return self.redirect(self.request.route_url('batch.importer.view', uuid=batch.uuid))

        if not importer_host_title:
            importer_host_title = handler.host_title

        return self.render_to_response('import_file', {
            'form': form,
            'dform': form.make_deform_form(),
            'importer_host_title': importer_host_title,
        })

    def render_truncated_value(self, obj, field):
        """
        Simple renderer which truncates the (string) value to 100 chars.
        """
        value = getattr(obj, field)
        if value is None:
            return ""
        value = six.text_type(value)
        if len(value) > 100:
            value = value[:100] + '...'
        return value

    def render_id_str(self, obj, field):
        """
        Render the ``id_str`` attribute value for the given object.
        """
        return obj.id_str

    def render_as_is(self, obj, field):
        return getattr(obj, field)

    def render_url(self, obj, field):
        url = getattr(obj, field)
        if url:
            return tags.link_to(url, url, target='_blank')

    def render_html(self, obj, field):
        html = getattr(obj, field)
        if html:
            return HTML.literal(html)

    def render_default_phone(self, obj, field):
        """
        Render the "default" (first) phone number for the given contact.
        """
        if obj.phones:
            return obj.phones[0].number

    def render_default_email(self, obj, field):
        """
        Render the "default" (first) email address for the given contact.
        """
        if obj.emails:
            return obj.emails[0].address

    # TODO: deprecate / remove this
    def render_product_key_value(self, obj, field=None):
        """
        Render the "canonical" product key value for the given object.

        nb. the ``field`` kwarg is ignored if present
        """
        product_key = self.rattail_config.product_key()
        if product_key == 'upc':
            return obj.upc.pretty() if obj.upc else ''
        return getattr(obj, product_key)

    def render_upc(self, obj, field):
        """
        Render a :class:`~rattail:rattail.gpc.GPC` field.
        """
        value = getattr(obj, field)
        if value:
            app = self.rattail_config.get_app()
            return app.render_gpc(value)

    def render_store(self, obj, field):
        store = getattr(obj, field)
        if store:
            text = "({}) {}".format(store.id, store.name)
            url = self.request.route_url('stores.view', uuid=store.uuid)
            return tags.link_to(text, url)

    def render_product(self, obj, field):
        product = getattr(obj, field)
        if not product:
            return ""
        text = six.text_type(product)
        url = self.request.route_url('products.view', uuid=product.uuid)
        return tags.link_to(text, url)

    def render_pending_product(self, obj, field):
        pending = getattr(obj, field)
        if not pending:
            return
        text = six.text_type(pending)
        url = self.request.route_url('pending_products.view', uuid=pending.uuid)
        return tags.link_to(text, url,
                            class_='has-background-warning')

    def render_vendor(self, obj, field):
        vendor = getattr(obj, field)
        if not vendor:
            return ""
        short = vendor.id or vendor.abbreviation
        if short:
            text = "({}) {}".format(short, vendor.name)
        else:
            text = six.text_type(vendor)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_department(self, obj, field):
        department = getattr(obj, field)
        if not department:
            return ""
        text = "({}) {}".format(department.number, department.name)
        url = self.request.route_url('departments.view', uuid=department.uuid)
        return tags.link_to(text, url)

    def render_subdepartment(self, obj, field):
        subdepartment = getattr(obj, field)
        if not subdepartment:
            return ""
        text = "({}) {}".format(subdepartment.number, subdepartment.name)
        url = self.request.route_url('subdepartments.view', uuid=subdepartment.uuid)
        return tags.link_to(text, url)

    def render_brand(self, obj, field):
        brand = getattr(obj, field)
        if not brand:
            return
        text = brand.name
        url = self.request.route_url('brands.view', uuid=brand.uuid)
        return tags.link_to(text, url)

    def render_category(self, obj, field):
        category = getattr(obj, field)
        if not category:
            return ""
        text = "({}) {}".format(category.code, category.name)
        url = self.request.route_url('categories.view', uuid=category.uuid)
        return tags.link_to(text, url)

    def render_family(self, obj, field):
        family = getattr(obj, field)
        if not family:
            return ""
        text = "({}) {}".format(family.code, family.name)
        url = self.request.route_url('families.view', uuid=family.uuid)
        return tags.link_to(text, url)

    def render_report(self, obj, field):
        report = getattr(obj, field)
        if not report:
            return ""
        text = "({}) {}".format(report.code, report.name)
        url = self.request.route_url('reportcodes.view', uuid=report.uuid)
        return tags.link_to(text, url)

    def render_person(self, obj, field):
        person = getattr(obj, field)
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_user(self, obj, field):
        user = getattr(obj, field)
        if not user:
            return ""
        text = six.text_type(user)
        url = self.request.route_url('users.view', uuid=user.uuid)
        return tags.link_to(text, url)

    def render_users(self, obj, field):
        users = obj.users
        if not users:
            return ""

        items = []
        for user in users:
            text = user.username
            url = self.request.route_url('users.view', uuid=user.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def render_customer(self, obj, field):
        customer = getattr(obj, field)
        if not customer:
            return ""
        text = six.text_type(customer)
        url = self.request.route_url('customers.view', uuid=customer.uuid)
        return tags.link_to(text, url)

    def before_create_flush(self, obj, form):
        pass

    def flash_after_create(self, obj):
        self.request.session.flash("{} has been created: {}".format(
            self.get_model_title(), self.get_instance_title(obj)))

    def redirect_after_create(self, instance, **kwargs):
        if self.populatable and self.should_populate(instance):
            return self.redirect(self.get_action_url('populate', instance))
        return self.redirect(self.get_action_url('view', instance))

    def should_populate(self, obj):
        return True

    def populate(self):
        """
        View for populating a new object.  What exactly this means / does will
        depend on the logic in :meth:`populate_object()`.
        """
        obj = self.get_instance()
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        # showing progress requires a separate thread; start that first
        key = '{}.populate'.format(route_prefix)
        progress = self.make_progress(key)
        thread = Thread(target=self.populate_thread, args=(obj.uuid, progress)) # TODO: uuid?
        thread.start()

        # Send user to progress page.
        kwargs = {
            'cancel_url': self.get_action_url('view', obj),
            'cancel_msg': "{} population was canceled.".format(self.get_model_title()),
        }

        return self.render_progress(progress, kwargs)

    def populate_thread(self, uuid, progress): # TODO: uuid?
        """
        Thread target for populating new object with progress indicator.
        """
        # mustn't use tailbone web session here
        session = RattailSession()
        obj = session.query(self.model_class).get(uuid)
        try:
            self.populate_object(session, obj, progress=progress)
        except Exception as error:
            session.rollback()
            msg = "{} population failed".format(self.get_model_title())
            log.warning("{}: {}".format(msg, obj), exc_info=True)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {}".format(
                    msg, simple_error(error))
                progress.session.save()
            return

        session.commit()
        session.refresh(obj)
        session.close()

        # finalize progress
        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_action_url('view', obj)
            progress.session.save()

    def populate_object(self, session, obj, progress=None):
        """
        You must define this if new objects require population.
        """
        raise NotImplementedError

    def view(self, instance=None):
        """
        View for viewing details of an existing model record.
        """
        self.viewing = True
        use_buefy = self.get_use_buefy()
        if instance is None:
            instance = self.get_instance()
        form = self.make_form(instance)
        if self.has_rows:

            # must make grid prior to redirecting from filter reset, b/c the
            # grid will detect the filter reset request and store defaults in
            # the session, that way redirect will then show The Right Thing
            grid = self.make_row_grid(instance=instance)

            # If user just refreshed the page with a reset instruction, issue a
            # redirect in order to clear out the query string.
            if self.request.GET.get('reset-to-default-filters') == 'true':
                return self.redirect(self.request.current_route_url(_query=None))

            # return grid only, if partial page was requested
            if self.request.params.get('partial'):
                if use_buefy:
                    # render grid data only, as JSON
                    return render_to_response('json', grid.get_buefy_data(),
                                              request=self.request)
                else: # just do traditional thing, render grid HTML
                    self.request.response.content_type = str('text/html')
                    self.request.response.text = grid.render_grid()
                    return self.request.response

        context = {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_editable': self.editable_instance(instance),
            'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()

        if self.has_rows:
            if use_buefy:
                context['rows_grid'] = grid
                context['rows_grid_tools'] = HTML(self.make_row_grid_tools(instance) or '').strip()
            else:
                context['rows_grid'] = grid.render_complete(allow_save_defaults=False,
                                                            tools=self.make_row_grid_tools(instance))

        return self.render_to_response('view', context)

    def image(self):
        """
        View which renders the object's image as a response.
        """
        obj = self.get_instance()
        image_bytes = self.get_image_bytes(obj)
        if not image_bytes:
            raise self.notfound()
        # TODO: how to properly detect image type?
        self.request.response.content_type = str('image/jpeg')
        self.request.response.body = image_bytes
        return self.request.response

    def get_image_bytes(self, obj):
        raise NotImplementedError

    def thumbnail(self):
        """
        View which renders the object's thumbnail image as a response.
        """
        obj = self.get_instance()
        image_bytes = self.get_thumbnail_bytes(obj)
        if not image_bytes:
            raise self.notfound()
        # TODO: how to properly detect image type?
        self.request.response.content_type = str('image/jpeg')
        self.request.response.body = image_bytes
        return self.request.response

    def get_thumbnail_bytes(self, obj):
        raise NotImplementedError

    def clone(self):
        """
        View for cloning an object's data into a new object.
        """
        self.viewing = True
        self.cloning = True
        instance = self.get_instance()
        form = self.make_form(instance)
        self.configure_clone_form(form)
        if self.request.method == 'POST' and self.request.POST.get('clone') == 'clone':
            cloned = self.clone_instance(instance)
            self.request.session.flash("{} has been cloned: {}".format(
                self.get_model_title(), self.get_instance_title(instance)))
            self.request.session.flash("(NOTE, you are now viewing the clone!)")
            return self.redirect_after_clone(cloned)
        return self.render_to_response('clone', {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_url': self.get_action_url('view', instance),
            'form': form,
        })

    def configure_clone_form(self, form):
        pass

    def clone_instance(self, instance):
        """
        This method should create and return a *new* instance, which has been
        "cloned" from the given instance.  Default behavior assumes a typical
        SQLAlchemy record instance, and the new one has all "column" values
        copied *except* for the ``'uuid'`` column.
        """
        cloned = self.model_class()

        for column in get_columns(instance):
            if column.name != 'uuid':
                setattr(cloned, column.name, getattr(instance, column.name))

        self.Session.add(cloned)
        self.Session.flush()
        return cloned

    def redirect_after_clone(self, instance, **kwargs):
        return self.redirect(self.get_action_url('view', instance))

    def touch(self):
        """
        View for "touching" an object so as to trigger datasync logic for it.
        Useful instead of actually "editing" the object, which is generally the
        alternative.
        """
        obj = self.get_instance()
        self.touch_instance(obj)
        self.request.session.flash("{} has been touched: {}".format(
            self.get_model_title(), self.get_instance_title(obj)))
        return self.redirect(self.get_action_url('view', obj))

    def touch_instance(self, obj):
        """
        Perform actual "touch" logic for the given object.
        """
        change = model.Change()
        change.class_name = obj.__class__.__name__
        change.instance_uuid = obj.uuid
        change = self.Session.merge(change)
        change.deleted = False

    def versions(self):
        """
        View to list version history for an object.
        """
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)
        grid = self.make_version_grid(instance=instance)
        use_buefy = self.get_use_buefy()

        # return grid only, if partial page was requested
        if self.request.params.get('partial'):
            if use_buefy:
                # render grid data only, as JSON
                return render_to_response('json', grid.get_buefy_data(),
                                          request=self.request)
            else: # just do traditional thing, render grid HTML
                self.request.response.content_type = str('text/html')
                self.request.response.text = grid.render_grid()
                return self.request.response

        return self.render_to_response('versions', {
            'instance': instance,
            'instance_title': instance_title,
            'instance_url': self.get_action_url('view', instance),
            'grid': grid,
        })

    @classmethod
    def get_version_grid_key(cls):
        """
        Returns the unique key to be used for the version grid, for caching
        sort/filter options etc.
        """
        if hasattr(cls, 'version_grid_key'):
            return cls.version_grid_key
        return '{}.history'.format(cls.get_route_prefix())

    def get_version_data(self, instance):
        """
        Generate the base data set for the version grid.
        """
        model_class = self.get_model_class()
        transaction_class = continuum.transaction_class(model_class)
        query = model_transaction_query(self.Session(), instance, model_class,
                                        child_classes=self.normalize_version_child_classes())
        return query.order_by(transaction_class.issued_at.desc())

    def get_version_child_classes(self):
        """
        If applicable, should return a list of child classes which should be
        considered when querying for version history of an object.
        """
        return []

    def normalize_version_child_classes(self):
        classes = []
        for cls in self.get_version_child_classes():
            if not isinstance(cls, tuple):
                cls = (cls, 'uuid', 'uuid')
            elif len(cls) == 2:
                cls = tuple([cls[0], cls[1], 'uuid'])
            classes.append(cls)
        return classes

    def view_version(self):
        """
        View showing diff details of a particular object version.
        """
        instance = self.get_instance()
        model_class = self.get_model_class()
        route_prefix = self.get_route_prefix()
        Transaction = continuum.transaction_class(model_class)
        transactions = model_transaction_query(self.Session(), instance, model_class,
                                               child_classes=self.normalize_version_child_classes())
        transaction_id = self.request.matchdict['txnid']
        transaction = transactions.filter(Transaction.id == transaction_id).first()
        if not transaction:
            return self.notfound()
        older = transactions.filter(Transaction.issued_at <= transaction.issued_at)\
                            .filter(Transaction.id != transaction_id)\
                            .order_by(Transaction.issued_at.desc())\
                            .first()
        newer = transactions.filter(Transaction.issued_at >= transaction.issued_at)\
                            .filter(Transaction.id != transaction_id)\
                            .order_by(Transaction.issued_at)\
                            .first()

        instance_title = self.get_instance_title(instance)

        prev_url = next_url = None
        if older:
            prev_url = self.request.route_url('{}.version'.format(route_prefix), uuid=instance.uuid, txnid=older.id)
        if newer:
            next_url = self.request.route_url('{}.version'.format(route_prefix), uuid=instance.uuid, txnid=newer.id)

        return self.render_to_response('view_version', {
            'instance': instance,
            'instance_title': "{} (history)".format(instance_title),
            'instance_title_normal': instance_title,
            'instance_url': self.get_action_url('versions', instance),
            'transaction': transaction,
            'changed': localtime(self.rattail_config, transaction.issued_at, from_utc=True),
            'versions': self.get_relevant_versions(transaction, instance),
            'show_prev_next': True,
            'prev_url': prev_url,
            'next_url': next_url,
            'previous_transaction': older,
            'next_transaction': newer,
            'title_for_version': self.title_for_version,
            'fields_for_version': self.fields_for_version,
            'continuum': continuum,
            'render_old_value': self.render_version_old_field_value,
            'render_new_value': self.render_version_new_field_value,
        })

    def title_for_version(self, version):
        cls = continuum.parent_class(version.__class__)
        return cls.get_model_title()

    def fields_for_version(self, version):
        mapper = orm.class_mapper(version.__class__)
        fields = sorted(mapper.columns.keys())
        fields.remove('transaction_id')
        fields.remove('end_transaction_id')
        fields.remove('operation_type')
        return fields

    def get_relevant_versions(self, transaction, instance):
        versions = []
        version_cls = self.get_model_version_class()
        query = self.Session.query(version_cls)\
                            .filter(version_cls.transaction == transaction)\
                            .filter(version_cls.uuid == instance.uuid)
        versions.extend(query.all())
        for cls, foreign_attr, primary_attr in self.normalize_version_child_classes():
            version_cls = continuum.version_class(cls)
            query = self.Session.query(version_cls)\
                                .filter(version_cls.transaction == transaction)\
                                .filter(getattr(version_cls, foreign_attr) == getattr(instance, primary_attr))
            versions.extend(query.all())
        return versions

    def render_version_old_field_value(self, version, field):
        return repr(getattr(version.previous, field))

    def render_version_new_field_value(self, version, field, typ):
        return repr(getattr(version, field))

    def configure_common_form(self, form):
        """
        Configure the form in whatever way is deemed "common" - i.e. where
        configuration should be done the same for desktop and mobile.

        By default this removes the 'uuid' field (if present), sets any primary
        key fields to be readonly (if we have a :attr:`model_class` and are in
        edit mode), and sets labels as defined by the master class hierarchy.

        TODO: this logic should be moved back into configure_form()
        """
        form.remove_field('uuid')

        if self.editing:
            model_class = self.get_model_class(error=False)
            if model_class:
                # set readonly for all primary key fields
                mapper = orm.class_mapper(model_class)
                for key in mapper.primary_key:
                    for field in form.fields:
                        if field == key.name:
                            form.set_readonly(field)
                            break

        self.set_labels(form)

        # hide "local only" field, unless global access allowed
        if self.secure_global_objects:
            if not self.has_perm('view_global'):
                form.remove_field('local_only')
            elif self.creating:
                # assume this flag should be ON by default - it is hoped this
                # is the safer option and would help prevent unwanted mistakes
                form.set_default('local_only', True)

    def make_quick_row_form(self, instance=None, factory=None, fields=None, schema=None, **kwargs):
        """
        Creates a "quick" form for adding a new row to the given instance.
        """
        if factory is None:
            factory = self.get_quick_row_form_factory()
        if fields is None:
            fields = self.get_quick_row_form_fields()
        if schema is None:
            schema = self.make_quick_row_form_schema()

        kwargs = self.make_quick_row_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_quick_row_form(form)
        return form

    def get_quick_row_form_factory(self, **kwargs):
        return forms.Form

    def get_quick_row_form_fields(self, **kwargs):
        pass

    def make_quick_row_form_schema(self, **kwargs):
        schema = colander.MappingSchema()
        schema.add(colander.SchemaNode(colander.String(), name='quick_entry'))
        return schema

    def make_quick_row_form_kwargs(self, **kwargs):
        defaults = {
            'request': self.request,
            'model_class': getattr(self, 'model_row_class', None),
            'cancel_url': self.request.get_referrer(),
        }
        defaults.update(kwargs)
        return defaults

    def configure_quick_row_form(self, form, **kwargs):
        pass

    def validate_quick_row_form(self, form):
        return form.validate(newstyle=True)

    def make_default_row_grid_tools(self, obj):
        if self.rows_creatable:
            link = tags.link_to("Create a new {}".format(self.get_row_model_title()),
                                self.get_action_url('create_row', obj))
            return HTML.tag('p', c=[link])

    def make_row_grid_tools(self, obj):
        return self.make_default_row_grid_tools(obj)

    # TODO: depracate / remove this
    def get_effective_row_query(self):
        """
        Convenience method which returns the "effective" query for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        return self.get_effective_row_data(sort=False)

    def get_row_data(self, instance):
        """
        Generate the base data set for a rows grid.
        """
        raise NotImplementedError

    def get_effective_row_data(self, session=None, sort=False, **kwargs):
        """
        Convenience method which returns the "effective" data for the row grid,
        filtered (and optionally sorted) to match what would show on the UI,
        but not paged.
        """
        if session is None:
            session = self.Session()
        kwargs.setdefault('pageable', False)
        kwargs.setdefault('sortable', sort)
        grid = self.make_row_grid(session=session, **kwargs)
        return grid.make_visible_data()

    @classmethod
    def get_row_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class, for "row" views, e.g. '/products/rows'.
        """
        return getattr(cls, 'row_url_prefix', '{}/rows'.format(cls.get_url_prefix()))

    @classmethod
    def get_row_permission_prefix(cls):
        """
        Permission prefix specific to the row-level data for this batch type,
        e.g. ``'vendorcatalogs.rows'``.
        """
        return "{}.rows".format(cls.get_permission_prefix())

    def row_editable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def row_view_action_url(self, row, i):
        return self.get_row_action_url('view', row)

    def row_edit_action_url(self, row, i):
        if self.row_editable(row):
            return self.get_row_action_url('edit', row)

    def row_delete_action_url(self, row, i):
        if self.row_deletable(row):
            return self.get_row_action_url('delete', row)

    def row_grid_row_attrs(self, row, i):
        return {}

    @classmethod
    def get_row_model_title(cls):
        if hasattr(cls, 'row_model_title'):
            return cls.row_model_title
        return "{} Row".format(cls.get_model_title())

    @classmethod
    def get_row_model_title_plural(cls):
        if hasattr(cls, 'row_model_title_plural'):
            return cls.row_model_title_plural
        return "{} Rows".format(cls.get_model_title())

    def view_index(self):
        """
        View a record according to its grid index.
        """
        try:
            index = int(self.request.GET['index'])
        except (KeyError, ValueError):
            return self.redirect(self.get_index_url())
        if index < 1:
            return self.redirect(self.get_index_url())
        data = self.get_effective_data()
        try:
            instance = data[index-1]
        except IndexError:
            return self.redirect(self.get_index_url())
        self.grid_index = index
        if hasattr(data, 'count'):
            self.grid_count = data.count()
        else:
            self.grid_count = len(data)
        return self.view(instance)

    def download(self):
        """
        View for downloading a data file.
        """
        obj = self.get_instance()
        filename = self.request.GET.get('filename', None)
        if not filename:
            raise self.notfound()
        path = self.download_path(obj, filename)
        response = FileResponse(path, request=self.request)
        response.content_length = os.path.getsize(path)
        content_type = self.download_content_type(path, filename)
        if content_type:
            if six.PY3:
                response.content_type = content_type
            else:
                response.content_type = six.binary_type(content_type)

        # content-disposition
        filename = os.path.basename(path)
        if six.PY2:
            filename = filename.encode('ascii', 'replace')
        response.content_disposition = str('attachment; filename="{}"'.format(filename))

        return response

    def download_content_type(self, path, filename):
        """
        Return a content type for a file download, if known.
        """

    def download_input_file_template(self):
        """
        View for downloading an input file template.
        """
        key = self.request.GET['key']
        filespec = self.request.GET['file']

        matches = [tmpl for tmpl in self.get_input_file_templates()
                   if tmpl['key'] == key]
        if not matches:
            raise self.notfound()

        template = matches[0]
        templatesdir = os.path.join(self.rattail_config.datadir(),
                                    'templates', 'input_files',
                                    self.get_route_prefix())
        basedir = os.path.join(templatesdir, template['key'])
        path = os.path.join(basedir, filespec)
        return self.file_response(path)

    def edit(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.editable_instance(instance):
            self.request.session.flash("Edit is not permitted for {}: {}".format(
                self.get_model_title(), instance_title), 'error')
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        if self.request.method == 'POST':
            if self.validate_form(form):
                self.save_edit_form(form)
                # note we must fetch new instance title, in case it changed
                self.request.session.flash("{} has been updated: {}".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect_after_edit(instance)

        context = {
            'instance': instance,
            'instance_title': instance_title,
            'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('edit', context)

    def save_edit_form(self, form):
        uploads = self.normalize_uploads(form)
        obj = self.objectify(form)
        self.process_uploads(obj, form, uploads)
        self.after_edit(obj)
        self.Session.flush()
        return obj

    def redirect_after_edit(self, instance, **kwargs):
        return self.redirect(self.get_action_url('view', instance))

    def delete(self):
        """
        View for deleting an existing model record.
        """
        if not self.deletable:
            raise httpexceptions.HTTPForbidden()

        self.deleting = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.deletable_instance(instance):
            self.request.session.flash("Deletion is not permitted for {}: {}".format(
                self.get_model_title(), instance_title), 'error')
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        # TODO: Add better validation, ideally CSRF etc.
        if self.request.method == 'POST':

            # Let derived classes prep for (or cancel) deletion.
            result = self.before_delete(instance)
            if isinstance(result, httpexceptions.HTTPException):
                return result

            if self.delete_requires_progress:
                return self.delete_instance_with_progress(instance)
            else:
                self.delete_instance(instance)
                self.request.session.flash("{} has been deleted: {}".format(
                    self.get_model_title(), instance_title))
                return self.redirect(self.get_after_delete_url(instance))

        form.readonly = True
        return self.render_to_response('delete', {
            'instance': instance,
            'instance_title': instance_title,
            'instance_editable': self.editable_instance(instance),
            'instance_deletable': self.deletable_instance(instance),
            'form': form})

    def bulk_delete(self):
        """
        Delete all records matching the current grid query
        """
        objects = self.get_effective_data()
        key = '{}.bulk_delete'.format(self.model_class.__tablename__)
        progress = self.make_progress(key)
        thread = Thread(target=self.bulk_delete_thread, args=(objects, progress))
        thread.start()
        return self.render_progress(progress, {
            'cancel_url': self.get_index_url(),
            'cancel_msg': "Bulk deletion was canceled",
        })

    def bulk_delete_objects(self, session, objects, progress=None):

        def delete(obj, i):
            self.delete_instance(obj)
            if i % 1000 == 0:
                session.flush()

        self.progress_loop(delete, objects, progress,
                           message="Deleting objects")

    def get_bulk_delete_session(self):
        return self.make_isolated_session()

    def bulk_delete_thread(self, objects, progress):
        """
        Thread target for bulk-deleting current results, with progress.
        """
        session = self.get_bulk_delete_session()
        objects = objects.with_session(session).all()
        try:
            self.bulk_delete_objects(session, objects, progress=progress)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("execution failed for batch results")
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Bulk deletion failed: {}".format(
                    simple_error(error))
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            session.commit()
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = self.get_index_url()
                progress.session.save()

    def obtain_set(self):
        """
        Obtain the effective "set" (selection) of records from POST data.
        """
        # TODO: should have a cleaner way to parse object uuids?
        uuids = self.request.POST.get('uuids')
        if uuids:
            uuids = uuids.split(',')
            # TODO: probably need to allow override of fetcher callable
            fetcher = lambda uuid: self.Session.query(self.model_class).get(uuid)
            objects = []
            for uuid in uuids:
                obj = fetcher(uuid)
                if obj:
                    objects.append(obj)
            return objects

    def enable_set(self):
        """
        View which can turn ON the 'enabled' flag for a specific set of records.
        """
        objects = self.obtain_set()
        if objects:
            enabled = 0
            for obj in objects:
                if not obj.enabled:
                    obj.enabled = True
                    enabled += 1
            model_title_plural = self.get_model_title_plural()
            self.request.session.flash("Enabled {} {}".format(enabled, model_title_plural))
        return self.redirect(self.get_index_url())

    def disable_set(self):
        """
        View which can turn OFF the 'enabled' flag for a specific set of records.
        """
        objects = self.obtain_set()
        if objects:
            disabled = 0
            for obj in objects:
                if obj.enabled:
                    obj.enabled = False
                    disabled += 1
            model_title_plural = self.get_model_title_plural()
            self.request.session.flash("Disabled {} {}".format(disabled, model_title_plural))
        return self.redirect(self.get_index_url())

    def delete_set(self):
        """
        View which can delete a specific set of records.
        """
        objects = self.obtain_set()
        if objects:
            for obj in objects:
                self.delete_instance(obj)
            model_title_plural = self.get_model_title_plural()
            self.request.session.flash("Deleted {} {}".format(len(objects), model_title_plural))
        return self.redirect(self.get_index_url())

    def oneoff_import(self, importer, host_object=None):
        """
        Basic helper method, to do a one-off import (or export, depending on
        perspective) of the "current instance" object.  Where the data "goes"
        depends on the importer you provide.
        """
        if not host_object:
            host_object = self.get_instance()

        host_data = importer.normalize_host_object(host_object)
        if not host_data:
            return

        key = importer.get_key(host_data)
        local_object = importer.get_local_object(key)
        if local_object:
            if importer.allow_update:
                local_data = importer.normalize_local_object(local_object)
                if importer.data_diffs(local_data, host_data) and importer.allow_update:
                    local_object = importer.update_object(local_object, host_data, local_data)
            return local_object
        elif importer.allow_create:
            return importer.create_object(key, host_data)

    def execute(self):
        """
        Execute an object.
        """
        obj = self.get_instance()
        model_title = self.get_model_title()
        progress = self.make_execute_progress(obj)

        kwargs = {'progress': progress}
        key = [self.request.matchdict[k]
               for k in self.get_model_key(as_tuple=True)]
        thread = Thread(target=self.execute_thread, args=(key, self.request.user.uuid), kwargs=kwargs)
        thread.start()

        return self.render_progress(progress, {
            'instance': obj,
            'initial_msg': self.execute_progress_initial_msg,
            'cancel_url': self.get_action_url('view', obj),
            'cancel_msg': "{} execution was canceled".format(model_title),
        }, template=self.execute_progress_template)

    def make_execute_progress(self, obj):
        key = '{}.execute'.format(self.get_grid_key())
        return self.make_progress(key)

    def get_instance_for_key(self, key, session):
        model_key = self.get_model_key(as_tuple=True)
        if len(model_key) == 1 and model_key[0] == 'uuid':
            uuid = key[0]
            return session.query(self.model_class).get(uuid)
        raise NotImplementedError

    def execute_thread(self, key, user_uuid, progress=None, **kwargs):
        """
        Thread target for executing an object.
        """
        session = RattailSession()
        obj = self.get_instance_for_key(key, session)
        user = session.query(model.User).get(user_uuid)
        try:
            success_msg = self.execute_instance(obj, user,
                                                progress=progress,
                                                **kwargs)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("{} failed to execute: {}".format(self.get_model_title(), obj))
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = self.execute_error_message(error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            session.commit()
            try:
                needs_refresh = obj in session
            except:
                pass
            else:
                if needs_refresh:
                    session.refresh(obj)
            success_url = self.get_execute_success_url(obj)
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                if success_msg:
                    progress.session['success_msg'] = success_msg
                progress.session.save()

    def execute_error_message(self, error):
        return "Execution of {} failed: {}".format(self.get_model_title(),
                                                   simple_error(error))

    def get_execute_success_url(self, obj, **kwargs):
        return self.get_action_url('view', obj, **kwargs)

    def progress_thread(self, sock, success_url, progress):
        """
        This method is meant to be used as a thread target.  Its job is to read
        progress data from ``connection`` and update the session progress
        accordingly.  When a final "process complete" indication is read, the
        socket will be closed and the thread will end.
        """
        while True:
            try:
                self.process_progress(sock, progress)
            except EverythingComplete:
                break

        # close server socket
        sock.close()

        # finalize session progress
        progress.session.load()
        progress.session['complete'] = True
        if callable(success_url):
            success_url = success_url()
        progress.session['success_url'] = success_url
        progress.session.save()

    def process_progress(self, sock, progress):
        """
        This method will accept a client connection on the given socket, and
        then update the given progress object according to data written by the
        client.
        """
        connection, client_address = sock.accept()
        active_progress = None

        # TODO: make this configurable?
        suffix = "\n\n.".encode('utf_8')
        data = b''

        # listen for progress info, update session progress as needed
        while True:

            # accumulate data bytestring until we see the suffix
            byte = connection.recv(1)
            data += byte
            if data.endswith(suffix):

                # strip suffix, interpret data as JSON
                data = data[:-len(suffix)]
                if six.PY3:
                    data = data.decode('utf_8')
                data = json.loads(data)

                if data.get('everything_complete'):
                    if active_progress:
                        active_progress.finish()
                    raise EverythingComplete

                elif data.get('process_complete'):
                    active_progress.finish()
                    active_progress = None
                    break

                elif 'value' in data:
                    if not active_progress:
                        active_progress = progress(data['message'], data['maximum'])
                    active_progress.update(data['value'])

                # reset data buffer
                data = b''

        # close client connection
        connection.close()

    def get_merge_fields(self):
        if hasattr(self, 'merge_fields'):
            return self.merge_fields
        mapper = orm.class_mapper(self.get_model_class())
        return mapper.columns.keys()

    def get_merge_coalesce_fields(self):
        if hasattr(self, 'merge_coalesce_fields'):
            return self.merge_coalesce_fields
        return []

    def get_merge_additive_fields(self):
        if hasattr(self, 'merge_additive_fields'):
            return self.merge_additive_fields
        return []

    def merge(self):
        """
        Preview and execute a merge of two records.
        """
        object_to_remove = object_to_keep = None
        if self.request.method == 'POST':
            uuids = self.request.POST.get('uuids', '').split(',')
            if len(uuids) == 2:
                object_to_remove = self.Session.query(self.get_model_class()).get(uuids[0])
                object_to_keep = self.Session.query(self.get_model_class()).get(uuids[1])

                if object_to_remove and object_to_keep and self.request.POST.get('commit-merge') == 'yes':
                    msg = six.text_type(object_to_remove)
                    try:
                        self.validate_merge(object_to_remove, object_to_keep)
                    except Exception as error:
                        self.request.session.flash("Requested merge cannot proceed (maybe swap kept/removed and try again?): {}".format(error), 'error')
                    else:
                        self.merge_objects(object_to_remove, object_to_keep)
                        self.request.session.flash("{} has been merged into {}".format(msg, object_to_keep))
                        return self.redirect(self.get_action_url('view', object_to_keep))

        if not object_to_remove or not object_to_keep or object_to_remove is object_to_keep:
            return self.redirect(self.get_index_url())

        remove = self.get_merge_data(object_to_remove)
        keep = self.get_merge_data(object_to_keep)
        return self.render_to_response('merge', {'object_to_remove': object_to_remove,
                                                 'object_to_keep': object_to_keep,
                                                 'view_url': lambda obj: self.get_action_url('view', obj),
                                                 'merge_fields': self.get_merge_fields(),
                                                 'remove_data': remove,
                                                 'keep_data': keep,
                                                 'resulting_data': self.get_merge_resulting_data(remove, keep)})

    def validate_merge(self, removing, keeping):
        """
        If applicable, your view should override this in order to confirm that
        the requested merge is valid, in your context.  If it is not - for *any
        reason* - you should raise an exception; the type does not matter.
        """

    def get_merge_data(self, obj):
        raise NotImplementedError("please implement `{}.get_merge_data()`".format(self.__class__.__name__))

    def get_merge_resulting_data(self, remove, keep):
        result = dict(keep)
        for field in self.get_merge_coalesce_fields():
            if remove[field] is not None and keep[field] is None:
                result[field] = remove[field]
            elif remove[field] and not keep[field]:
                result[field] = remove[field]
        for field in self.get_merge_additive_fields():
            if isinstance(keep[field], (list, tuple)):
                result[field] = sorted(set(remove[field] + keep[field]))
            else:
                result[field] = remove[field] + keep[field]
        return result

    def merge_objects(self, removing, keeping):
        """
        Merge the two given objects.  You should probably override this;
        default behavior is merely to delete the 'removing' object.
        """
        self.Session.delete(removing)

    ##############################
    # Core Stuff
    ##############################

    @classmethod
    def get_model_class(cls, error=True):
        """
        Returns the data model class for which the master view exists.
        """
        if not hasattr(cls, 'model_class') and error:
            raise NotImplementedError("You must define the `model_class` for: {}".format(cls))
        return getattr(cls, 'model_class', None)

    @classmethod
    def get_model_version_class(cls):
        """
        Returns the version class for the master model class.
        """
        return continuum.version_class(cls.get_model_class())

    @classmethod
    def get_normalized_model_name(cls):
        """
        Returns the "normalized" name for the view's model class.  This will be
        the value of the :attr:`normalized_model_name` attribute if defined;
        otherwise it will be a simple lower-cased version of the associated
        model class name.
        """
        if hasattr(cls, 'normalized_model_name'):
            return cls.normalized_model_name
        return cls.get_model_class().__name__.lower()

    @classmethod
    def get_model_key(cls, as_tuple=False):
        """
        Returns the primary key(s) for the model class.  Note that this will
        return a *string* value unless a tuple is requested.  If the model has
        a composite key then the string result would be a comma-delimited list
        of names, e.g. ``foo_id,bar_id``.
        """
        if hasattr(cls, 'model_key'):
            keys = cls.model_key
            if isinstance(keys, six.string_types):
                keys = [keys]
        else:
            keys = get_primary_keys(cls.get_model_class())

        if as_tuple:
            return tuple(keys)

        return ','.join(keys)

    @classmethod
    def get_model_title(cls):
        """
        Return a "humanized" version of the model name, for display in templates.
        """
        if hasattr(cls, 'model_title'):
            return cls.model_title

        # model class itself may provide title
        model_class = cls.get_model_class()
        if hasattr(model_class, 'get_model_title'):
            return model_class.get_model_title()

        # otherwise just use model class name
        return model_class.__name__

    @classmethod
    def get_model_title_plural(cls):
        """
        Return a "humanized" (and plural) version of the model name, for
        display in templates.
        """
        if hasattr(cls, 'model_title_plural'):
            return cls.model_title_plural
        try:
            return cls.get_model_class().get_model_title_plural()
        except (NotImplementedError, AttributeError):
            return '{}s'.format(cls.get_model_title())

    @classmethod
    def get_route_prefix(cls):
        """
        Returns a prefix which (by default) applies to all routes provided by
        the master view class.  This is the plural, lower-cased name of the
        model class by default, e.g. 'products'.
        """
        if hasattr(cls, 'route_prefix'):
            return cls.route_prefix
        model_name = cls.get_normalized_model_name()
        return '{}s'.format(model_name)

    @classmethod
    def get_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class.  By default this is the route prefix, preceded by a
        slash, e.g. '/products'.
        """
        return getattr(cls, 'url_prefix', '/{0}'.format(cls.get_route_prefix()))

    @classmethod
    def get_template_prefix(cls):
        """
        Returns a prefix which (by default) applies to all templates required by
        the master view class.  This uses the URL prefix by default.
        """
        return getattr(cls, 'template_prefix', cls.get_url_prefix())

    @classmethod
    def get_permission_prefix(cls):
        """
        Returns a prefix which (by default) applies to all permissions leveraged by
        the master view class.  This uses the route prefix by default.
        """
        return getattr(cls, 'permission_prefix', cls.get_route_prefix())

    def get_index_url(self, **kwargs):
        """
        Returns the master view's index URL.
        """
        route = self.get_route_prefix()
        return self.request.route_url(route, **kwargs)

    @classmethod
    def get_index_title(cls):
        """
        Returns the title for the index page.
        """
        return getattr(cls, 'index_title', cls.get_model_title_plural())

    @classmethod
    def get_config_title(cls):
        """
        Returns the view's "config title".
        """
        if hasattr(cls, 'config_title'):
            return cls.config_title

        return cls.get_model_title_plural()

    def get_action_url(self, action, instance, **kwargs):
        """
        Generate a URL for the given action on the given instance
        """
        kw = self.get_action_route_kwargs(instance)
        kw.update(kwargs)
        route_prefix = self.get_route_prefix()
        return self.request.route_url('{}.{}'.format(route_prefix, action), **kw)

    def get_help_url(self):
        """
        May return a "help URL" if applicable.  Default behavior is to simply
        return the value of :attr:`help_url` (regardless of which view is in
        effect), which in turn defaults to ``None``.  If an actual URL is
        returned, then a Help button will be shown in the page header;
        otherwise it is not shown.

        This method is invoked whenever a template is rendered for a response,
        so if you like you can return a different help URL depending on which
        type of CRUD view is in effect, etc.
        """
        if self.help_url:
            return self.help_url

        return global_help_url(self.rattail_config)

    def render_to_response(self, template, data, **kwargs):
        """
        Return a response with the given template rendered with the given data.
        Note that ``template`` must only be a "key" (e.g. 'index' or 'view').
        First an attempt will be made to render using the :attr:`template_prefix`.
        If that doesn't work, another attempt will be made using '/master' as
        the template prefix.
        """
        context = {
            'master': self,
            'use_buefy': self.get_use_buefy(),
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(),
            'config_title': self.get_config_title(),
            'action_url': self.get_action_url,
            'grid_index': self.grid_index,
            'help_url': self.get_help_url(),
            'quickie': None,
        }

        if self.expose_quickie_search:
            context['quickie'] = self.get_quickie_context()

        if self.grid_index:
            context['grid_count'] = self.grid_count

        if self.has_rows:
            context['row_permission_prefix'] = self.get_row_permission_prefix()
            context['row_model_title'] = self.get_row_model_title()
            context['row_model_title_plural'] = self.get_row_model_title_plural()
            context['row_action_url'] = self.get_row_action_url

        context.update(data)
        context.update(self.template_kwargs(**context))
        if hasattr(self, 'template_kwargs_{}'.format(template)):
            context.update(getattr(self, 'template_kwargs_{}'.format(template))(**context))

        # First try the template path most specific to the view.
        mako_path = '{}/{}.mako'.format(self.get_template_prefix(), template)
        try:
            return render_to_response(mako_path, context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template):
                try:
                    return render_to_response(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render_to_response('{}/{}.mako'.format(self.get_template_prefix(), template),
                                      context, request=self.request)

    # TODO: merge this logic with render_to_response()
    def render(self, template, data):
        """
        Render the given template with the given context data.
        """
        context = {
            'master': self,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(),
            'action_url': self.get_action_url,
        }
        context.update(data)

        # First try the template path most specific to the view.
        try:
            return render('{}/{}.mako'.format(self.get_template_prefix(), template),
                          context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template):
                try:
                    return render(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render('{}/{}.mako'.format(self.get_template_prefix(), template),
                          context, request=self.request)

    def get_fallback_templates(self, template, **kwargs):
        return ['/master/{}.mako'.format(template)]

    def get_default_engine_dbkey(self):
        """
        Returns the "default" engine dbkey.
        """
        return self.rattail_config.get(
            'tailbone',
            'engines.{}.pretend_default'.format(self.engine_type_key),
            default='default')

    def get_current_engine_dbkey(self):
        """
        Returns the "current" engine's dbkey, for the current user.
        """
        default = self.get_default_engine_dbkey()
        return self.request.session.get('tailbone.engines.{}.current'.format(self.engine_type_key),
                                        default)

    def template_kwargs(self, **kwargs):
        """
        Supplement the template context, for all views.
        """
        # whether or not to show the DB picker?
        kwargs['expose_db_picker'] = False
        if self.supports_multiple_engines:

            # view declares support for multiple engines, but we only want to
            # show the picker if we have more than one engine configured
            engines = self.get_db_engines()
            if len(engines) > 1:

                # user session determines "current" db engine *of this type*
                # (note that many master views may declare the same type, and
                # would therefore share the "current" engine)
                selected = self.get_current_engine_dbkey()
                kwargs['expose_db_picker'] = True
                kwargs['db_picker_options'] = [tags.Option(k) for k in engines]
                kwargs['db_picker_selected'] = selected

        # add info for downloadable input file templates, if any
        if self.has_input_file_templates:
            templates = self.normalize_input_file_templates()
            kwargs['input_file_templates'] = OrderedDict([(tmpl['key'], tmpl)
                                                          for tmpl in templates])

        return kwargs

    def get_input_file_templates(self):
        return []

    def normalize_input_file_templates(self, templates=None,
                                       include_file_options=False):
        if templates is None:
            templates = self.get_input_file_templates()

        route_prefix = self.get_route_prefix()

        if include_file_options:
            templatesdir = os.path.join(self.rattail_config.datadir(),
                                        'templates', 'input_files',
                                        route_prefix)

        for template in templates:

            if 'config_section' not in template:
                template['config_section'] = self.input_file_template_config_section
            section = template['config_section']

            if 'config_prefix' not in template:
                template['config_prefix'] = '{}.{}'.format(
                    self.input_file_template_config_prefix,
                    template['key'])
            prefix = template['config_prefix']

            for key in ('mode', 'file', 'url'):

                if 'option_{}'.format(key) not in template:
                    template['option_{}'.format(key)] = '{}.{}'.format(prefix, key)

                if 'setting_{}'.format(key) not in template:
                    template['setting_{}'.format(key)] = '{}.{}'.format(
                        section,
                        template['option_{}'.format(key)])

                if key not in template:
                    value = self.rattail_config.get(
                        section,
                        template['option_{}'.format(key)])
                    if value is not None:
                        template[key] = value

            template.setdefault('mode', 'default')
            template.setdefault('file', None)
            template.setdefault('url', template['default_url'])

            if include_file_options:
                options = []
                basedir = os.path.join(templatesdir, template['key'])
                if os.path.exists(basedir):
                    for name in sorted(os.listdir(basedir)):
                        if len(name) == 4 and name.isdigit():
                            files = os.listdir(os.path.join(basedir, name))
                            if len(files) == 1:
                                options.append(os.path.join(name, files[0]))
                template['file_options'] = options
                template['file_options_dir'] = basedir

            if template['mode'] == 'external':
                template['effective_url'] = template['url']
            elif template['mode'] == 'hosted':
                template['effective_url'] = self.request.route_url(
                    '{}.download_input_file_template'.format(route_prefix),
                    _query={'key': template['key'],
                            'file': template['file']})
            else:
                template['effective_url'] = template['default_url']

        return templates

    def template_kwargs_index(self, **kwargs):
        """
        Method stub, so subclass can always invoke super() for it.
        """
        return kwargs

    def template_kwargs_create(self, **kwargs):
        """
        Method stub, so subclass can always invoke super() for it.
        """
        return kwargs

    def template_kwargs_view(self, **kwargs):
        """
        Method stub, so subclass can always invoke super() for it.
        """
        return kwargs

    def template_kwargs_edit(self, **kwargs):
        """
        Method stub, so subclass can always invoke super() for it.
        """
        return kwargs

    def template_kwargs_delete(self, **kwargs):
        """
        Method stub, so subclass can always invoke super() for it.
        """
        return kwargs

    def get_db_engines(self):
        """
        Must return a dict (or even better, OrderedDict) which contains all
        supported database engines for the master view.  Used with the DB
        picker feature.
        """
        engines = OrderedDict(self.rattail_config.trainwreck_engines)
        hidden = self.rattail_config.getlist('tailbone', 'engines.rattail.hidden',
                                             default=None)
        if hidden:
            for key in hidden:
                engines.pop(key, None)
        return engines

    ##############################
    # Grid Stuff
    ##############################

    @classmethod
    def get_grid_key(cls):
        """
        Returns the unique key to be used for the grid, for caching sort/filter
        options etc.
        """
        if hasattr(cls, 'grid_key'):
            return cls.grid_key
        # default previously came from cls.get_normalized_model_name() but this is hopefully better
        return cls.get_route_prefix()

    def get_row_grid_key(self):
        model_key = self.get_model_key(as_tuple=True)
        key = '.'.join([self.get_grid_key()] +
                       [self.request.matchdict[k] for k in model_key])
        return key

    def get_grid_actions(self):
        main, more = self.get_main_actions(), self.get_more_actions()
        if len(more) == 1:
            main, more = main + more, []
        if len(main + more) <= 3:
            main, more = main + more, []
        return main, more

    def get_row_attrs(self, row, i):
        """
        Returns a dict of HTML attributes which is to be applied to the row's
        ``<tr>`` element.  Note that ``i`` will be a 1-based index value for
        the row within its table.  The meaning of ``row`` is basically not
        defined; it depends on the type of data the grid deals with.
        """
        if callable(self.row_attrs):
            attrs = self.row_attrs(row, i)
        else:
            attrs = dict(self.row_attrs)
        if self.mergeable:
            attrs['data-uuid'] = row.uuid
        return attrs

    def get_cell_attrs(self, row, column):
        """
        Returns a dictionary of HTML attributes which should be applied to the
        ``<td>`` element in which the given row and column "intersect".
        """
        if callable(self.cell_attrs):
            return self.cell_attrs(row, column)
        return self.cell_attrs

    def get_main_actions(self):
        """
        Return a list of 'main' actions for the grid.
        """
        actions = []
        if self.viewable and self.has_perm('view'):
            actions.append(self.make_grid_action_view())
        return actions

    def make_grid_action_view(self):
        use_buefy = self.get_use_buefy()
        url = self.get_view_index_url if self.use_index_links else None
        icon = 'eye' if use_buefy else 'zoomin'
        return self.make_action('view', icon=icon, url=url)

    def get_view_index_url(self, row, i):
        route = '{}.view_index'.format(self.get_route_prefix())
        return '{}?index={}'.format(self.request.route_url(route), self.first_visible_grid_index + i - 1)

    def get_more_actions(self):
        """
        Return a list of 'more' actions for the grid.
        """
        actions = []

        # Edit
        if self.editable and self.has_perm('edit'):
            actions.append(self.make_grid_action_edit())

        # Delete
        if self.deletable and self.has_perm('delete'):
            actions.append(self.make_grid_action_delete())

        return actions

    def make_grid_action_edit(self):
        use_buefy = self.get_use_buefy()
        icon = 'edit' if use_buefy else 'pencil'
        return self.make_action('edit', icon=icon, url=self.default_edit_url)

    def make_grid_action_clone(self):
        return self.make_action('clone', icon='object-ungroup',
                                url=self.default_clone_url)

    def make_grid_action_delete(self):
        use_buefy = self.get_use_buefy()
        kwargs = {}
        if use_buefy and self.delete_confirm == 'simple':
            kwargs['click_handler'] = 'deleteObject'
        return self.make_action('delete', icon='trash', url=self.default_delete_url, **kwargs)

    def default_edit_url(self, row, i=None):
        if self.editable_instance(row):
            return self.request.route_url('{}.edit'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def default_clone_url(self, row, i=None):
        return self.request.route_url('{}.clone'.format(self.get_route_prefix()),
                                      **self.get_action_route_kwargs(row))

    def default_delete_url(self, row, i=None):
        if self.deletable_instance(row):
            return self.request.route_url('{}.delete'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def make_action(self, key, url=None, factory=None, **kwargs):
        """
        Make a new :class:`GridAction` instance for the current grid.
        """
        if url is None:
            route = '{}.{}'.format(self.get_route_prefix(), key)
            url = lambda r, i: self.request.route_url(route, **self.get_action_route_kwargs(r))
        if not factory:
            factory = grids.GridAction
        return factory(key, url=url, **kwargs)

    def get_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        try:
            mapper = orm.object_mapper(row)
        except orm.exc.UnmappedInstanceError:
            try:
                if isinstance(self.model_key, six.string_types):
                    return {self.model_key: row[self.model_key]}
                return dict([(key, row[key])
                             for key in self.model_key])
            except TypeError:
                return {self.model_key: getattr(row, self.model_key)}
        else:
            pkeys = get_primary_keys(row)
            keys = list(pkeys)
            values = [getattr(row, k) for k in keys]
            return dict(zip(keys, values))

    def get_data(self, session=None):
        """
        Generate the base data set for the grid.  This typically will be a
        SQLAlchemy query against the view's model class, but subclasses may
        override this to support arbitrary data sets.

        Note that if your view is typical and uses a SA model, you should not
        override this methid, but override :meth:`query()` instead.
        """
        if session is None:
            session = self.Session()
        return self.query(session)

    def query(self, session):
        """
        Produce the initial/base query for the master grid.  By default this is
        simply a query against the model class, but you may override as
        necessary to apply any sort of pre-filtering etc.  This is useful if
        say, you don't ever want to show records of a certain type to non-admin
        users.  You would modify the base query to hide what you wanted,
        regardless of the user's filter selections.
        """
        model_class = self.get_model_class()
        query = session.query(model_class)

        # only show "local only" objects, unless global access allowed
        if self.secure_global_objects:
            if not self.has_perm('view_global'):
                query = query.filter(model_class.local_only == True)

        return query

    def get_effective_query(self, session=None, **kwargs):
        return self.get_effective_data(session=session, **kwargs)

    def checkbox(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        rendererd for the given row.  Default implementation returns ``True``
        in all cases.
        """
        return True

    def checked(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        checked by default, for the given row.  Default implementation returns
        ``False`` in all cases.
        """
        return False

    def download_results_path(self, user_uuid, filename=None,
                              typ='results', makedirs=False):
        """
        Returns an absolute path for the "results" data file, specific to the
        given user UUID.
        """
        route_prefix = self.get_route_prefix()
        path = os.path.join(self.rattail_config.datadir(), 'downloads',
                            typ, route_prefix,
                            user_uuid[:2], user_uuid[2:])
        if makedirs and not os.path.exists(path):
            os.makedirs(path)

        if filename:
            path = os.path.join(path, filename)
        return path

    def download_results_filename(self, fmt):
        """
        Must return an appropriate "download results" filename for the given
        format.  E.g. ``'products.csv'``
        """
        route_prefix = self.get_route_prefix()
        if fmt == 'csv':
            return '{}.csv'.format(route_prefix)
        if fmt == 'xlsx':
            return '{}.xlsx'.format(route_prefix)

    def download_results_supported_formats(self):
        # TODO: default formats should be configurable?
        return OrderedDict([
            ('xlsx', "Excel (XLSX)"),
            ('csv', "CSV"),
        ])

    def download_results_default_format(self):
        # TODO: default format should be configurable
        return 'xlsx'

    def download_results(self):
        """
        View for saving current (filtered) data results into a file, and
        downloading that file.
        """
        route_prefix = self.get_route_prefix()
        user_uuid = self.request.user.uuid

        # POST means generate a new results file for download
        if self.request.method == 'POST':

            # make sure a valid format was requested
            supported = self.download_results_supported_formats()
            if not supported:
                self.request.session.flash("There are no supported download formats!",
                                           'error')
                return self.redirect(self.get_index_url())
            fmt = self.request.POST.get('fmt')
            if not fmt:
                fmt = self.download_results_default_format() or list(supported)[0]
            if fmt not in supported:
                self.request.session.flash("Unsupported download format: {}".format(fmt),
                                           'error')
                return self.redirect(self.get_index_url())

            # parse field list if one was given
            fields = self.request.POST.get('fields')
            if fields:
                fields = fields.split(',')

            # start thread to actually do work / report progress
            key = '{}.download_results'.format(route_prefix)
            progress = self.make_progress(key)
            results = self.get_effective_data()
            thread = Thread(target=self.download_results_thread,
                            args=(results, fmt, fields, user_uuid, progress))
            thread.start()

            # show user the progress page
            return self.render_progress(progress, {
                'cancel_url': self.get_index_url(),
                'cancel_msg': "Download was canceled.",
            })

        # not POST, so just download a file (if specified)
        filename = self.request.GET.get('filename')
        if not filename:
            return self.redirect(self.get_index_url())
        path = self.download_results_path(user_uuid, filename)
        return self.file_response(path)

    def download_results_thread(self, results, fmt, fields, user_uuid, progress):
        """
        Thread target, which invokes :meth:`download_results_generate()` to
        officially generate the data file which is then to be downloaded.
        """
        route_prefix = self.get_route_prefix()
        session = self.make_isolated_session()
        try:

            # create folder(s) for output; make sure file doesn't exist
            filename = self.download_results_filename(fmt)
            path = self.download_results_path(user_uuid, filename, makedirs=True)
            if os.path.exists(path):
                os.remove(path)

            # generate file for download
            results = results.with_session(session).all()
            self.download_results_setup(fields, progress=progress)
            self.download_results_generate(session, results, path, fmt, fields,
                                           progress=progress)

            session.commit()

        except Exception as error:
            msg = "failed to generate results file for download!"
            log.warning(msg, exc_info=True)
            session.rollback()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {}".format(
                    msg, simple_error(error))
                progress.session.save()
            return

        finally:
            session.close()

        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_index_url()
            progress.session['extra_session_bits'] = {
                '{}.results.generated'.format(route_prefix): path,
            }
            progress.session.save()

    def download_results_setup(self, fields, progress=None):
        """
        Perform any up-front caching or other setup required, just prior to
        generating a new results data file for download.
        """

    def download_results_generate(self, session, results, path, fmt, fields, progress=None):
        """
        This method is responsible for actually generating the data file for a
        "download results" operation, according to the given params.
        """
        if fmt == 'csv':

            if six.PY2:
                csv_file = open(path, 'wb')
                writer = UnicodeDictWriter(csv_file, fields, encoding='utf_8')
            else: # PY3
                csv_file = open(path, 'wt', encoding='utf_8')
                writer = csv.DictWriter(csv_file, fields)
            writer.writeheader()

            def write(obj, i):
                data = self.download_results_normalize(obj, fields, fmt=fmt)
                csvrow = self.download_results_coerce_csv(data, fields)
                writer.writerow(csvrow)

            self.progress_loop(write, results, progress,
                               message="Writing data to CSV file")
            csv_file.close()

        elif fmt == 'xlsx':

            writer = ExcelWriter(path, fields,
                                 sheet_title=self.get_model_title_plural())
            writer.write_header()

            xlrows = []
            def write(obj, i):
                data = self.download_results_normalize(obj, fields, fmt=fmt)
                row = self.download_results_coerce_xlsx(data, fields)
                xlrow = [row[field] for field in fields]
                xlrows.append(xlrow)

            self.progress_loop(write, results, progress,
                               message="Collecting data for Excel")

            def finalize(x, i):
                writer.write_rows(xlrows)
                writer.auto_freeze()
                writer.auto_filter()
                writer.auto_resize()
                writer.save()

            self.progress_loop(finalize, [1], progress,
                               message="Writing Excel file to disk")

    def download_results_fields_available(self, **kwargs):
        """
        Return the list of fields which are *available* to be written to
        download file.  Default field list will be constructed from the
        underlying table columns.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def download_results_fields_default(self, fields, **kwargs):
        """
        Return the default list of fields to be written to download file.
        Unless you override, all "available" fields will be included by
        default.
        """
        return fields

    def download_results_normalize(self, obj, fields, **kwargs):
        """
        Normalize the given object into a data dict, for use when writing to
        the results file for download.
        """
        data = {}
        for field in fields:
            value = getattr(obj, field, None)

            # make timestamps zone-aware
            if isinstance(value, datetime.datetime):
                value = localtime(self.rattail_config, value,
                                  from_utc=not self.has_local_times)

            data[field] = value

        return data

    def download_results_coerce_csv(self, data, fields, **kwargs):
        """
        Coerce the given data dict record, to a "row" dict suitable for use
        when writing directly to CSV file.  Each value in the dict should be a
        string type.
        """
        csvrow = dict(data)
        for field in fields:
            value = csvrow.get(field)

            if value is None:
                value = ''
            else:
                value = six.text_type(value)

            csvrow[field] = value

        return csvrow

    def download_results_coerce_xlsx(self, data, fields, **kwargs):
        """
        Coerce the given data dict record, to a "row" dict suitable for use
        when writing directly to XLSX file.
        """
        data = dict(data)
        for key in data:
            value = data[key]

            # make timestamps local, "zone-naive"
            if isinstance(value, datetime.datetime):
                value = localtime(self.rattail_config, value, tzinfo=False)

            data[key] = value

        return data

    def results_csv(self):
        """
        Download current list results as CSV.
        """
        results = self.get_effective_data()

        # start thread to actually do work / generate progress data
        route_prefix = self.get_route_prefix()
        key = '{}.results_csv'.format(route_prefix)
        progress = self.make_progress(key)
        thread = Thread(target=self.results_csv_thread,
                        args=(results, self.request.user.uuid, progress))
        thread.start()

        # send user to progress page
        return self.render_progress(progress, {
            'cancel_url': self.get_index_url(),
            'cancel_msg': "CSV download was canceled.",
        })

    def results_csv_session(self):
        return self.make_isolated_session()

    def results_csv_thread(self, results, user_uuid, progress):
        """
        Thread target, responsible for actually generating the CSV file which
        is to be presented for download.
        """
        route_prefix = self.get_route_prefix()
        session = self.results_csv_session()
        try:

            # create folder(s) for output; make sure file doesn't exist
            path = os.path.join(self.rattail_config.datadir(), 'downloads',
                                'results-csv', route_prefix,
                                user_uuid[:2], user_uuid[2:])
            if not os.path.exists(path):
                os.makedirs(path)
            path = os.path.join(path, '{}.csv'.format(route_prefix))
            if os.path.exists(path):
                os.remove(path)

            results = results.with_session(session).all()
            fields = self.get_csv_fields()

            if six.PY2:
                csv_file = open(path, 'wb')
                writer = UnicodeDictWriter(csv_file, fields, encoding='utf_8')
            else: # PY3
                csv_file = open(path, 'wt', encoding='utf_8')
                writer = csv.DictWriter(csv_file, fields)

            writer.writeheader()

            def write(obj, i):
                writer.writerow(self.get_csv_row(obj, fields))

            self.progress_loop(write, results, progress,
                               message="Collecting data for CSV")
            csv_file.close()
            session.commit()

        except Exception as error:
            msg = "generating CSV file for download failed!"
            log.warning(msg, exc_info=True)
            session.rollback()
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {}".format(
                    msg, simple_error(error))
                progress.session.save()
            return

        finally:
            session.close()

        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_index_url()
            progress.session['extra_session_bits'] = {
                '{}.results_csv.generated'.format(route_prefix): True,
            }
            progress.session.save()

    def results_csv_download(self):
        route_prefix = self.get_route_prefix()
        user_uuid = self.request.user.uuid
        path = os.path.join(self.rattail_config.datadir(), 'downloads',
                            'results-csv', route_prefix,
                            user_uuid[:2], user_uuid[2:],
                            '{}.csv'.format(route_prefix))
        return self.file_response(path)

    def results_xlsx(self):
        """
        Download current list results as XLSX.
        """
        results = self.get_effective_data()

        # start thread to actually do work / generate progress data
        route_prefix = self.get_route_prefix()
        key = '{}.results_xlsx'.format(route_prefix)
        progress = self.make_progress(key)
        thread = Thread(target=self.results_xlsx_thread,
                        args=(results, self.request.user.uuid, progress))
        thread.start()

        # send user to progress page
        return self.render_progress(progress, {
            'cancel_url': self.get_index_url(),
            'cancel_msg': "XLSX download was canceled.",
        })

    def results_xlsx_session(self):
        return self.make_isolated_session()

    def results_write_xlsx(self, path, fields, results, session, progress=None):
        writer = ExcelWriter(path, fields, sheet_title=self.get_model_title_plural())
        writer.write_header()

        rows = []
        def write(obj, i):
            data = self.get_xlsx_row(obj, fields)
            row = [data[field] for field in fields]
            rows.append(row)

        self.progress_loop(write, results, progress,
                           message="Collecting data for Excel")

        def finalize(x, i):
            writer.write_rows(rows)
            writer.auto_freeze()
            writer.auto_filter()
            writer.auto_resize()
            writer.save()

        self.progress_loop(finalize, [1], progress,
                           message="Writing Excel file to disk")

    def results_xlsx_thread(self, results, user_uuid, progress):
        """
        Thread target, responsible for actually generating the Excel file which
        is to be presented for download.
        """
        route_prefix = self.get_route_prefix()
        session = self.results_xlsx_session()
        try:

            # create folder(s) for output; make sure file doesn't exist
            path = os.path.join(self.rattail_config.datadir(), 'downloads',
                                'results-xlsx', route_prefix,
                                user_uuid[:2], user_uuid[2:])
            if not os.path.exists(path):
                os.makedirs(path)
            path = os.path.join(path, '{}.xlsx'.format(route_prefix))
            if os.path.exists(path):
                os.remove(path)

            results = results.with_session(session).all()
            fields = self.get_xlsx_fields()

            # write output file
            self.results_write_xlsx(path, fields, results, session, progress=progress)

        except Exception as error:
            msg = "generating XLSX file for download failed!"
            log.warning(msg, exc_info=True)
            session.rollback()
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {}".format(
                    msg, simple_error(error))
                progress.session.save()
            return

        session.commit()
        session.close()

        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_index_url()
            progress.session['extra_session_bits'] = {
                '{}.results_xlsx.generated'.format(route_prefix): True,
            }
            progress.session.save()

    def results_xlsx_download(self):
        route_prefix = self.get_route_prefix()
        user_uuid = self.request.user.uuid
        path = os.path.join(self.rattail_config.datadir(), 'downloads',
                            'results-xlsx', route_prefix,
                            user_uuid[:2], user_uuid[2:],
                            '{}.xlsx'.format(route_prefix))
        return self.file_response(path)

    def get_xlsx_fields(self):
        """
        Return the list of fields to be written to XLSX download.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_xlsx_row(self, obj, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        row = {}
        for field in fields:
            row[field] = getattr(obj, field, None)
        return row

    def download_results_rows_supported_formats(self):
        # TODO: default formats should be configurable?
        return OrderedDict([
            ('xlsx', "Excel (XLSX)"),
            ('csv', "CSV"),
        ])

    def download_results_rows_default_format(self):
        # TODO: default format should be configurable
        return 'xlsx'

    def download_results_rows(self):
        """
        View for saving *rows* of current (filtered) data results into a file,
        and downloading that file.
        """
        route_prefix = self.get_route_prefix()
        user_uuid = self.request.user.uuid

        # POST means generate a new results file for download
        if self.request.method == 'POST':

            # make sure a valid format was requested
            supported = self.download_results_rows_supported_formats()
            if not supported:
                self.request.session.flash("There are no supported download formats!",
                                           'error')
                return self.redirect(self.get_index_url())
            fmt = self.request.POST.get('fmt')
            if not fmt:
                fmt = self.download_results_rows_default_format() or list(supported)[0]
            if fmt not in supported:
                self.request.session.flash("Unsupported download format: {}".format(fmt),
                                           'error')
                return self.redirect(self.get_index_url())

            # parse field list if one was given
            fields = self.request.POST.get('fields')
            if fields:
                fields = fields.split(',')
            if not fields:
                if fmt == 'csv':
                    fields = self.get_row_csv_fields()
                elif fmt == 'xlsx':
                    fields = self.get_row_xlsx_fields()
                else:
                    self.request.session.flash("No fields were specified", 'error')
                    return self.redirect(self.get_index_url())

            # start thread to actually do work / report progress
            key = '{}.download_results_rows'.format(route_prefix)
            progress = self.make_progress(key)
            results = self.get_effective_data()
            thread = Thread(target=self.download_results_rows_thread,
                            args=(results, fmt, fields, user_uuid, progress))
            thread.start()

            # show user the progress page
            return self.render_progress(progress, {
                'cancel_url': self.get_index_url(),
                'cancel_msg': "Download was canceled.",
            })

        # not POST, so just download a file (if specified)
        filename = self.request.GET.get('filename')
        if not filename:
            return self.redirect(self.get_index_url())
        path = self.download_results_rows_path(user_uuid, filename)
        return self.file_response(path)

    def download_results_rows_filename(self, fmt):
        """
        Must return an appropriate "download results" filename for the given
        format.  E.g. ``'products.csv'``
        """
        route_prefix = self.get_route_prefix()
        if fmt == 'csv':
            return '{}.rows.csv'.format(route_prefix)
        if fmt == 'xlsx':
            return '{}.rows.xlsx'.format(route_prefix)

    def download_results_rows_path(self, user_uuid, filename=None,
                              typ='results', makedirs=False):
        """
        Returns an absolute path for the "results" data file, specific to the
        given user UUID.
        """
        route_prefix = self.get_route_prefix()
        path = os.path.join(self.rattail_config.datadir(), 'downloads',
                            typ, route_prefix,
                            user_uuid[:2], user_uuid[2:])
        if makedirs and not os.path.exists(path):
            os.makedirs(path)

        if filename:
            path = os.path.join(path, filename)
        return path

    def download_results_rows_fields_available(self, **kwargs):
        """
        Return the list of fields which are *available* to be written to
        download file.  Default field list will be constructed from the
        underlying table columns.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def download_results_rows_fields_default(self, fields, **kwargs):
        """
        Return the default list of fields to be written to download file.
        Unless you override, all "available" fields will be included by
        default.
        """
        return fields

    def download_results_rows_thread(self, results, fmt, fields, user_uuid, progress):
        """
        Thread target, which invokes :meth:`download_results_generate()` to
        officially generate the data file which is then to be downloaded.
        """
        route_prefix = self.get_route_prefix()
        session = self.make_isolated_session()
        try:

            # create folder(s) for output; make sure file doesn't exist
            filename = self.download_results_rows_filename(fmt)
            path = self.download_results_rows_path(user_uuid, filename, makedirs=True)
            if os.path.exists(path):
                os.remove(path)

            # generate file for download
            results = results.with_session(session).all()
            self.download_results_rows_setup(fields, progress=progress)
            self.download_results_rows_generate(session, results, path, fmt, fields,
                                                progress=progress)

            session.commit()

        except Exception as error:
            msg = "failed to generate results file for download!"
            log.warning(msg, exc_info=True)
            session.rollback()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {}".format(
                    msg, simple_error(error))
                progress.session.save()
            return

        finally:
            session.close()

        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_index_url()
            progress.session['extra_session_bits'] = {
                '{}.results_rows.generated'.format(route_prefix): path,
            }
            progress.session.save()

    def download_results_rows_setup(self, fields, progress=None):
        """
        Perform any up-front caching or other setup required, just prior to
        generating a new results data file for download.
        """

    def download_results_rows_generate(self, session, results, path, fmt, fields, progress=None):
        """
        This method is responsible for actually generating the data file for a
        "download rows for results" operation, according to the given params.
        """
        # we really are concerned with "rows of results" here, so let's just
        # replace the 'results' list with a list of rows
        original_results = results
        results = []

        def collect(obj, i):
            results.extend(self.get_row_data(obj).all())

        self.progress_loop(collect, original_results, progress,
                           message="Collecting data for {}".format(self.get_row_model_title_plural()))

        if fmt == 'csv':

            if six.PY2:
                csv_file = open(path, 'wb')
                writer = UnicodeDictWriter(csv_file, fields, encoding='utf_8')
            else: # PY3
                csv_file = open(path, 'wt', encoding='utf_8')
                writer = csv.DictWriter(csv_file, fields)
            writer.writeheader()

            def write(obj, i):
                data = self.download_results_rows_normalize(obj, fields, fmt=fmt)
                csvrow = self.download_results_rows_coerce_csv(data, fields)
                writer.writerow(csvrow)

            self.progress_loop(write, results, progress,
                               message="Writing data to CSV file")
            csv_file.close()

        elif fmt == 'xlsx':

            writer = ExcelWriter(path, fields,
                                 sheet_title=self.get_row_model_title_plural())
            writer.write_header()

            xlrows = []
            def write(obj, i):
                data = self.download_results_rows_normalize(obj, fields, fmt=fmt)
                row = self.download_results_rows_coerce_xlsx(data, fields)
                xlrow = [row[field] for field in fields]
                xlrows.append(xlrow)

            self.progress_loop(write, results, progress,
                               message="Collecting data for Excel")

            def finalize(x, i):
                writer.write_rows(xlrows)
                writer.auto_freeze()
                writer.auto_filter()
                writer.auto_resize()
                writer.save()

            self.progress_loop(finalize, [1], progress,
                               message="Writing Excel file to disk")

    def download_results_rows_normalize(self, row, fields, **kwargs):
        """
        Normalize the given row object into a data dict, for use when writing
        to the results file for download.
        """
        data = {}
        for field in fields:
            value = getattr(row, field, None)

            # make timestamps zone-aware
            if isinstance(value, datetime.datetime):
                value = localtime(self.rattail_config, value,
                                  from_utc=not self.has_local_times)

            data[field] = value

        return data

    def download_results_rows_coerce_csv(self, data, fields, **kwargs):
        """
        Coerce the given data dict record, to a "row" dict suitable for use
        when writing directly to CSV file.  Each value in the dict should be a
        string type.
        """
        csvrow = dict(data)
        for field in fields:
            value = csvrow.get(field)

            if value is None:
                value = ''
            else:
                value = six.text_type(value)

            csvrow[field] = value

        return csvrow

    def download_results_rows_coerce_xlsx(self, data, fields, **kwargs):
        """
        Coerce the given data dict record, to a "row" dict suitable for use
        when writing directly to XLSX file.
        """
        data = dict(data)
        for key in data:
            value = data[key]

            # convert GPC to pretty string
            if isinstance(value, GPC):
                value = value.pretty()

            # make timestamps local, "zone-naive"
            elif isinstance(value, datetime.datetime):
                value = localtime(self.rattail_config, value, tzinfo=False)

            data[key] = value

        return data

    def row_results_xlsx(self):
        """
        Download current *row* results as XLSX.
        """
        obj = self.get_instance()
        results = self.get_effective_row_data(sort=True)
        fields = self.get_row_xlsx_fields()
        path = temp_path(suffix='.xlsx')
        writer = ExcelWriter(path, fields, sheet_title=self.get_row_model_title_plural())
        writer.write_header()

        rows = []
        for row_obj in results:
            data = self.get_row_xlsx_row(row_obj, fields)
            row = [data[field] for field in fields]
            rows.append(row)

        writer.write_rows(rows)
        writer.auto_freeze()
        writer.auto_filter()
        writer.auto_resize()
        writer.save()

        response = self.request.response
        with open(path, 'rb') as f:
            response.body = f.read()
        os.remove(path)

        response.content_length = len(response.body)
        response.content_type = str('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = self.get_row_results_xlsx_filename(obj)
        response.content_disposition = str('attachment; filename={}'.format(filename))
        return response

    def get_row_xlsx_fields(self):
        """
        Return the list of row fields to be written to XLSX download.
        """
        # TODO: should this be shared at all? in a better way?
        return self.get_row_csv_fields()

    def get_row_xlsx_row(self, row, fields):
        """
        Return a dict for use when writing the row's data to XLSX download.
        """
        xlrow = {}
        for field in fields:
            value = getattr(row, field, None)

            if isinstance(value, GPC):
                value = six.text_type(value)

            elif isinstance(value, datetime.datetime):
                # datetime values we provide to Excel must *not* have time zone info,
                # but we should make sure they're in "local" time zone effectively.
                # note however, this assumes a "naive" time value is in UTC zone!
                if value.tzinfo:
                    value = localtime(self.rattail_config, value, tzinfo=False)
                else:
                    value = localtime(self.rattail_config, value, from_utc=True, tzinfo=False)

            xlrow[field] = value
        return xlrow

    def get_row_results_xlsx_filename(self, obj):
        return '{}.xlsx'.format(self.get_row_grid_key())

    def row_results_csv(self):
        """
        Download current row results data for an object, as CSV
        """
        obj = self.get_instance()
        fields = self.get_row_csv_fields()
        data = six.StringIO()
        writer = UnicodeDictWriter(data, fields)
        writer.writeheader()
        for row in self.get_effective_row_data(sort=True):
            writer.writerow(self.get_row_csv_row(row, fields))
        response = self.request.response
        filename = self.get_row_results_csv_filename(obj)
        if six.PY3:
            response.text = data.getvalue()
            response.content_type = 'text/csv'
            response.content_disposition = 'attachment; filename={}'.format(filename)
        else:
            response.body = data.getvalue()
            response.content_type = b'text/csv'
            response.content_disposition = b'attachment; filename={}'.format(filename)
        data.close()
        response.content_length = len(response.body)
        return response

    def get_row_results_csv_filename(self, instance):
        return '{}.csv'.format(self.get_row_grid_key())

    def get_csv_fields(self):
        """
        Return the list of fields to be written to CSV download.  Default field
        list will be constructed from the underlying table columns.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_row_csv_fields(self):
        """
        Return the list of row fields to be written to CSV download.
        """
        fields = []
        mapper = orm.class_mapper(self.model_row_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_csv_row(self, obj, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        csvrow = {}
        for field in fields:
            value = getattr(obj, field, None)
            if isinstance(value, datetime.datetime):
                # TODO: this assumes value is *always* naive UTC
                value = localtime(self.rattail_config, value, from_utc=True)
            csvrow[field] = '' if value is None else six.text_type(value)
        return csvrow

    def get_row_csv_row(self, row, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        csvrow = {}
        for field in fields:
            value = getattr(row, field, None)
            if isinstance(value, datetime.datetime):
                # TODO: this assumes value is *always* naive UTC
                value = localtime(self.rattail_config, value, from_utc=True)
            csvrow[field] = '' if value is None else six.text_type(value)
        return csvrow

    ##############################
    # CRUD Stuff
    ##############################

    def get_instance(self):
        """
        Fetch the current model instance by inspecting the route kwargs and
        doing a database lookup.  If the instance cannot be found, raises 404.
        """
        model_keys = self.get_model_key(as_tuple=True)
        query = self.Session.query(self.get_model_class())

        def filtr(query, model_key):
            key = self.request.matchdict[model_key]
            if self.key_is_integer(model_key):
                key = int(key)
            query = query.filter(getattr(self.model_class, model_key) == key)
            return query

        # filter query by composite key.  we use filter() instead of a simple
        # get() here in case view uses a "pseudo-PK"
        for i, model_key in enumerate(model_keys):
            query = filtr(query, model_key)
        try:
            obj = query.one()
        except orm.exc.NoResultFound:
            raise self.notfound()

        # pretend global object doesn't exist, unless access allowed
        if self.secure_global_objects:
            if not obj.local_only:
                if not self.has_perm('view_global'):
                    raise self.notfound()

        return obj

    def key_is_integer(self, model_key):

        # inspect model class to determine if model_key is numeric
        cls = self.get_model_class(error=False)
        if cls:
            attr = getattr(cls, model_key)
            if isinstance(attr.type, sa.Integer):
                return True

        # do not assume integer by default
        return False

    def get_instance_title(self, instance):
        """
        Return a "pretty" title for the instance, to be used in the page title etc.
        """
        return six.text_type(instance)

    @classmethod
    def get_form_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'form_factory', forms.Form)

    @classmethod
    def get_row_form_factory(cls):
        """
        Returns the factory or class which is to be used when creating new row
        forms.
        """
        return getattr(cls, 'row_form_factory', forms.Form)

    def download_path(self, obj, filename):
        """
        Should return absolute path on disk, for the given object and filename.
        Result will be used to return a file response to client.
        """
        raise NotImplementedError

    def render_downloadable_file(self, obj, field):
        filename = getattr(obj, field)
        if not filename:
            return ""
        path = self.download_path(obj, filename)
        url = self.get_action_url('download', obj, _query={'filename': filename})
        return self.render_file_field(path, url)

    def render_file_field(self, path, url=None, filename=None):
        """
        Convenience for rendering a file with optional download link
        """
        if not filename:
            filename = os.path.basename(path)
        content = "{} ({})".format(filename, self.readable_size(path))
        if url:
            return tags.link_to(content, url)
        return content

    def readable_size(self, path, size=None):
        # TODO: this was shamelessly copied from FormAlchemy ...
        if size is None:
            size = self.get_size(path)
        if size == 0:
            return '0 KB'
        if size <= 1024:
            return '1 KB'
        if size > 1048576:
            return '%0.02f MB' % (size / 1048576.0)
        return '%0.02f KB' % (size / 1024.0)

    def get_size(self, path):
        try:
            return os.path.getsize(path)
        except os.error:
            return 0

    def make_form(self, instance=None, factory=None, fields=None, schema=None, make_kwargs=None, configure=None, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        if factory is None:
            factory = self.get_form_factory()
        if fields is None:
            fields = self.get_form_fields()
        if schema is None:
            schema = self.make_form_schema()
        if make_kwargs is None:
            make_kwargs = self.make_form_kwargs
        if configure is None:
            configure = self.configure_form

        # TODO: SQLAlchemy class instance is assumed *unless* we get a dict
        # (seems like we should be smarter about this somehow)
        # if not self.creating and not isinstance(instance, dict):
        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = make_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        configure(form)
        return form

    def get_form_fields(self):
        if hasattr(self, 'form_fields'):
            return self.form_fields
        # TODO
        # raise NotImplementedError

    def make_form_schema(self):
        if not self.model_class:
            # TODO
            raise NotImplementedError

    def make_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new form instances.
        """
        defaults = {
            'request': self.request,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_class', None),
            'action_url': self.request.current_route_url(_query=None),
            'use_buefy': self.get_use_buefy(),
            'assume_local_times': self.has_local_times,
        }
        if self.creating:
            kwargs.setdefault('cancel_url', self.get_index_url())
        else:
            instance = kwargs['model_instance']
            kwargs.setdefault('cancel_url', self.get_action_url('view', instance))
        defaults.update(kwargs)
        return defaults

    def configure_form(self, form):
        """
        Configure the main "desktop" form for the view's data model.
        """
        self.configure_common_form(form)

        self.configure_field_product_key(form)

    def validate_form(self, form):
        if form.validate(newstyle=True):
            self.form_deserialized = form.validated
            return True
        return False

    def objectify(self, form, data=None):
        """
        Create and/or update the model instance from the given form, and return
        this object.

        .. todo::
           This needs a better explanation.  And probably tests.
        """
        if data is None:
            data = form.validated

        obj = form.schema.objectify(data, context=form.model_instance)

        if self.is_contact:
            obj = self.objectify_contact(obj, data)

        # force "local only" flag unless global access granted
        if self.secure_global_objects:
            if not self.has_perm('view_global'):
                obj.local_only = True

        return obj

    def objectify_contact(self, contact, data):

        if 'default_email' in data:
            address = data['default_email']
            if contact.emails:
                if address:
                    email = contact.emails[0]
                    email.address = address
                else:
                    contact.emails.pop(0)
            elif address:
                contact.add_email_address(address)

        if 'default_phone' in data:
            number = data['default_phone']
            if contact.phones:
                if number:
                    phone = contact.phones[0]
                    phone.number = number
                else:
                    contact.phones.pop(0)
            elif number:
                contact.add_phone_number(number)

        address_fields = ('address_street',
                          'address_street2',
                          'address_city',
                          'address_state',
                          'address_zipcode')

        addr = dict([(field, data[field])
                     for field in address_fields
                     if field in data])

        if any(addr.values()):
            # we strip 'address_' prefix from fields
            addr = dict([(field[8:], value)
                         for field, value in addr.items()])
            if contact.addresses:
                address = contact.addresses[0]
                for field, value in addr.items():
                    setattr(address, field, value)
            else:
                contact.add_mailing_address(**addr)

        elif any([field in data for field in address_fields]) and contact.addresses:
            contact.addresses.pop()

        return contact

    def save_form(self, form):
        form.save()

    def before_create(self, form):
        """
        Event hook, called just after the form to create a new instance has
        been validated, but prior to the form itself being saved.
        """

    def after_create(self, instance):
        """
        Event hook, called just after a new instance is saved.
        """

    def editable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def after_edit(self, instance):
        """
        Event hook, called just after an existing instance is saved.
        """

    def deletable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def before_delete(self, instance):
        """
        Event hook, called just before deletion is attempted.
        """

    def delete_instance(self, instance):
        """
        Delete the instance, or mark it as deleted, or whatever you need to do.
        """
        # note, we don't use self.Session here, in case we're being called from
        # a separate (bulk-delete) thread
        session = orm.object_session(instance)
        session.delete(instance)

        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        session.flush()

    def get_after_delete_url(self, instance):
        """
        Returns the URL to which the user should be redirected after
        successfully "deleting" the given instance.
        """
        if hasattr(self, 'after_delete_url'):
            if callable(self.after_delete_url):
                return self.after_delete_url(instance)
            return self.after_delete_url
        return self.get_index_url()

    ##############################
    # Autocomplete Stuff
    ##############################

    def autocomplete(self):
        """
        View which accepts a single ``term`` param, and returns a list
        of autocomplete results to match.
        """
        app = self.get_rattail_app()
        key = self.get_autocompleter_key()
        # url may include key, for more specific autocompleter
        if 'key' in self.request.matchdict:
            key = '{}.{}'.format(key, self.request.matchdict['key'])
        autocompleter = app.get_autocompleter(key)

        term = self.request.params.get('term', '')
        return autocompleter.autocomplete(self.Session(), term)

    def get_autocompleter_key(self):
        """
        Must return the "key" to be used when locating the
        Autocompleter object, for use with autocomplete view.
        """
        if hasattr(self, 'autocompleter_key'):
            if self.autocompleter_key:
                return self.autocompleter_key
        return self.get_route_prefix()

    ##############################
    # Associated Rows Stuff
    ##############################

    def create_row(self):
        """
        View for creating a new row record.
        """
        self.creating = True
        parent = self.get_instance()
        index_url = self.get_action_url('view', parent)
        form = self.make_row_form(self.model_row_class, cancel_url=index_url)
        if self.request.method == 'POST':
            if self.validate_row_form(form):
                self.before_create_row(form)
                obj = self.save_create_row_form(form)
                self.after_create_row(obj)
                return self.redirect_after_create_row(obj)
        return self.render_to_response('create_row', {
            'index_url': index_url,
            'index_title': '{} {}'.format(
                self.get_model_title(),
                self.get_instance_title(parent)),
            'form': form})

    # TODO: still need to verify this logic
    def save_create_row_form(self, form):
        # self.before_create(form)
        # with self.Session().no_autoflush:
        #     obj = self.objectify(form, self.form_deserialized)
        #     self.before_create_flush(obj, form)
        obj = self.objectify(form, self.form_deserialized)
        self.Session.add(obj)
        self.Session.flush()
        return obj

    # def save_create_row_form(self, form):
    #     self.save_row_form(form)

    def before_create_row(self, form):
        pass

    def after_create_row(self, row_object):
        pass

    def redirect_after_create_row(self, row, **kwargs):
        return self.redirect(self.get_row_action_url('view', row))

    def save_quick_row_form(self, form):
        raise NotImplementedError("You must define `{}:{}.save_quick_row_form()` "
                                  "in order to process quick row forms".format(
                                      self.__class__.__module__,
                                      self.__class__.__name__))

    def redirect_after_quick_row(self, row, **kwargs):
        return self.redirect(self.get_row_action_url('edit', row))

    def view_row(self):
        """
        View for viewing details of a single data row.
        """
        self.viewing = True
        row = self.get_row_instance()
        form = self.make_row_form(row)
        parent = self.get_parent(row)
        return self.render_to_response('view_row', {
            'instance': row,
            'instance_title': self.get_instance_title(parent),
            'row_title': self.get_row_instance_title(row),
            'instance_url': self.get_action_url('view', parent),
            'instance_editable': self.row_editable(row),
            'instance_deletable': self.row_deletable(row),
            'rows_creatable': self.rows_creatable and self.rows_creatable_for(parent),
            'model_title': self.get_row_model_title(),
            'model_title_plural': self.get_row_model_title_plural(),
            'parent_instance': parent,
            'parent_model_title': self.get_model_title(),
            'action_url': self.get_row_action_url,
            'form': form})

    def rows_creatable_for(self, instance):
        """
        Returns boolean indicating whether or not the given instance should
        allow new rows to be added to it.
        """
        return True

    def rows_quickable_for(self, instance):
        """
        Must return boolean indicating whether the "quick row" feature should
        be allowed for the given instance.  Returns ``True`` by default.
        """
        return True

    def row_editable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def edit_row(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        row = self.get_row_instance()
        if not self.row_editable(row):
            raise self.redirect(self.get_row_action_url('view', row))

        form = self.make_row_form(row)

        if self.request.method == 'POST':
            if self.validate_row_form(form):
                self.save_edit_row_form(form)
                return self.redirect_after_edit_row(row)

        parent = self.get_parent(row)
        return self.render_to_response('edit_row', {
            'instance': row,
            'row_parent': parent,
            'parent_model_title': self.get_model_title(),
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent),
            'parent_instance': parent,
            'instance_title': self.get_row_instance_title(row),
            'instance_deletable': self.row_deletable(row),
            'form': form,
            'dform': form.make_deform_form(),
        })

    def save_edit_row_form(self, form):
        obj = self.objectify(form, self.form_deserialized)
        self.after_edit_row(obj)
        self.Session.flush()
        return obj

    # def save_row_form(self, form):
    #     form.save()

    def after_edit_row(self, row):
        """
        Event hook, called just after an existing row object is saved.
        """

    def redirect_after_edit_row(self, row, **kwargs):
        return self.redirect(self.get_row_action_url('view', row))

    def row_deletable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        if not self.rows_deletable:
            return False
        return True

    def delete_row_object(self, row):
        """
        Perform the actual deletion of given row object.
        """
        self.Session.delete(row)

    def delete_row(self):
        """
        Desktop view which can "delete" a sub-row from the parent.
        """
        row = self.get_row_instance()
        if not self.row_deletable(row):
            raise self.redirect(self.get_row_action_url('view', row))

        self.delete_row_object(row)
        return self.redirect(self.get_action_url('view', self.get_parent(row)))

    def get_parent(self, row):
        raise NotImplementedError

    def get_row_instance_title(self, instance):
        return self.get_row_model_title()

    def get_row_instance(self):
        # TODO: is this right..?
        # key = self.request.matchdict[self.get_model_key()]
        key = self.request.matchdict['row_uuid']
        instance = self.Session.query(self.model_row_class).get(key)
        if not instance:
            raise self.notfound()
        return instance

    def make_row_form(self, instance=None, factory=None, fields=None, schema=None, **kwargs):
        """
        Creates a new row form for the given model class/instance.
        """
        if factory is None:
            factory = self.get_row_form_factory()
        if fields is None:
            fields = self.get_row_form_fields()
        if schema is None:
            schema = self.make_row_form_schema()

        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = self.make_row_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_row_form(form)
        return form

    def get_row_form_fields(self):
        if hasattr(self, 'row_form_fields'):
            return self.row_form_fields
        # TODO
        # raise NotImplementedError

    def make_row_form_schema(self):
        if not self.model_row_class:
            # TODO
            raise NotImplementedError

    def make_row_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new row forms.
        """
        defaults = {
            'request': self.request,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_row_class', None),
            'action_url': self.request.current_route_url(_query=None),
            'use_buefy': self.get_use_buefy(),
        }
        if self.creating:
            kwargs.setdefault('cancel_url', self.request.get_referrer())
        else:
            instance = kwargs['model_instance']
            if 'cancel_url' not in kwargs:
                kwargs['cancel_url'] = self.get_row_action_url('view', instance)
        defaults.update(kwargs)
        return defaults

    def configure_row_form(self, form):
        """
        Configure a row form.
        """
        # TODO: is any of this stuff from configure_form() needed?
        # if self.editing:
        #     model_class = self.get_model_class(error=False)
        #     if model_class:
        #         mapper = orm.class_mapper(model_class)
        #         for key in mapper.primary_key:
        #             for field in form.fields:
        #                 if field == key.name:
        #                     form.set_readonly(field)
        #                     break
        # form.remove_field('uuid')

        self.set_row_labels(form)

        self.configure_field_product_key(form)

    def validate_row_form(self, form):
        if form.validate(newstyle=True):
            self.form_deserialized = form.validated
            return True
        return False

    def configure_column_product_key(self, g):
        if '_product_key_' in g.columns:
            key = self.rattail_config.product_key()
            field = self.product_key_fields.get(key, key)
            g.replace('_product_key_', field)
            g.set_label(field, self.rattail_config.product_key_title(key))
            g.set_link(field)
            if key == 'upc':
                g.set_renderer(field, self.render_upc)

    def configure_field_product_key(self, f):
        if '_product_key_' in f:
            key = self.rattail_config.product_key()
            field = self.product_key_fields.get(key, key)
            f.replace('_product_key_', field)
            f.set_label(field, self.rattail_config.product_key_title(key))
            if key == 'upc':
                f.set_renderer(field, self.render_upc)

    def get_row_action_url(self, action, row, **kwargs):
        """
        Generate a URL for the given action on the given row.
        """
        route_name = '{}.{}_row'.format(self.get_route_prefix(), action)
        return self.request.route_url(route_name, **self.get_row_action_route_kwargs(row))

    def get_row_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        # TODO: make this smarter?
        parent = self.get_parent(row)
        return {
            'uuid': parent.uuid,
            'row_uuid': row.uuid,
        }

    def make_diff(self, old_data, new_data, **kwargs):
        return diffs.Diff(old_data, new_data, **kwargs)

    ##############################
    # Configuration Views
    ##############################

    def configure(self):
        """
        Generic view for configuring some aspect of the software.
        """
        if self.request.method == 'POST':
            if self.request.POST.get('remove_settings'):
                self.configure_remove_settings()
                self.request.session.flash("Settings have been removed.")
                return self.redirect(self.request.current_route_url())
            else:
                data = self.request.POST

                # collect any uploaded files
                uploads = {}
                for key, value in six.iteritems(data):
                    if isinstance(value, cgi_FieldStorage):
                        tempdir = tempfile.mkdtemp()
                        filename = os.path.basename(value.filename)
                        filepath = os.path.join(tempdir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(value.file.read())
                        uploads[key] = {
                            'filedir': tempdir,
                            'filename': filename,
                            'filepath': filepath,
                        }

                # process any uploads first
                if uploads:
                    self.configure_process_uploads(uploads, data)

                # then gather/save settings
                settings = self.configure_gather_settings(data)
                self.configure_remove_settings()
                self.configure_save_settings(settings)
                self.request.session.flash("Settings have been saved.")
                return self.redirect(self.request.current_route_url())

        context = self.configure_get_context()
        return self.render_to_response('configure', context)

    def configure_process_uploads(self, uploads, data):
        if self.has_input_file_templates:
            templatesdir = os.path.join(self.rattail_config.datadir(),
                                        'templates', 'input_files',
                                        self.get_route_prefix())

            def get_next_filedir(basedir):
                nextid = 1
                while True:
                    path = os.path.join(basedir, '{:04d}'.format(nextid))
                    if not os.path.exists(path):
                        # this should fail if there happens to be a race
                        # condition and someone else got to this id first
                        os.mkdir(path)
                        return path
                    nextid += 1

            for template in self.normalize_input_file_templates():
                key = '{}.upload'.format(template['setting_file'])
                if key in uploads:
                    assert self.request.POST[template['setting_mode']] == 'hosted'
                    assert not self.request.POST[template['setting_file']]
                    info = uploads[key]
                    basedir = os.path.join(templatesdir, template['key'])
                    if not os.path.exists(basedir):
                        os.makedirs(basedir)
                    filedir = get_next_filedir(basedir)
                    filepath = os.path.join(filedir, info['filename'])
                    shutil.copyfile(info['filepath'], filepath)
                    shutil.rmtree(info['filedir'])
                    numdir = os.path.basename(filedir)
                    data[template['setting_file']] = os.path.join(numdir,
                                                                  info['filename'])

    def configure_get_simple_settings(self):
        """
        If you have some "simple" settings, each of which basically
        just needs to be rendered as a separate field, then you can
        declare them via this method.

        You should return a list of settings; each setting should be
        represented as a dict with various pieces of info, e.g.::

           {
               'section': 'rattail.batch',
               'option': 'purchase.allow_cases',
               'name': 'rattail.batch.purchase.allow_cases',
               'type': bool,
               'value': config.getbool('rattail.batch',
                                       'purchase.allow_cases'),
           }

        Note that some of the above is optional, in particular it
        works like this:

        If you pass ``section`` and ``option`` then you do not need to
        pass ``name`` since that can be deduced.  Also in this case
        you need not pass ``value`` as the normal view logic can fetch
        the value automatically.  Note that when fetching, it honors
        ``type`` which, if you do not specify, would be ``str`` by
        default.

        However if you pass ``name`` then you need not pass
        ``section`` or ``option``, but you must pass ``value`` since
        that cannot be automatically fetched in this case.

        :returns: List of simple setting info dicts, as described
           above.
        """

    def configure_get_name_for_simple_setting(self, simple):
        if 'name' in simple:
            return simple['name']
        return '{}.{}'.format(simple['section'],
                              simple['option'])

    def configure_get_context(self):
        context = {}
        simple_settings = self.configure_get_simple_settings()
        if simple_settings:

            config = self.rattail_config
            settings = {}
            for simple in simple_settings:

                name = self.configure_get_name_for_simple_setting(simple)

                if 'value' in simple:
                    value = simple['value']
                elif simple.get('type') is bool:
                    value = config.getbool(simple['section'],
                                           simple['option'],
                                           default=False)
                else:
                    value = config.get(simple['section'],
                                       simple['option'])

                settings[name] = value

            context['simple_settings'] = settings

        # add settings for downloadable input file templates, if any
        if self.has_input_file_templates:
            settings = {}
            file_options = {}
            file_option_dirs = {}
            for template in self.normalize_input_file_templates(
                    include_file_options=True):
                settings[template['setting_mode']] = template['mode']
                settings[template['setting_file']] = template['file']
                settings[template['setting_url']] = template['url']
                file_options[template['key']] = template['file_options']
                file_option_dirs[template['key']] = template['file_options_dir']
            context['input_file_template_settings'] = settings
            context['input_file_options'] = file_options
            context['input_file_option_dirs'] = file_option_dirs

        return context

    def configure_gather_settings(self, data):
        settings = []

        # maybe collect "simple" settings
        simple_settings = self.configure_get_simple_settings()
        if simple_settings:

            for simple in simple_settings:
                name = self.configure_get_name_for_simple_setting(simple)
                value = data.get(name)

                if simple.get('type') is bool:
                    value = six.text_type(bool(value)).lower()
                elif simple.get('type') is int:
                    value = six.text_type(int(value or '0'))
                else:
                    value = six.text_type(value)

                settings.append({'name': name,
                                 'value': value})

        # maybe also collect input file template settings
        if self.has_input_file_templates:
            for template in self.normalize_input_file_templates():

                # mode
                settings.append({'name': template['setting_mode'],
                                 'value': data.get(template['setting_mode'])})

                # file
                value = data.get(template['setting_file'])
                if value:
                    # nb. avoid saving if empty, so can remain "null"
                    settings.append({'name': template['setting_file'],
                                     'value': value})

                # url
                settings.append({'name': template['setting_url'],
                                 'value': data.get(template['setting_url'])})

        return settings

    def configure_remove_settings(self):
        model = self.model
        names = []

        simple_settings = self.configure_get_simple_settings()
        if simple_settings:
            names.extend([self.configure_get_name_for_simple_setting(simple)
                          for simple in simple_settings])

        if self.has_input_file_templates:
            for template in self.normalize_input_file_templates():
                names.extend([
                    template['setting_mode'],
                    template['setting_file'],
                    template['setting_url'],
                ])

        if names:
            # nb. we do not use self.Session b/c that may not point to
            # the Rattail DB for the subclass
            Session().query(model.Setting)\
                     .filter(model.Setting.name.in_(names))\
                     .delete(synchronize_session=False)

    def configure_save_settings(self, settings):
        model = self.model
        # nb. we do not use self.Session b/c that may not point to the
        # Rattail DB for the subclass
        session = Session()
        for setting in settings:
            session.add(model.Setting(name=setting['name'],
                                      value=setting['value']))

    ##############################
    # Pyramid View Config
    ##############################

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        cls._defaults(config)

    @classmethod
    def get_instance_url_prefix(cls):
        """
        Generate the URL prefix specific to an instance for this model view.
        Winds up looking something like:

        * ``/products/{uuid}``
        * ``/params/{foo}|{bar}|{baz}``
        """
        url_prefix = cls.get_url_prefix()
        model_keys = cls.get_model_key(as_tuple=True)

        prefix = '{}/'.format(url_prefix)
        for i, key in enumerate(model_keys):
            if i:
                prefix += '|'
            prefix += '{{{}}}'.format(key)

        return prefix

    @classmethod
    def _defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        rattail_config = config.registry.settings.get('rattail_config')
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()
        config_title = cls.get_config_title()
        if cls.has_rows:
            row_model_title = cls.get_row_model_title()
            row_model_title_plural = cls.get_row_model_title_plural()

        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        # list/search
        if cls.listable:
            config.add_tailbone_permission(permission_prefix, '{}.list'.format(permission_prefix),
                                           "List / search {}".format(model_title_plural))
            config.add_route(route_prefix, '{}/'.format(url_prefix))
            config.add_view(cls, attr='index', route_name=route_prefix,
                            permission='{}.list'.format(permission_prefix),
                            # hopefully, instruct browser to never cache this page.
                            # on windows/chrome we are seeing some caching when e.g.
                            # user applies some filters, then views a record, then
                            # clicks back button, filters no longer are applied
                            # cf. https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/viewconfig.html#non-predicate-arguments
                            http_cache=0)

            # download results
            # this is the "new" more flexible approach, but we only want to
            # enable it if the class declares it, *and* does *not* declare the
            # older style(s).  that way each class must explicitly choose
            # *only* the new style in order to use it
            if cls.results_downloadable and not (
                    cls.results_downloadable_csv or cls.results_downloadable_xlsx):
                config.add_tailbone_permission(permission_prefix, '{}.download_results'.format(permission_prefix),
                                               "Download search results for {}".format(model_title_plural))
                config.add_route('{}.download_results'.format(route_prefix), '{}/download-results'.format(url_prefix))
                config.add_view(cls, attr='download_results', route_name='{}.download_results'.format(route_prefix),
                                permission='{}.download_results'.format(permission_prefix))

            # download results as CSV (deprecated)
            if cls.results_downloadable_csv:
                config.add_tailbone_permission(permission_prefix, '{}.results_csv'.format(permission_prefix),
                                               "Download {} as CSV".format(model_title_plural))
                config.add_route('{}.results_csv'.format(route_prefix), '{}/csv'.format(url_prefix))
                config.add_view(cls, attr='results_csv', route_name='{}.results_csv'.format(route_prefix),
                                permission='{}.results_csv'.format(permission_prefix))
                config.add_route('{}.results_csv_download'.format(route_prefix), '{}/csv/download'.format(url_prefix))
                config.add_view(cls, attr='results_csv_download', route_name='{}.results_csv_download'.format(route_prefix),
                                permission='{}.results_csv'.format(permission_prefix))

            # download results as XLSX (deprecated)
            if cls.results_downloadable_xlsx:
                config.add_tailbone_permission(permission_prefix, '{}.results_xlsx'.format(permission_prefix),
                                               "Download {} as XLSX".format(model_title_plural))
                config.add_route('{}.results_xlsx'.format(route_prefix), '{}/xlsx'.format(url_prefix))
                config.add_view(cls, attr='results_xlsx', route_name='{}.results_xlsx'.format(route_prefix),
                                permission='{}.results_xlsx'.format(permission_prefix))
                config.add_route('{}.results_xlsx_download'.format(route_prefix), '{}/xlsx/download'.format(url_prefix))
                config.add_view(cls, attr='results_xlsx_download', route_name='{}.results_xlsx_download'.format(route_prefix),
                                permission='{}.results_xlsx'.format(permission_prefix))

            # download rows for results
            if cls.has_rows and cls.results_rows_downloadable:
                config.add_tailbone_permission(permission_prefix, '{}.download_results_rows'.format(permission_prefix),
                                               "Download *rows* for {} search results".format(model_title))
                config.add_route('{}.download_results_rows'.format(route_prefix), '{}/download-rows-for-results'.format(url_prefix))
                config.add_view(cls, attr='download_results_rows', route_name='{}.download_results_rows'.format(route_prefix),
                                permission='{}.download_results_rows'.format(permission_prefix))

        # configure
        if cls.configurable:
            config.add_tailbone_permission(permission_prefix,
                                           '{}.configure'.format(permission_prefix),
                                           label="Configure {}".format(config_title))
            config.add_route('{}.configure'.format(route_prefix),
                             cls.get_config_url())
            config.add_view(cls, attr='configure',
                            route_name='{}.configure'.format(route_prefix),
                            permission='{}.configure'.format(permission_prefix))
            config.add_tailbone_config_page('{}.configure'.format(route_prefix),
                                            config_title)

        # quickie (search)
        if cls.supports_quickie_search:
            config.add_tailbone_permission(permission_prefix, '{}.quickie'.format(permission_prefix),
                                           "Do a \"quickie search\" for {}".format(model_title_plural))
            config.add_route('{}.quickie'.format(route_prefix), '{}/quickie'.format(route_prefix),
                             request_method='GET')
            config.add_view(cls, attr='quickie', route_name='{}.quickie'.format(route_prefix),
                            permission='{}.quickie'.format(permission_prefix))

        # autocomplete
        if cls.supports_autocomplete:

            # default
            config.add_route('{}.autocomplete'.format(route_prefix),
                             '{}/autocomplete'.format(url_prefix))
            config.add_view(cls, attr='autocomplete',
                            route_name='{}.autocomplete'.format(route_prefix),
                            renderer='json',
                            permission='{}.list'.format(permission_prefix))

            # special
            config.add_route('{}.autocomplete_special'.format(route_prefix),
                             '{}/autocomplete/{{key}}'.format(url_prefix))
            config.add_view(cls, attr='autocomplete',
                            route_name='{}.autocomplete_special'.format(route_prefix),
                            renderer='json',
                            permission='{}.list'.format(permission_prefix))

        # create
        if cls.creatable:
            config.add_tailbone_permission(permission_prefix, '{}.create'.format(permission_prefix),
                                           "Create new {}".format(model_title))
            config.add_route('{}.create'.format(route_prefix), '{}/new'.format(url_prefix))
            config.add_view(cls, attr='create', route_name='{}.create'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # populate new object
        if cls.populatable:
            config.add_route('{}.populate'.format(route_prefix), '{}/{{uuid}}/populate'.format(url_prefix))
            config.add_view(cls, attr='populate', route_name='{}.populate'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # enable/disable set
        if cls.supports_set_enabled_toggle:
            config.add_tailbone_permission(permission_prefix, '{}.enable_disable_set'.format(permission_prefix),
                                           "Enable / disable set (selection) of {}".format(model_title_plural))
            config.add_route('{}.enable_set'.format(route_prefix), '{}/enable-set'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='enable_set', route_name='{}.enable_set'.format(route_prefix),
                            permission='{}.enable_disable_set'.format(permission_prefix))
            config.add_route('{}.disable_set'.format(route_prefix), '{}/disable-set'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='disable_set', route_name='{}.disable_set'.format(route_prefix),
                            permission='{}.enable_disable_set'.format(permission_prefix))

        # delete set
        if cls.set_deletable:
            config.add_tailbone_permission(permission_prefix, '{}.delete_set'.format(permission_prefix),
                                           "Delete set (selection) of {}".format(model_title_plural))
            config.add_route('{}.delete_set'.format(route_prefix), '{}/delete-set'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='delete_set', route_name='{}.delete_set'.format(route_prefix),
                            permission='{}.delete_set'.format(permission_prefix))

        # bulk delete
        if cls.bulk_deletable:
            config.add_route('{}.bulk_delete'.format(route_prefix), '{}/bulk-delete'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='bulk_delete', route_name='{}.bulk_delete'.format(route_prefix),
                            permission='{}.bulk_delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.bulk_delete'.format(permission_prefix),
                                           "Bulk delete {}".format(model_title_plural))

        # merge
        if cls.mergeable:
            config.add_route('{}.merge'.format(route_prefix), '{}/merge'.format(url_prefix))
            config.add_view(cls, attr='merge', route_name='{}.merge'.format(route_prefix),
                            permission='{}.merge'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.merge'.format(permission_prefix),
                                           "Merge 2 {}".format(model_title_plural))

        # download input file template
        if cls.has_input_file_templates and cls.creatable:
            config.add_route('{}.download_input_file_template'.format(route_prefix),
                             '{}/download-input-file-template'.format(url_prefix))
            config.add_view(cls, attr='download_input_file_template',
                            route_name='{}.download_input_file_template'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # view
        if cls.viewable:
            config.add_tailbone_permission(permission_prefix, '{}.view'.format(permission_prefix),
                                           "View details for {}".format(model_title))
            if cls.has_pk_fields:
                config.add_tailbone_permission(permission_prefix, '{}.view_pk_fields'.format(permission_prefix),
                                               "View all PK-type fields for {}".format(model_title_plural))
            if cls.secure_global_objects:
                config.add_tailbone_permission(permission_prefix, '{}.view_global'.format(permission_prefix),
                                               "View *global* {}".format(model_title_plural))

            # view by grid index
            config.add_route('{}.view_index'.format(route_prefix), '{}/view'.format(url_prefix))
            config.add_view(cls, attr='view_index', route_name='{}.view_index'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

            # view by record key
            config.add_route('{}.view'.format(route_prefix), instance_url_prefix)
            config.add_view(cls, attr='view', route_name='{}.view'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

            # version history
            if cls.has_versions and rattail_config and rattail_config.versioning_enabled():
                config.add_tailbone_permission(permission_prefix, '{}.versions'.format(permission_prefix),
                                               "View version history for {}".format(model_title))
                config.add_route('{}.versions'.format(route_prefix), '{}/versions/'.format(instance_url_prefix))
                config.add_view(cls, attr='versions', route_name='{}.versions'.format(route_prefix),
                                permission='{}.versions'.format(permission_prefix))
                config.add_route('{}.version'.format(route_prefix), '{}/versions/{{txnid}}'.format(instance_url_prefix))
                config.add_view(cls, attr='view_version', route_name='{}.version'.format(route_prefix),
                                permission='{}.versions'.format(permission_prefix))

        # image
        if cls.has_image:
            config.add_route('{}.image'.format(route_prefix), '{}/image'.format(instance_url_prefix))
            config.add_view(cls, attr='image', route_name='{}.image'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

        # thumbnail
        if cls.has_thumbnail:
            config.add_route('{}.thumbnail'.format(route_prefix), '{}/thumbnail'.format(instance_url_prefix))
            config.add_view(cls, attr='thumbnail', route_name='{}.thumbnail'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

        # clone
        if cls.cloneable:
            config.add_tailbone_permission(permission_prefix, '{}.clone'.format(permission_prefix),
                                           "Clone an existing {0} as a new {0}".format(model_title))
            config.add_route('{}.clone'.format(route_prefix), '{}/clone'.format(instance_url_prefix))
            config.add_view(cls, attr='clone', route_name='{}.clone'.format(route_prefix),
                            permission='{}.clone'.format(permission_prefix))

        # touch
        if cls.touchable:
            config.add_tailbone_permission(permission_prefix, '{}.touch'.format(permission_prefix),
                                           "\"Touch\" a {} to trigger datasync for it".format(model_title))
            config.add_route('{}.touch'.format(route_prefix), '{}/touch'.format(instance_url_prefix))
            config.add_view(cls, attr='touch', route_name='{}.touch'.format(route_prefix),
                            permission='{}.touch'.format(permission_prefix))

        # download
        if cls.downloadable:
            config.add_route('{}.download'.format(route_prefix), '{}/download'.format(instance_url_prefix))
            config.add_view(cls, attr='download', route_name='{}.download'.format(route_prefix),
                            permission='{}.download'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.download'.format(permission_prefix),
                                           "Download associated data for {}".format(model_title))

        # edit
        if cls.editable:
            config.add_tailbone_permission(permission_prefix, '{}.edit'.format(permission_prefix),
                                           "Edit {}".format(model_title))
            config.add_route('{}.edit'.format(route_prefix), '{}/edit'.format(instance_url_prefix))
            config.add_view(cls, attr='edit', route_name='{}.edit'.format(route_prefix),
                            permission='{}.edit'.format(permission_prefix))

        # execute
        if cls.executable:
            config.add_tailbone_permission(permission_prefix, '{}.execute'.format(permission_prefix),
                                           "Execute {}".format(model_title))
            config.add_route('{}.execute'.format(route_prefix),
                             '{}/execute'.format(instance_url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='execute', route_name='{}.execute'.format(route_prefix),
                            permission='{}.execute'.format(permission_prefix))

        # delete
        if cls.deletable:
            config.add_route('{0}.delete'.format(route_prefix), '{}/delete'.format(instance_url_prefix))
            config.add_view(cls, attr='delete', route_name='{0}.delete'.format(route_prefix),
                            permission='{0}.delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.delete'.format(permission_prefix),
                                           "Delete {0}".format(model_title))

        # import batch from file
        if cls.supports_import_batch_from_file:
            config.add_tailbone_permission(permission_prefix, '{}.import_file'.format(permission_prefix),
                                           "Create a new import batch from data file")

        ### sub-rows stuff follows

        # download row results as CSV
        if cls.has_rows and cls.rows_downloadable_csv:
            config.add_tailbone_permission(permission_prefix, '{}.row_results_csv'.format(permission_prefix),
                                           "Download {} results as CSV".format(row_model_title))
            config.add_route('{}.row_results_csv'.format(route_prefix), '{}/{{uuid}}/rows-csv'.format(url_prefix))
            config.add_view(cls, attr='row_results_csv', route_name='{}.row_results_csv'.format(route_prefix),
                            permission='{}.row_results_csv'.format(permission_prefix))

        # download row results as Excel
        if cls.has_rows and cls.rows_downloadable_xlsx:
            config.add_tailbone_permission(permission_prefix, '{}.row_results_xlsx'.format(permission_prefix),
                                           "Download {} results as XLSX".format(row_model_title))
            config.add_route('{}.row_results_xlsx'.format(route_prefix), '{}/rows-xlsx'.format(instance_url_prefix))
            config.add_view(cls, attr='row_results_xlsx', route_name='{}.row_results_xlsx'.format(route_prefix),
                            permission='{}.row_results_xlsx'.format(permission_prefix))

        # create row
        if cls.has_rows:
            if cls.rows_creatable:
                config.add_tailbone_permission(permission_prefix, '{}.create_row'.format(permission_prefix),
                                               "Create new {} rows".format(model_title))
                config.add_route('{}.create_row'.format(route_prefix), '{}/new-row'.format(instance_url_prefix))
                config.add_view(cls, attr='create_row', route_name='{}.create_row'.format(route_prefix),
                                permission='{}.create_row'.format(permission_prefix))

        # view row
        if cls.has_rows:
            if cls.rows_viewable:
                config.add_route('{}.view_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}'.format(url_prefix))
                config.add_view(cls, attr='view_row', route_name='{}.view_row'.format(route_prefix),
                                permission='{}.view'.format(permission_prefix))

        # edit row
        if cls.has_rows:
            if cls.rows_editable or cls.rows_editable_but_not_directly:
                config.add_tailbone_permission(permission_prefix, '{}.edit_row'.format(permission_prefix),
                                               "Edit individual {}".format(row_model_title_plural))
            if cls.rows_editable:
                config.add_route('{}.edit_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}/edit'.format(url_prefix))
                config.add_view(cls, attr='edit_row', route_name='{}.edit_row'.format(route_prefix),
                                permission='{}.edit_row'.format(permission_prefix))

        # delete row
        if cls.has_rows:
            if cls.rows_deletable:
                config.add_tailbone_permission(permission_prefix, '{}.delete_row'.format(permission_prefix),
                                               "Delete individual {}".format(row_model_title_plural))
                config.add_route('{}.delete_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}/delete'.format(url_prefix))
                config.add_view(cls, attr='delete_row', route_name='{}.delete_row'.format(route_prefix),
                                permission='{}.delete_row'.format(permission_prefix))
