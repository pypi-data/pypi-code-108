import logging
from pathlib import Path

from django.core.management.base import BaseCommand

from app_utils.logging import LoggerAddTag

from ... import __title__
from ...core.data_exporters import DataExporter

logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    help = "Export data into a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "topic",
            choices=sorted(DataExporter.topics),
            help="Section for exporting data from",
        )
        parser.add_argument(
            "--destination",
            default=str(Path.cwd().resolve()),
            help="Directory the output file will be written to",
        )

    def handle(self, *args, **options):
        self.stdout.write("Member Audit - Data Export")
        self.stdout.write()
        exporter = DataExporter.create_exporter(options["topic"])
        if not exporter.has_data():
            self.stdout.write(self.style.WARNING("No objects for output."))
        path = exporter.output_path(options["destination"])
        objects_count = exporter.count()
        self.stdout.write(
            f"Writing {objects_count:,} objects to file: {path.resolve()}"
        )
        self.stdout.write("This can take a minute. Please stand by...")
        exporter.write_to_file(options["destination"])
        self.stdout.write(self.style.SUCCESS("Done."))
