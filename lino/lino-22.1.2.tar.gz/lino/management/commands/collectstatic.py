# -*- coding: UTF-8 -*-
# Copyright 2009-2021 Rumma & Ko Ltd.
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from django.core.management.base import BaseCommand
from django.contrib.staticfiles.management.commands.collectstatic import Command
from django.core.management import call_command
from django.conf import settings

# from lino.modlib.help.management.commands.makehelp import Command as MakeHelp


class Command(Command):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.collect_static = CollectStatic(*args, **kwargs)
        # self.make_help = MakeHelp(*args, **kwargs)

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        # self.collect_static.add_arguments(parser)
        # self.make_help.add_arguments(parser)

        parser.add_argument(
            '--skip-cachebuild', '--skip-cache-build', action='store_true',
            dest='skip_cache', help="Do NOT build site cache.")
        parser.add_argument(
            '--skipcollect', '--skip-collect', action='store_true',
            dest='skip_collect', help="Do NOT collect static files.")
        parser.add_argument(
            '--skiphelp', '--skip-help', action='store_true',
            dest='skip_help', help="Do NOT build local help pages.")

    def handle(self, **options):
        if not options['skip_cache']:
            settings.SITE.kernel.default_ui.renderer.build_site_cache(
                force=True, from_commandline=True)

        if not options['skip_help']:
            if settings.SITE.is_installed('help'):
                if settings.SITE.plugins.help.make_help_pages:
                    call_command('makehelp')

        if not options['skip_collect']:
            super(Command, self).handle(**options)
            # self.collect_static.handle(**options)
