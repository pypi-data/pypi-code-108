import logging
from pathlib import Path

from django.utils.translation import ugettext_lazy as _

from mayan.apps.cabinets.models import Cabinet
from mayan.apps.metadata.models import MetadataType

from .classes import ImportSetupActionBackend


logger = logging.getLogger(name=__name__)


class ImportSetupActionCabinetFromPath(ImportSetupActionBackend):
    fields = {
        'parent': {
            'label': _('Parent cabinet'),
            'class': 'django.forms.ModelChoiceField', 'kwargs': {
                'help_text': _(
                    'Cabinet to use as the parent. If left blank, the first '
                    'part of the path will be the parent cabinet.'
                ),
                'queryset': Cabinet.objects.all(), 'required': False
            }
        },
        'value': {
            'label': _('Value'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Value to from which the path will be extracted. '
                    'The filename part of the path will be ignored. '
                    'Can be a literal value or template code. '
                    'Object available: {{ self }} and {{ document }}.'
                ),
                'required': True
            }
        },
    }
    field_order = ('parent', 'value')
    label = _('Cabinet tree')
    widgets = {
        'parent': {
            'class': 'django.forms.widgets.Select', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        },
        'value': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {
                'attrs': {'rows': '10'},
            }
        }
    }

    def execute(self, context):
        value = self.render_field(
            field_name='value', context=context
        )

        path = Path(value)

        parts = list(path.parts[1:-1])

        if self.parent:
            cabinet = Cabinet.objects.get(pk=self.parent)
        else:
            cabinet, created = Cabinet.objects.get_or_create(
                label=parts[0], parent=None
            )
            parts.pop(0)

        for part in parts:
            cabinet, created = cabinet.children.get_or_create(label=part)

        cabinet.document_add(document=context['document'])

    def get_form_schema(self, **kwargs):
        kwargs.pop('import_setup')

        return super().get_form_schema(**kwargs)


class ImportSetupActionDocumentMetadata(ImportSetupActionBackend):
    fields = {
        'metadata_type': {
            'label': _('Metadata type'),
            'class': 'django.forms.ModelChoiceField', 'kwargs': {
                'help_text': _(
                    'Metadata types associated with the document '
                    'type of the import setup.'
                ),
                'queryset': MetadataType.objects.none(), 'required': True
            }
        },
        'value': {
            'label': _('Value'),
            'class': 'django.forms.CharField', 'kwargs': {
                'help_text': _(
                    'Value to assign to the metadata. '
                    'Can be a literal value or template code. '
                    'Object available: {{ self }} and {{ document }}.'
                ),
                'required': True
            }
        },
    }
    field_order = ('metadata_type', 'value')
    label = _('Add metadata')
    widgets = {
        'metadata_types': {
            'class': 'django.forms.widgets.Select', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        },
        'value': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {
                'attrs': {'rows': '10'},
            }
        }
    }

    def execute(self, context):
        value = self.render_field(
            field_name='value', context=context
        )

        context['document'].metadata.create(
            metadata_type=MetadataType.objects.get(pk=self.metadata_type),
            value=value
        )

    def get_form_schema(self, **kwargs):
        import_setup = kwargs.pop('import_setup')

        result = super().get_form_schema(**kwargs)

        queryset = MetadataType.objects.get_for_document_type(
            document_type=import_setup.document_type
        )

        result['fields']['metadata_type']['kwargs']['queryset'] = queryset

        return result
