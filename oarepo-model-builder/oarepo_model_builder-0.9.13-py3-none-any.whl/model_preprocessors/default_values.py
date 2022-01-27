import os
from pathlib import Path
from typing import Dict

from . import ModelPreprocessor
from ..schema import ModelSchema


class DefaultValuesModelPreprocessor(ModelPreprocessor):
    TYPE = 'default'

    def transform(self, schema: ModelSchema, settings: Dict):
        self.set(settings, 'package',
                 lambda: os.path.basename(schema.schema.get('output-directory', os.getcwd())).replace('-', '_'))

        self.set(settings, 'processing-order', lambda: ['settings', '*', 'model'])

        self.set(settings, 'package-base', lambda: settings.package.rsplit('.', maxsplit=1)[-1])

        self.set(settings, 'package-base-upper', lambda: settings.package_base.upper())

        self.set(settings, 'kebap-package', lambda: settings.package.replace('_', '-'))

        @self.set(settings, 'package-path')
        def c():
            package_path = settings.package.split('.')
            return Path(package_path[0]).joinpath(*package_path[1:])

        self.set(settings, 'schema-version', lambda: schema.schema.get('version', '1.0.0'))

        self.set(settings, 'schema-name', lambda: f"{settings.kebap_package}-{settings.schema_version}.json")

        self.set(
            settings, 'schema-file', lambda: os.path.join(
                settings.package_path,
                'records',
                'jsonschemas',
                settings.schema_name
            )
        )

        self.set(
            settings, 'mapping-package', lambda: f'{settings.package}.records.mappings'
        )

        self.set(
            settings, 'jsonschemas-package', lambda: f'{settings.package}.records.jsonschemas'
        )

        self.set(
            settings, 'mapping-file', lambda: os.path.join(
                settings.package_path,
                'records',
                'mappings',
                'v7',
                settings.package_base,
                settings.schema_name
            )
        )

        self.set(settings, 'schema-server', lambda: 'http://localhost/schemas/')

        self.set(settings, 'index-name',
                 lambda: settings.package_base + '-' + os.path.basename(settings.mapping_file).replace('.json', ''))

        self.set(settings, 'collection-url', lambda: f'/{settings.package_base}/')
