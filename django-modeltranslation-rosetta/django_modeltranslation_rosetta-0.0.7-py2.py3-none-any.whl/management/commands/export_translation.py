# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from ...export_translation import (
    export_po,
    collect_models,
    collect_translations,
    UNTRANSLATED,
)

EXPORT_FILTERS = getattr(settings, "MODELTRANSLATION_ROSETTA_EXPORT_FILTERS", {})


class Command(BaseCommand):
    args = "<app app ...>"
    help = "export translations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            action="store",
            dest="filename",
            type=argparse.FileType("w"),
            default=sys.stdout,
        )
        parser.add_argument(
            "--excludes",
            "-e",
            nargs="*",
            action="store",
            dest="excludes",
            help="app or app.Model or app.Model.field",
        )
        parser.add_argument(
            "--includes",
            "-i",
            nargs="*",
            action="store",
            dest="includes",
            help="app or app.Model or app.Model.field",
        )
        # Named (optional) arguments
        parser.add_argument(
            "--from_lang",
            "-fl",
            action="store",
            dest="from_lang",
            default=settings.LANGUAGES[0][0],
            help="from lang",
        )

        parser.add_argument(
            "--to_lang",
            "-tl",
            action="store",
            dest="to_lang",
            default=settings.LANGUAGES[1][0],
            help="to lang",
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
            "--skip-translated",
            action="store_true",
            dest="skip_translated",
            default=False,
            help="skip translated",
        )

        parser.add_argument(
            "--models",
            action="store_true",
            dest="print_models",
            default=False,
            help="Print list of translated field names with includes & excludes and exit",
        )

    def handle(self, **options):
        fmt = options.pop("format", None) or "xlsx"
        filename = options.pop("filename", None)
        to_lang = options["to_lang"]
        kw = {
            k: options[k]
            for k in ["from_lang", "to_lang", "includes", "excludes"]
            if k in options
        }
        if options["skip_translated"]:
            kw["translate_status"] = UNTRANSLATED

        if options.pop("print_models", False):
            models = collect_models(
                includes=options.get("includes"), excludes=options.get("excludes")
            )
            for model in models:
                print(
                    "{model_key} [{fields}]".format(
                        model_key=model["model_key"], fields=", ".join(model["fields"])
                    )
                )
            return

        translations = collect_translations(**kw)

        if fmt == "po":
            export_po(stream=filename, to_lang=to_lang, translations=translations)
