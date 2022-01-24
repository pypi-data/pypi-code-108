# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.core.management.base import BaseCommand
from django.core.management import call_command

from lino.modlib.search.utils import ESResolver
from lino.api import dd

class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '-m', '--map-to-file', action='store_true', dest='map_to_file',
            help="Force writing of the index's settings and mappings to the default file.")

        parser.add_argument(
            '-c', '--create-indexes', action='store_true', dest='create_indexes',
            help="Force creation of indexes in the ElasticSearch server.")

        parser.add_argument(
            '-p', '--populate-es', action='store_true', dest='populate_es',
            help="Populate ElasticSearch server with database content.")

        parser.add_argument(
            '-i', '--initialize', action='store_true', dest='initialize',
            help="Initialize ElasticSearch server.")


    def handle(self, *args, **options):

        dd.logger.info("Resolving indexes...")
        _, modified = ESResolver.resolve_es_indexes()
        dd.logger.info('Indexes resolved.')

        if modified or options.get('map_to_file') or options.get('initialize'):
            dd.logger.info('Creating index mapping file...')
            ESResolver.create_index_mapping_files()

        if modified or options.get('create_indexes') or options.get('initialize'):
            dd.logger.info('Creating ElasticSearch indexes...')
            ESResolver.create_indexes()

        if options.get('populate_es'):
            dd.logger.info('Populating ElasticSearch database...')
            ESResolver.populate_search_indexes_on_init()

        dd.logger.info('Done.')
