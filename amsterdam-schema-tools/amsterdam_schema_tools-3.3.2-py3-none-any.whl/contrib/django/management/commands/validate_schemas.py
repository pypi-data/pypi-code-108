from django.core.management import BaseCommand
import jsonschema
from jsonschema import draft7_format_checker
from pprint import pprint
import requests
from typing import Any

from schematools.contrib.django.models import Dataset
from schematools.validation import Validator

META_SCHEMA_URL = "https://schemas.data.amsterdam.nl/schema@v1.1.1"


class Command(BaseCommand):  # noqa: D101
    help = "Validate the loaded dataset schemas."  # noqa: A003

    def _fetch_meta_schema(self, url):

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: D102

        meta_schema = self._fetch_meta_schema(META_SCHEMA_URL)
        for dataset in Dataset.objects.all():
            try:
                jsonschema.validate(
                    instance=dataset.schema.json_data(),
                    schema=meta_schema,
                    format_checker=draft7_format_checker,
                )
            except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
                print(f"\n{e!s}")

            try:
                validator = Validator(dataset=dataset.schema)
            except:
                breakpoint()

            errors = list(validator.run_all())
            if errors:
                print(f"dataset{dataset.id} has errors")
                print(errors)
