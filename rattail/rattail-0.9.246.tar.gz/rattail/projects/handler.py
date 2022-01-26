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
Handler for Generating Projects
"""

from __future__ import unicode_literals, absolute_import

import os
import random
import shutil
import string
import subprocess
import sys

from mako.template import Template


class ProjectHandler(object):
    """
    Base class for project handlers.
    """

    def __init__(self, config):
        self.config = config

    def get_storage_dir(self):
        """
        Returns the path to root storage (output) dir for all generated
        projects.
        """
        path = self.config.get('rattail', 'generated_projects.storage_dir')
        if path:
            return path
        return os.path.join(self.config.workdir(require=True),
                            'generated-projects')

    def get_project_dir(self, slug):
        """
        Returns the storage/output path for generated project with the given
        slug name.
        """
        return os.path.join(self.get_storage_dir(), slug)

    def generate_project(self, project_type, slug, options, path=None):
        """
        Generate source code for a new project.

        Note that this method is *not* meant to be overridden by custom
        handlers.  It sticks to the housekeeping chores, and all "interesting"
        logic should be found in :meth:`do_generate()` - which you're free to
        override.

        :param slug: Canonical "slug" (machine-friendly name) for the project.

        :param options: Dictionary(-like) object which contains whatever
           "options" should direct the code generator logic.

        :param path: Path to folder in which project source code should be
           generated.  It will be created if it doesn't exist.  If not
           specified, will use the path returned by :meth:`get_project_dir()`.
        """
        if not path:
            path = self.get_project_dir(slug)

        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

        # TODO: all of this logic really belongs elsewhere...
        if project_type in ('rattail', 'fabric'):

            if 'egg_name' not in options:
                options['egg_name'] = options['python_project_name'].replace('-', '_')

            if 'studly_name' not in options:
                words = options['name'].split('-')
                options['studly_name'] = ''.join([word.capitalize()
                                                  for word in words])

            if 'env_name' not in options:
                options['env_name'] = slug

        if project_type == 'rattail':

            if 'db_name' not in options:
                options['db_name'] = slug

            if 'runas_username' not in options:
                options['runas_username'] = slug

            if 'alembic_script_location' not in options:
                if options['extends_db']:
                    location = '{}.db:alembic'.format(options['python_name'])
                else:
                    location = 'rattail.db:alembic'
                options['alembic_script_location'] = location

            if 'alembic_version_locations' not in options:
                locations = ['rattail.db:alembic/versions']
                if options['integrates_catapult']:
                    locations.append('rattail_onager.db:alembic/versions')
                if options['extends_db']:
                    locations.append('{}.db:alembic/versions'.format(options['python_name']))
                options['alembic_version_locations'] = ' '.join(reversed(locations))

            if 'beaker_session_secret' not in options:
                options['beaker_session_secret'] = self.random_string()

        self.do_generate(project_type, slug, options, path)
        return path

    def random_string(self, size=20, chars=string.ascii_letters + string.digits):
        # per https://stackoverflow.com/a/2257449
        return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

    def do_generate(self, project_type, slug, options, path):
        """
        This method supplies the "true" logic for generating new project code.
        Custom handlers may need to override it.  Arguments are essentially the
        same as for :meth:`generate_project()`; however note that the ``path``
        will already exist when this method is invoked.

        Default logic for this method simply runs the ``pcreate`` command with
        the 'rattail' scaffold.  But that is quite limiting, i.e. the only
        "option" it accepts is the project name.  (Hopefully improved logic is
        coming soon though..!)
        """
        pcreate = os.path.join(os.path.dirname(sys.executable), 'pcreate')
        current = os.getcwd()
        os.chdir(path)
        try:
            subprocess.check_call([pcreate, '-s', 'rattail', options['name']])
        finally:
            os.chdir(current)

    def resolve(self, path):
        """
        Returns an absolute path, based on the given path.  So, if that's
        already an absolute path, it's returned as-is; however if not then the
        path is assumed to be relative to this python module.
        """
        abspath = os.path.abspath(path)
        if abspath == path:
            return path
        return os.path.join(os.path.dirname(__file__), path)

    def generate(self, template, output, **context):
        """
        Generate a file from the given template, and save the result to the
        given output path.
        """
        # maybe run it through our simplistic, hand-rolled template engine
        # (note, this is only for the sake of *avoiding* mako logic, when
        # generating "actual" mako templates, so we avoid a mako-within-mako
        # situation.)
        if template.endswith('.mako_tmpl'):
            return self.generate_mako_tmpl(template, output, **context)

        # maybe run it through Mako template engine
        if template.endswith('.mako'):
            return self.generate_mako(template, output, **context)

        # or, just copy the file as-is
        template = self.resolve(template)
        shutil.copyfile(template, output)

    def generate_mako(self, template, output, **context):
        """
        Generate a file from the given template, and save the result to the
        given output path.
        """
        template = self.resolve(template)
        template = Template(filename=template)
        text = template.render(**context)
        with open(output, 'wt') as f:
            f.write(text)

    def generate_mako_tmpl(self, template, output, **context):
        """
        Generate a file from the given template, and save the result to the
        given output path.
        """
        template = os.path.join(os.path.dirname(__file__), template)
        with open(template, 'rt') as f:
            template_lines = f.readlines()

        output_lines = []
        for line in template_lines:
            line = line.rstrip('\n')
            line = line % context
            output_lines.append(line)

        with open(output, 'wt') as f:
            f.write('\n'.join(output_lines))


class RattailProjectHandler(ProjectHandler):
    """
    Project handler for Rattail
    """

    def do_generate(self, project_type, slug, options, path):
        """
        And here we do some experimentation...
        """
        if project_type == 'byjove':
            return self.generate_byjove_project(slug, options, path)
        elif project_type == 'fabric':
            return self.generate_fabric_project(slug, options, path)
        else:
            return self.generate_rattail_project(slug, options, path)

    def generate_rattail_project(self, slug, options, path):
        """
        And here we do some experimentation...
        """
        context = options

        ##############################
        # root project dir
        ##############################

        self.generate('rattail/gitignore.mako', os.path.join(path, '.gitignore'),
                      **context)

        self.generate('rattail/MANIFEST.in.mako', os.path.join(path, 'MANIFEST.in'),
                      **context)

        self.generate('rattail/README.md.mako', os.path.join(path, 'README.md'),
                      **context)

        self.generate('rattail/setup.py.mako', os.path.join(path, 'setup.py'),
                      **context)

        self.generate('rattail/tasks.py.mako', os.path.join(path, 'tasks.py'),
                      **context)

        ##############################
        # root package dir
        ##############################

        package = os.path.join(path, options['python_name'])
        os.makedirs(package)

        self.generate('rattail/package/__init__.py.mako', os.path.join(package, '__init__.py'),
                      **context)

        self.generate('rattail/package/_version.py', os.path.join(package, '_version.py'))

        self.generate('rattail/package/config.py.mako', os.path.join(package, 'config.py'),
                      **context)

        self.generate('rattail/package/commands.py.mako', os.path.join(package, 'commands.py'),
                      **context)

        self.generate('rattail/package/emails.py.mako', os.path.join(package, 'emails.py'),
                      **context)

        self.generate('rattail/package/settings.py', os.path.join(package, 'settings.py'))

        ##############################
        # data dir
        ##############################

        data = os.path.join(package, 'data')
        os.makedirs(data)

        config = os.path.join(data, 'config')
        os.makedirs(config)

        self.generate('rattail/package/data/config/rattail.conf.mako',
                      os.path.join(config, '{}-rattail.conf'.format(slug)),
                      **context)

        self.generate('rattail/package/data/config/web.conf.mako',
                      os.path.join(config, '{}-web.conf'.format(slug)),
                      **context)

        ##############################
        # db package dir
        ##############################

        if context['extends_db']:

            db = os.path.join(package, 'db')
            os.makedirs(db)

            self.generate('rattail/package/db/__init__.py', os.path.join(db, '__init__.py'))

            ####################
            # model
            ####################

            model = os.path.join(db, 'model')
            os.makedirs(model)

            self.generate('rattail/package/db/model/__init__.py.mako', os.path.join(model, '__init__.py'),
                          **context)

            self.generate('rattail/package/db/model/core.py.mako', os.path.join(model, 'core.py'),
                          **context)

            ####################
            # alembic
            ####################

            alembic = os.path.join(db, 'alembic')
            os.makedirs(alembic)

            self.generate('rattail/package/db/alembic/README', os.path.join(alembic, 'README'))

            self.generate('rattail/package/db/alembic/env.py.mako', os.path.join(alembic, 'env.py'),
                          **context)

            self.generate('rattail/package/db/alembic/script.py.mako_', os.path.join(alembic, 'script.py.mako'))

            versions = os.path.join(alembic, 'versions')
            os.makedirs(versions)

            self.generate('rattail/package/db/alembic/versions/.keepme', os.path.join(versions, '.keepme'))

        ##############################
        # web package dir
        ##############################

        if context['has_web']:

            web = os.path.join(package, 'web')
            os.makedirs(web)

            self.generate('rattail/package/web/__init__.py', os.path.join(web, '__init__.py'))

            self.generate('rattail/package/web/app.py.mako', os.path.join(web, 'app.py'),
                          **context)

            self.generate('rattail/package/web/menus.py.mako', os.path.join(web, 'menus.py'),
                          **context)

            self.generate('rattail/package/web/subscribers.py.mako', os.path.join(web, 'subscribers.py'),
                          **context)

            static = os.path.join(web, 'static')
            os.makedirs(static)

            self.generate('rattail/package/web/static/__init__.py.mako', os.path.join(static, '__init__.py'),
                          **context)

            templates = os.path.join(web, 'templates')
            os.makedirs(templates)

            self.generate('rattail/package/web/templates/base_meta.mako_tmpl', os.path.join(templates, 'base_meta.mako'),
                          **context)

            views = os.path.join(web, 'views')
            os.makedirs(views)

            self.generate('rattail/package/web/views/__init__.py.mako', os.path.join(views, '__init__.py'),
                          **context)

            self.generate('rattail/package/web/views/common.py.mako', os.path.join(views, 'common.py'),
                          **context)

        ##############################
        # dev
        ##############################

        dev = os.path.join(path, 'dev')
        os.makedirs(dev)

        self.generate('rattail/dev/bootstrap.py.mako', os.path.join(dev, 'bootstrap.py'),
                      **context)

        self.generate('rattail/dev/tasks.py.mako', os.path.join(dev, 'tasks.py'),
                      **context)

        self.generate('rattail/dev/rattail.conf.mako', os.path.join(dev, 'rattail.conf'),
                      **context)

        self.generate('rattail/dev/web.conf.mako', os.path.join(dev, 'web.conf'),
                      **context)

        ##############################
        # fablib / machines
        ##############################

        if context['uses_fabric']:

            fablib = os.path.join(package, 'fablib')
            os.makedirs(fablib)

            self.generate('rattail/package/fablib/__init__.py.mako', os.path.join(fablib, '__init__.py'),
                          **context)

            self.generate('rattail/package/fablib/python.py.mako', os.path.join(fablib, 'python.py'),
                          **context)

            deploy = os.path.join(fablib, 'deploy')
            os.makedirs(deploy)

            python = os.path.join(deploy, 'python')
            os.makedirs(python)

            self.generate('rattail/package/fablib/deploy/python/premkvirtualenv.mako', os.path.join(python, 'premkvirtualenv.mako'),
                          **context)

            machines = os.path.join(path, 'machines')
            os.makedirs(machines)

            server = os.path.join(machines, 'server')
            os.makedirs(server)

            self.generate('rattail/machines/server/README.md.mako', os.path.join(server, 'README.md'),
                          **context)

            self.generate('rattail/machines/server/Vagrantfile.mako', os.path.join(server, 'Vagrantfile'),
                          **context)

            self.generate('rattail/machines/server/fabenv.py.dist.mako', os.path.join(server, 'fabenv.py.dist'),
                          **context)

            self.generate('rattail/machines/server/fabric.yaml.dist', os.path.join(server, 'fabric.yaml.dist'))

            self.generate('rattail/machines/server/fabfile.py.mako', os.path.join(server, 'fabfile.py'),
                          **context)

            deploy = os.path.join(server, 'deploy')
            os.makedirs(deploy)

            poser = os.path.join(deploy, slug)
            os.makedirs(poser)

            if options['integrates_catapult']:
                self.generate('rattail/machines/server/deploy/poser/freetds.conf.mako_', os.path.join(poser, 'freetds.conf.mako'))
                self.generate('rattail/machines/server/deploy/poser/odbc.ini', os.path.join(poser, 'odbc.ini'))

            self.generate('rattail/machines/server/deploy/poser/rattail.conf.mako', os.path.join(poser, 'rattail.conf.mako'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/cron.conf.mako', os.path.join(poser, 'cron.conf'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/web.conf.mako', os.path.join(poser, 'web.conf.mako'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/supervisor.conf.mako', os.path.join(poser, 'supervisor.conf'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/overnight.sh.mako', os.path.join(poser, 'overnight.sh'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/overnight-wrapper.sh.mako', os.path.join(poser, 'overnight-wrapper.sh'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/crontab.mako', os.path.join(poser, 'crontab.mako'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/upgrade.sh.mako', os.path.join(poser, 'upgrade.sh'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/tasks.py.mako', os.path.join(poser, 'tasks.py'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/upgrade-wrapper.sh.mako', os.path.join(poser, 'upgrade-wrapper.sh'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/sudoers.mako', os.path.join(poser, 'sudoers'),
                          **context)

            self.generate('rattail/machines/server/deploy/poser/logrotate.conf.mako', os.path.join(poser, 'logrotate.conf'),
                          **context)

    def generate_byjove_project(self, slug, options, path):
        """
        Generate a new 'byjove' project per the given arguments.
        """
        context = options

        ##############################
        # root project dir
        ##############################

        self.generate('byjove/CHANGELOG.md.mako', os.path.join(path, 'CHANGELOG.md'),
                      **context)

        self.generate('byjove/gitignore', os.path.join(path, '.gitignore'))

        self.generate('byjove/README.md.mako', os.path.join(path, 'README.md'),
                      **context)

        self.generate('byjove/vue.config.js.dist.mako', os.path.join(path, 'vue.config.js.dist'),
                      **context)

    def generate_fabric_project(self, slug, options, path):
        """
        Generate a new 'fabric' project per the given arguments.
        """
        context = options

        ##############################
        # root project dir
        ##############################

        self.generate('fabric/gitignore.mako', os.path.join(path, '.gitignore'),
                      **context)

        self.generate('fabric/README.md.mako', os.path.join(path, 'README.md'),
                      **context)

        self.generate('fabric/setup.py.mako', os.path.join(path, 'setup.py'),
                      **context)

        ##############################
        # package dir
        ##############################

        package = os.path.join(path, options['python_name'])
        os.makedirs(package)

        self.generate('fabric/package/__init__.py.mako', os.path.join(package, '__init__.py'),
                      **context)

        self.generate('fabric/package/_version.py', os.path.join(package, '_version.py'))

        ##############################
        # machines
        ##############################

        machines = os.path.join(path, 'machines')
        os.makedirs(machines)

        ##############################
        # generic-server
        ##############################

        generic_server = os.path.join(machines, 'generic-server')
        os.makedirs(generic_server)

        self.generate('fabric/machines/generic-server/README.md.mako', os.path.join(generic_server, 'README.md'),
                      **context)

        self.generate('fabric/machines/generic-server/Vagrantfile.mako', os.path.join(generic_server, 'Vagrantfile'),
                      **context)

        self.generate('fabric/machines/generic-server/fabenv.py.dist.mako', os.path.join(generic_server, 'fabenv.py.dist'),
                      **context)

        self.generate('fabric/machines/generic-server/fabric.yaml.dist', os.path.join(generic_server, 'fabric.yaml.dist'))

        self.generate('fabric/machines/generic-server/fabfile.py.mako', os.path.join(generic_server, 'fabfile.py'),
                      **context)

        ##############################
        # theo-server
        ##############################

        theo_server = os.path.join(machines, 'theo-server')
        os.makedirs(theo_server)

        self.generate('fabric/machines/theo-server/README.md', os.path.join(theo_server, 'README.md'))

        self.generate('fabric/machines/theo-server/Vagrantfile', os.path.join(theo_server, 'Vagrantfile'))

        self.generate('fabric/machines/theo-server/fabenv.py.dist.mako', os.path.join(theo_server, 'fabenv.py.dist'),
                      **context)

        self.generate('fabric/machines/theo-server/fabric.yaml.dist', os.path.join(theo_server, 'fabric.yaml.dist'))

        self.generate('fabric/machines/theo-server/fabfile.py.mako', os.path.join(theo_server, 'fabfile.py'),
                      **context)

        theo_deploy = os.path.join(theo_server, 'deploy')
        os.makedirs(theo_deploy)

        theo_python = os.path.join(theo_deploy, 'python')
        os.makedirs(theo_python)

        self.generate('fabric/machines/theo-server/deploy/python/pip.conf.mako', os.path.join(theo_python, 'pip.conf.mako'),
                      **context)

        theo_rattail = os.path.join(theo_deploy, 'rattail')
        os.makedirs(theo_rattail)

        self.generate('fabric/machines/theo-server/deploy/rattail/rattail.conf.mako', os.path.join(theo_rattail, 'rattail.conf.mako'),
                      **context)

        self.generate('fabric/machines/theo-server/deploy/rattail/freetds.conf.mako_', os.path.join(theo_rattail, 'freetds.conf.mako'))

        self.generate('fabric/machines/theo-server/deploy/rattail/odbc.ini', os.path.join(theo_rattail, 'odbc.ini'))

        theo_theo_common = os.path.join(theo_deploy, 'theo-common')
        os.makedirs(theo_theo_common)

        self.generate('fabric/machines/theo-server/deploy/theo-common/rattail.conf.mako', os.path.join(theo_theo_common, 'rattail.conf.mako'),
                      **context)

        self.generate('fabric/machines/theo-server/deploy/theo-common/web.conf.mako', os.path.join(theo_theo_common, 'web.conf.mako'),
                      **context)

        self.generate('fabric/machines/theo-server/deploy/theo-common/upgrade.sh.mako', os.path.join(theo_theo_common, 'upgrade.sh.mako'),
                      **context)

        self.generate('fabric/machines/theo-server/deploy/theo-common/tasks.py.mako_', os.path.join(theo_theo_common, 'tasks.py.mako'))

        self.generate('fabric/machines/theo-server/deploy/theo-common/upgrade-wrapper.sh.mako_', os.path.join(theo_theo_common, 'upgrade-wrapper.sh.mako'))

        self.generate('fabric/machines/theo-server/deploy/theo-common/supervisor.conf.mako_', os.path.join(theo_theo_common, 'supervisor.conf.mako'))

        self.generate('fabric/machines/theo-server/deploy/theo-common/sudoers.mako_', os.path.join(theo_theo_common, 'sudoers.mako'))
