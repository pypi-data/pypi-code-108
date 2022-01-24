from oarepo_model_builder.utils.deepmerge import deepmerge
from oarepo_model_builder.model_preprocessors import ModelPreprocessor
from oarepo_model_builder.utils.camelcase import camel_case, snake_case


def last_item(x):
    return x.rsplit('.', maxsplit=1)[-1]


class InvenioModelPreprocessor(ModelPreprocessor):
    TYPE = 'invenio'

    def transform(self, schema, settings):
        deepmerge(settings, {
            'python': {
                'record_prefix': camel_case(settings.package.rsplit('.', maxsplit=1)[-1]),
                # just make sure that the templates is always there
                'templates': {
                },
                'marshmallow': {
                    'mapping': {
                    }
                }
            }
        })

        record_prefix = settings.python.record_prefix
        self.set(settings.python, 'record-prefix-snake',
                 lambda: snake_case(settings.python.record_prefix))

        # config
        self.set(settings.python, 'config-package',
                 lambda: f'{settings.package}.config')
        self.set(settings.python, 'config-dummy-class',
                 lambda: f'{settings.package}.config.DummyClass')
        self.set(settings.python, 'config-resource-config-key',
                 lambda: f'{settings.package_base_upper}_RESOURCE_CONFIG')
        self.set(settings.python, 'config-resource-class-key',
                 lambda: f'{settings.package_base_upper}_RESOURCE_CLASS')
        self.set(settings.python, 'config-service-config-key',
                 lambda: f'{settings.package_base_upper}_SERVICE_CONFIG')
        self.set(settings.python, 'config-service-class-key',
                 lambda: f'{settings.package_base_upper}_SERVICE_CLASS')

        # ext
        self.set(settings.python, 'ext-class',
                 lambda: f'{settings.package}.ext.{record_prefix}Ext')
        self.set(settings.python, 'flask-extension-name',
                 lambda: f'{settings.package_base}')

        # proxies
        self.set(settings.python, 'proxies-current-resource',
                 lambda: f'{settings.package}.proxies.current_resource')

        # record
        self.set(settings.python, 'record-class',
                 lambda: f'{settings.package}.records.api.{record_prefix}Record')
        self.set(settings.python, 'record-metadata-class',
                 lambda: f'{settings.package}.records.models.{record_prefix}Metadata')
        self.set(settings.python, 'record-metadata-table-name',
                 lambda: f'{record_prefix.lower()}_metadata')
        #   - poetry
        self.set(settings.python, 'record-mapping-poetry',
                 lambda: f'{settings.package_base}')
        self.set(settings.python, 'record-jsonschemas-poetry',
                 lambda: f'{settings.package_base}')

        # resource
        self.set(settings.python, 'record-resource-config-class',
                 lambda: f'{settings.package}.resources.config.{record_prefix}ResourceConfig')
        self.set(settings.python, 'record-resource-class',
                 lambda: f'{settings.package}.resources.resource.{record_prefix}Resource')
        self.set(settings.python, 'record-permissions-class',
                 lambda: f'{settings.package}.services.permissions.{record_prefix}PermissionPolicy')

        # service
        self.set(settings.python, 'record-service-class',
                 lambda: f'{settings.package}.services.service.{record_prefix}Service')
        self.set(settings.python, 'record-service-config-class',
                 lambda: f'{settings.package}.services.config.{record_prefix}ServiceConfig')
        #   - schema
        self.set(settings.python, 'record-schema-class',
                 lambda: f'{settings.package}.services.schema.{record_prefix}Schema')
        self.set(settings.python, 'record-schema-metadata-class',
                 lambda: f'{settings.package}.services.schema.{record_prefix}MetadataSchema')
        #   - dumper
        self.set(settings.python, 'record-dumper-class',
                 lambda: f'{settings.package}.services.dumper.{record_prefix}Dumper')
        #   - search
        self.set(settings.python, 'record-search-options-class',
                 lambda: f'{settings.package}.services.search.{record_prefix}SearchOptions')

        # alembic
        self.set(settings.python, 'record-schema-metadata-alembic',
                 lambda: f'{settings.package_base}')
        self.set(settings.python, 'record-schema-metadata-poetry',
                 lambda: f'{settings.package_base}')

        self.set(settings.python, 'record-resource-blueprint-name',
                 lambda: record_prefix)
        self.set(settings.python, 'create-blueprint-from-app',
                 lambda: f'{settings.package}.views.create_blueprint_from_app')

        if 'model' in schema.schema:
            schema_class = settings.python.record_schema_class
            schema_metadata_class = settings.python.record_schema_metadata_class
            schema_class_base_classes = settings.python.get('record_schema_metadata_bases', []) + [
                'ma.Schema'  # alias will be recognized automatically
            ]

            deepmerge(
                schema.schema.model.setdefault('oarepo:marshmallow', {}),
                {
                    'class': schema_class,
                    'base-classes': schema_class_base_classes,
                    'generate': True
                })
            if 'properties' in schema.schema.model and 'metadata' in schema.schema.model.properties:
                deepmerge(
                    schema.schema.model.properties.metadata.setdefault('oarepo:marshmallow', {}),
                    {
                        'class': schema_metadata_class,
                        'base-classes': schema_class_base_classes,
                        'generate': True
                    })

        # default import prefixes
        settings.python.setdefault('always-defined-import-prefixes', []).extend(
            ['ma', 'ma_fields', 'ma_valid']
        )
