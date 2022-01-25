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
View for running arbitrary import/export jobs
"""

from __future__ import unicode_literals, absolute_import

import getpass
import socket
import sys
import logging
import subprocess
import time

import json
import six
import sqlalchemy as sa

from rattail.exceptions import ConfigurationError
from rattail.threads import Thread

import colander
import markdown
from deform import widget as dfwidget
from webhelpers2.html import HTML

from tailbone.views import MasterView


log = logging.getLogger(__name__)


class ImportingView(MasterView):
    """
    View for running arbitrary import/export jobs
    """
    normalized_model_name = 'importhandler'
    model_title = "Import / Export Handler"
    model_key = 'key'
    route_prefix = 'importing'
    url_prefix = '/importing'
    index_title = "Importing / Exporting"
    creatable = False
    editable = False
    deletable = False
    filterable = False
    pageable = False

    configurable = True
    config_title = "Import / Export"

    labels = {
        'host_title': "Data Source",
        'local_title': "Data Target",
        'direction_display': "Direction",
    }

    grid_columns = [
        'host_title',
        'local_title',
        'direction_display',
        'handler_spec',
    ]

    form_fields = [
        'key',
        'local_key',
        'host_key',
        'handler_spec',
        'host_title',
        'local_title',
        'direction_display',
        'models',
    ]

    runjob_form_fields = [
        'handler_spec',
        'host_title',
        'local_title',
        'models',
        'create',
        'update',
        'delete',
        # 'runas',
        'versioning',
        'dry_run',
        'warnings',
    ]

    def get_data(self, session=None):
        app = self.get_rattail_app()
        data = []

        for handler in app.get_designated_import_handlers(
                ignore_errors=True, sort=True):
            data.append(self.normalize(handler))

        return data

    def normalize(self, handler, keep_handler=True):
        data = {
            'key': handler.get_key(),
            'generic_title': handler.get_generic_title(),
            'host_key': handler.host_key,
            'host_title': handler.get_generic_host_title(),
            'local_key': handler.local_key,
            'local_title': handler.get_generic_local_title(),
            'handler_spec': handler.get_spec(),
            'direction': handler.direction,
            'direction_display': handler.direction.capitalize(),
            'safe_for_web_app': handler.safe_for_web_app,
        }

        if keep_handler:
            data['_handler'] = handler

        alternates = getattr(handler, 'alternate_handlers', None)
        if alternates:
            data['alternates'] = []
            for alternate in alternates:
                data['alternates'].append(self.normalize(
                    alternate, keep_handler=keep_handler))

        cmd = self.get_cmd_for_handler(handler, ignore_errors=True)
        if cmd:
            data['cmd'] = ' '.join(cmd)
            data['command'] = cmd[0]
            data['subcommand'] = cmd[1]

        runas = self.get_runas_for_handler(handler)
        if runas:
            data['default_runas'] = runas

        return data

    def configure_grid(self, g):
        super(ImportingView, self).configure_grid(g)

        g.set_link('host_title')
        g.set_link('local_title')

    def get_instance(self):
        """
        Fetch the current model instance by inspecting the route kwargs and
        doing a database lookup.  If the instance cannot be found, raises 404.
        """
        key = self.request.matchdict['key']
        app = self.get_rattail_app()
        handler = app.get_import_handler(key, ignore_errors=True)
        if handler:
            return self.normalize(handler)
        raise self.notfound()

    def get_instance_title(self, handler_info):
        handler = handler_info['_handler']
        return handler.get_generic_title()

    def make_form_schema(self):
        return ImportHandlerSchema()

    def make_form_kwargs(self, **kwargs):
        kwargs = super(ImportingView, self).make_form_kwargs(**kwargs)

        # nb. this is set as sort of a hack, to prevent SA model
        # inspection logic
        kwargs['renderers'] = {}

        return kwargs

    def configure_form(self, f):
        super(ImportingView, self).configure_form(f)

        f.set_renderer('models', self.render_models)

    def render_models(self, handler, field):
        handler = handler['_handler']
        items = []
        for key in handler.get_importer_keys():
            items.append(HTML.tag('li', c=[key]))
        return HTML.tag('ul', c=items)

    def template_kwargs_view(self, **kwargs):
        kwargs = super(ImportingView, self).template_kwargs_view(**kwargs)
        handler_info = kwargs['instance']
        kwargs['handler'] = handler_info['_handler']
        return kwargs

    def runjob(self):
        """
        View for running an import / export job
        """
        handler_info = self.get_instance()
        handler = handler_info['_handler']
        form = self.make_runjob_form(handler_info)

        if self.request.method == 'POST':
            if self.validate_form(form):

                self.cache_runjob_form_values(handler, form)

                try:
                    return self.do_runjob(handler_info, form)
                except Exception as error:
                    self.request.session.flash(six.text_type(error), 'error')
                    return self.redirect(self.request.current_route_url())

        return self.render_to_response('runjob', {
            'handler_info': handler_info,
            'handler': handler,
            'form': form,
        })

    def cache_runjob_form_values(self, handler, form):
        handler_key = handler.get_key()

        def make_key(field):
            return 'rattail.importing.{}.{}'.format(handler_key, field)

        for field in form.fields:
            key = make_key(field)
            self.request.session[key] = form.validated[field]

    def read_cached_runjob_values(self, handler, form):
        handler_key = handler.get_key()

        def make_key(field):
            return 'rattail.importing.{}.{}'.format(handler_key, field)

        for field in form.fields:
            key = make_key(field)
            if key in self.request.session:
                form.set_default(field, self.request.session[key])

    def make_runjob_form(self, handler_info, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        handler = handler_info['_handler']
        factory = self.get_form_factory()
        fields = list(self.runjob_form_fields)
        schema = RunJobSchema()

        kwargs = self.make_runjob_form_kwargs(handler_info, **kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_runjob_form(handler, form)

        self.read_cached_runjob_values(handler, form)

        return form

    def make_runjob_form_kwargs(self, handler_info, **kwargs):
        route_prefix = self.get_route_prefix()
        handler = handler_info['_handler']
        defaults = {
            'request': self.request,
            'use_buefy': self.get_use_buefy(),
            'model_instance': handler,
            'cancel_url': self.request.route_url('{}.view'.format(route_prefix),
                                                 key=handler.get_key()),
            # nb. these next 2 are set as sort of a hack, to prevent
            # SA model inspection logic
            'renderers': {},
            'appstruct': handler_info,
        }
        defaults.update(kwargs)
        return defaults

    def configure_runjob_form(self, handler, f):
        self.set_labels(f)

        f.set_readonly('handler_spec')
        f.set_renderer('handler_spec', lambda handler, field: handler.get_spec())

        f.set_readonly('host_title')
        f.set_readonly('local_title')

        keys = handler.get_importer_keys()
        f.set_widget('models', dfwidget.SelectWidget(values=[(k, k) for k in keys],
                                                     multiple=True,
                                                     size=len(keys)))
        # f.set_default('models', keys)

        f.set_default('create', True)
        f.set_default('update', True)
        f.set_default('delete', False)
        # f.set_default('runas', self.rattail_config.get('rattail', 'runas.default') or '')
        f.set_default('versioning', True)
        f.set_default('dry_run', False)
        f.set_default('warnings', False)

    def do_runjob(self, handler_info, form):
        handler = handler_info['_handler']
        handler_key = handler.get_key()

        if self.request.POST.get('runjob') == 'true':

            # will invoke handler to run job..

            # ..but only if it is safe to do so
            if not handler.safe_for_web_app:
                self.request.session.flash("Handler is not (yet) safe to run "
                                           "with this tool", 'error')
                return self.redirect(self.request.current_route_url())

            # TODO: this socket progress business was lifted from
            # tailbone.views.batch.core:BatchMasterView.handler_action
            # should probably refactor to share somehow

            # make progress object
            key = 'rattail.importing.{}'.format(handler_key)
            progress = self.make_progress(key)

            # make socket for progress thread to listen to action thread
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', 0))
            sock.listen(1)
            port = sock.getsockname()[1]

            # launch thread to monitor progress
            success_url = self.request.current_route_url()
            thread = Thread(target=self.progress_thread, 
                            args=(sock, success_url, progress))
            thread.start()

            true_cmd = self.make_runjob_cmd(handler, form, 'true', port=port)

            # launch thread to invoke handler
            thread = Thread(target=self.do_runjob_thread,
                            args=(handler, true_cmd, port, progress))
            thread.start()

            return self.render_progress(progress, {
                'can_cancel': False,
                'cancel_url': self.request.current_route_url(),
            })

        else: # explain only
            notes_cmd = self.make_runjob_cmd(handler, form, 'notes')
            self.cache_runjob_notes(handler, notes_cmd)

        return self.redirect(self.request.current_route_url())

    def do_runjob_thread(self, handler, cmd, port, progress):

        # invoke handler command via subprocess
        try:
            result = subprocess.run(cmd, check=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            output = result.stdout.decode('utf_8').strip()

        except Exception as error:
            log.warning("failed to invoke handler cmd: %s", cmd, exc_info=True)
            if progress:
                progress.session.load()
                progress.session['error'] = True
                msg = """\
{} failed!  Here is the command I tried to run:

```
{}
```

And here is the output:

```
{}
```
""".format(handler.direction.capitalize(),
           ' '.join(cmd),
           error.stdout.decode('utf_8').strip())
                msg = markdown.markdown(msg, extensions=['fenced_code'])
                msg = HTML.literal(msg)
                msg = HTML.tag('div', class_='tailbone-markdown', c=[msg])
                progress.session['error_msg'] = msg
                progress.session.save()

        else: # success

            if progress:
                progress.session.load()
                msg = self.get_runjob_success_msg(handler, output)
                progress.session['complete'] = True
                progress.session['success_url'] = self.request.current_route_url()
                progress.session['success_msg'] = msg
                progress.session.save()

            suffix = "\n\n.".encode('utf_8')
            cxn = socket.create_connection(('127.0.0.1', port))
            data = json.dumps({
                'everything_complete': True,
            })
            if six.PY3:
                data = data.encode('utf_8')
            cxn.send(data)
            cxn.send(suffix)
            cxn.close()

    def get_runjob_success_msg(self, handler, output):
        notes = """\
{} went okay, here is the output:

```
{}
```
""".format(handler.direction.capitalize(), output)

        notes = markdown.markdown(notes, extensions=['fenced_code'])
        notes = HTML.literal(notes)
        return HTML.tag('div', class_='tailbone-markdown', c=[notes])

    def get_cmd_for_handler(self, handler, ignore_errors=False):
        handler_key = handler.get_key()

        cmd = self.rattail_config.getlist('rattail.importing',
                                          '{}.cmd'.format(handler_key))
        if not cmd or len(cmd) != 2:
            cmd = self.rattail_config.getlist('rattail.importing',
                                              '{}.default_cmd'.format(handler_key))

            if not cmd or len(cmd) != 2:
                msg = ("Missing or invalid config; please set '{}.default_cmd' in the "
                       "[rattail.importing] section of your config file".format(handler_key))
                if ignore_errors:
                    return
                raise ConfigurationError(msg)

        return cmd

    def get_runas_for_handler(self, handler):
        handler_key = handler.get_key()
        runas = self.rattail_config.get('rattail.importing',
                                        '{}.runas'.format(handler_key))
        if runas:
            return runas
        return self.rattail_config.get('rattail', 'runas.default')

    def make_runjob_cmd(self, handler, form, typ, port=None):
        command, subcommand = self.get_cmd_for_handler(handler)
        runas = self.get_runas_for_handler(handler)
        data = form.validated

        if typ == 'true':
            cmd = [
                '{}/bin/{}'.format(sys.prefix, command),
                '--config={}/app/quiet.conf'.format(sys.prefix),
                '--progress',
                '--progress-socket=127.0.0.1:{}'.format(port),
            ]
        else:
            cmd = [
                'sudo', '-u', getpass.getuser(),
                'bin/{}'.format(command),
                '-c', 'app/quiet.conf',
                '-P',
            ]

        if runas:
            if typ == 'true':
                cmd.append('--runas={}'.format(runas))
            else:
                cmd.extend(['--runas', runas])

        cmd.append(subcommand)

        cmd.extend(data['models'])

        if data['create']:
            if typ == 'true':
                cmd.append('--create')
        else:
            cmd.append('--no-create')

        if data['update']:
            if typ == 'true':
                cmd.append('--update')
        else:
            cmd.append('--no-update')

        if data['delete']:
            cmd.append('--delete')
        else:
            if typ == 'true':
                cmd.append('--no-delete')

        if data['versioning']:
            if typ == 'true':
                cmd.append('--versioning')
        else:
            cmd.append('--no-versioning')

        if data['dry_run']:
            cmd.append('--dry-run')

        if data['warnings']:
            if typ == 'true':
                cmd.append('--warnings')
            else:
                cmd.append('-W')

        return cmd

    def cache_runjob_notes(self, handler, notes_cmd):
        notes = """\
You can run this {direction} job manually via command line:

```sh
cd {prefix}
{cmd}
```
""".format(direction=handler.direction,
           prefix=sys.prefix,
           cmd=' '.join(notes_cmd))

        self.request.session['rattail.importing.runjob.notes'] = markdown.markdown(
            notes, extensions=['fenced_code', 'codehilite'])

    def configure_get_context(self):
        app = self.get_rattail_app()
        handlers_data = []

        for handler in app.get_designated_import_handlers(
                with_alternates=True,
                ignore_errors=True, sort=True):

            data = self.normalize(handler, keep_handler=False)

            data['spec_options'] = [handler.get_spec()]
            for alternate in handler.alternate_handlers:
                data['spec_options'].append(alternate.get_spec())
            data['spec_options'].sort()

            handlers_data.append(data)

        return {
            'handlers_data': handlers_data,
        }

    def configure_gather_settings(self, data):
        settings = []

        for handler in json.loads(data['handlers']):
            key = handler['key']

            settings.extend([
                {'name': 'rattail.importing.{}.handler'.format(key),
                 'value': handler['handler_spec']},
                {'name': 'rattail.importing.{}.cmd'.format(key),
                 'value': '{} {}'.format(handler['command'],
                                         handler['subcommand'])},
                {'name': 'rattail.importing.{}.runas'.format(key),
                 'value': handler['default_runas']},
            ])

        return settings

    def configure_remove_settings(self):
        model = self.model
        self.Session.query(model.Setting)\
                    .filter(sa.or_(
                        model.Setting.name.like('rattail.importing.%.handler'),
                        model.Setting.name.like('rattail.importing.%.cmd'),
                        model.Setting.name.like('rattail.importing.%.runas')))\
                    .delete(synchronize_session=False)

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._importing_defaults(config)

    @classmethod
    def _importing_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()

        # run job
        config.add_tailbone_permission(permission_prefix,
                                       '{}.runjob'.format(permission_prefix),
                                       "Run an arbitrary Import / Export Job")
        config.add_route('{}.runjob'.format(route_prefix),
                         '{}/runjob'.format(instance_url_prefix))
        config.add_view(cls, attr='runjob', 
                        route_name='{}.runjob'.format(route_prefix),
                        permission='{}.runjob'.format(permission_prefix))


class ImportHandlerSchema(colander.MappingSchema):

    host_key = colander.SchemaNode(colander.String())

    local_key = colander.SchemaNode(colander.String())

    host_title = colander.SchemaNode(colander.String())

    local_title = colander.SchemaNode(colander.String())

    handler_spec = colander.SchemaNode(colander.String())


class RunJobSchema(colander.MappingSchema):

    handler_spec = colander.SchemaNode(colander.String())
    
    host_title = colander.SchemaNode(colander.String())

    local_title = colander.SchemaNode(colander.String())

    models = colander.SchemaNode(colander.List())

    create = colander.SchemaNode(colander.Bool())

    update = colander.SchemaNode(colander.Bool())

    delete = colander.SchemaNode(colander.Bool())

    # runas = colander.SchemaNode(colander.String())

    versioning = colander.SchemaNode(colander.Bool())

    dry_run = colander.SchemaNode(colander.Bool())

    warnings = colander.SchemaNode(colander.Bool())


def includeme(config):
    ImportingView.defaults(config)
