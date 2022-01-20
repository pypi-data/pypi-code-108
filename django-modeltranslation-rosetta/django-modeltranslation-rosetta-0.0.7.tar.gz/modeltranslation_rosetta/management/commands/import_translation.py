# coding: utf-8
from __future__ import print_function
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from ...import_translation import (
    parse_po,
    parse_xlsx,
    load_translation,
    load_same_rows,
    group_dataset,
    parse_xml,
)

FROM_LANG = settings.LANGUAGES[0][0]
TO_LANG = settings.LANGUAGES[1][0]


class Command(BaseCommand):
    args = "<app app ...>"
    help = (
        "reloads permissions for specified apps, or all apps if no args are specified"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            "-i",
            action="store",
            dest="filename",
            type=argparse.FileType("r"),
            default=sys.stdin,
        )
        parser.add_argument(
            "--format",
            "-f",
            action="store",
            dest="format",
            default="po",
            help="Format. xlsx or po",
        )

        parser.add_argument(
            "--from_lang",
            "-fl",
            action="store",
            dest="from_lang",
            default=FROM_LANG,
            help="from lang",
        )

        parser.add_argument(
            "--to_lang",
            "-tl",
            action="store",
            dest="to_lang",
            default=TO_LANG,
            help="to lang",
        )

        parser.add_argument("--cleanup", action="store_true", dest="cleanup")

        parser.add_argument("--dry_run", action="store_true", dest="dry_run")

    def import_translation(self, filename, **options):
        fmt = options.get("format")

        from_lang = options["from_lang"]
        to_lang = options["to_lang"]

        flatten_dataset = []

        if fmt == "xlsx":
            flatten_dataset = parse_xlsx(filename)
        elif fmt == "po":
            flatten_dataset = parse_po(filename)
        elif fmt == "xml":
            flatten_dataset = parse_xml(filename)

        result = load_translation(group_dataset(flatten_dataset), to_lang=to_lang)

        print(result["stat"])

        load_same_rows(flatten_dataset, from_lang=from_lang, to_lang=to_lang)

    def handle(self, **options):
        sid = transaction.savepoint()
        try:
            self.import_translation(**options)
        except Exception as e:
            print(e)
            transaction.savepoint_rollback(sid)
            return

        if options.get("dry_run"):
            transaction.savepoint_rollback(sid)
            return

        transaction.savepoint_commit(sid)
