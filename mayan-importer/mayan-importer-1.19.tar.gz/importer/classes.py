import csv
import io
import json
import logging

from django.apps import apps
from django.core.files import File
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.class_mixins import AppsModuleLoaderMixin
from mayan.apps.storage.utils import NamedTemporaryFile
from mayan.apps.templating.classes import Template

from .exceptions import ImportSetupActionError

logger = logging.getLogger(name=__name__)

__all__ = ('ImportSetupActionBackend', 'ImportSetupBackend',)


class ImportSetupActionBackendMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(
            mcs, name, bases, attrs
        )

        if not new_class.__module__ == __name__:
            mcs._registry[
                '{}.{}'.format(new_class.__module__, name)
            ] = new_class

        return new_class


class ImportSetupActionBackend(
    AppsModuleLoaderMixin, metaclass=ImportSetupActionBackendMetaclass
):
    _loader_module_name = 'import_setup_actions'
    fields = ()

    @classmethod
    def clean(cls, request, cleaned_data, dynamic_form_data):
        cleaned_data['backend_data'] = json.dumps(obj=dynamic_form_data)
        return cleaned_data

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return sorted(cls._registry.values(), key=lambda x: x.label)

    @classmethod
    def get_choices(cls):
        apps_name_map = {
            app.name: app for app in apps.get_app_configs()
        }

        # Match each import_setup action to an app
        apps_import_setup_action_map = {}

        for klass in cls.get_all():
            for app_name, app in apps_name_map.items():
                if klass.__module__.startswith(app_name):
                    apps_import_setup_action_map.setdefault(app, [])
                    apps_import_setup_action_map[app].append(
                        (klass.id(), klass.label)
                    )

        result = [
            (app.verbose_name, import_setup_actions) for app, import_setup_actions in apps_import_setup_action_map.items()
        ]

        # Sort by app, then by import_setup action
        return sorted(result, key=lambda x: (x[0], x[1]))

    @classmethod
    def id(cls):
        return '{}.{}'.format(cls.__module__, cls.__name__)

    def __init__(self, **kwargs):
        # Set the values of the dynamic fields
        for class_field in getattr(self, 'class_fields', ()):
            setattr(self, class_field, kwargs.pop(class_field, None))

        # Set the values of the persistent backend attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_form_schema(self, request=None):
        result = {
            'fields': self.fields or {},
            'media': getattr(self, 'media', {}),
            'widgets': getattr(self, 'widgets', {}),
        }

        if hasattr(self, 'field_order'):
            result['field_order'] = self.field_order

        return result

    def render_field(self, field_name, context):
        try:
            result = Template(
                template_string=getattr(self, field_name, '')
            ).render(
                context=context
            )
        except Exception as exception:
            raise ImportSetupActionError(
                _('%(field_name)s template error: %(exception)s') % {
                    'field_name': field_name, 'exception': exception
                }
            )

        logger.debug('%s template result: %s', field_name, result)

        return result


class ImportSetupBackendMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(
            mcs, name, bases, attrs
        )
        if not new_class.__module__ == 'importer.classes':
            mcs._registry[
                '{}.{}'.format(new_class.__module__, name)
            ] = new_class

        return new_class


class ImportSetupBackend(
    AppsModuleLoaderMixin, metaclass=ImportSetupBackendMetaclass
):
    _loader_module_name = 'importers'
    fields = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return cls._registry

    @classmethod
    def get_choices(cls):
        return sorted(
            [
                (
                    key, backend.label
                ) for key, backend in cls.get_all().items()
            ], key=lambda x: x[1]
        )

    @classmethod
    def get_class_fields(cls):
        backend_field_list = getattr(cls, 'fields', {}).keys()
        return getattr(cls, 'class_fields', backend_field_list)

    def __init__(self, **kwargs):
        for class_field in getattr(self, 'class_fields', ()):
            setattr(self, class_field, kwargs.get(class_field, None))

        self.credential_class = kwargs.get('credential_class', None)
        self.credential_data = kwargs.get('credential_data', None)

    def check_valid(self, identifier, data):
        return True


class NullBackend(ImportSetupBackend):
    label = _('Null backend')


class ModelFiler:
    _registry = {}

    @staticmethod
    def get_field_names(model):
        skipped_field_types = (
            models.fields.AutoField, models.fields.related.ForeignKey
        )
        field_names = []

        for field in model._meta.fields:
            if not isinstance(field, skipped_field_types):
                field_names.append(field.name)

        return field_names

    @staticmethod
    def get_full_model_name(model):
        return '{}.{}'.format(model._meta.app_label, model._meta.model_name)

    @classmethod
    def get(cls, full_model_name):
        return cls._registry[full_model_name]

    def __init__(self, model, bulk_size):
        self.model = model
        self.bulk_size = bulk_size
        self.__class__._registry[
            ModelFiler.get_full_model_name(model=model)
        ] = self

    def load(self, shared_upload_file, field_defaults=None):
        if not field_defaults:
            field_defaults = {}

        field_names = ModelFiler.get_field_names(model=self.model)

        with shared_upload_file.open() as file_object_binary:
            with io.TextIOWrapper(file_object_binary) as file_object:
                file_object.readline()  # Header
                reader = csv.DictReader(file_object, fieldnames=field_names)
                manager = self.model._meta.default_manager

                bulk_list = []
                bulk_count = 0

                for row in reader:
                    row.update(**field_defaults)
                    bulk_list.append(self.model(**row))
                    bulk_count = bulk_count + 1
                    if bulk_count > self.bulk_size:
                        manager.bulk_create(bulk_list)
                        bulk_list = []
                        bulk_count = 0

                        manager.bulk_create(bulk_list)

                manager.bulk_create(bulk_list)

    def save(self, filter_kwargs=None):
        SharedUploadedFile = apps.get_model(
            app_label='common', model_name='SharedUploadedFile'
        )

        if not filter_kwargs:
            filter_kwargs = {}

        field_names = ModelFiler.get_field_names(model=self.model)

        queryset = self.model._meta.default_manager.filter(**filter_kwargs)

        with NamedTemporaryFile(mode='r+') as file_object:
            writer = csv.DictWriter(file_object, fieldnames=field_names)

            writer.writeheader()
            for item in queryset.values(*field_names):
                writer.writerow(item)

            file_object.seek(0)

            return SharedUploadedFile.objects.create(
                file=File(file_object),
            )
