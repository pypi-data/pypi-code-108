import json

from django import forms
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import DynamicModelForm

from .classes import ImportSetupActionBackend, ImportSetupBackend
from .models import ImportSetupAction, ImportSetup


class ImportSetupActionSelectionForm(forms.Form):
    class_path = forms.ChoiceField(
        choices=(), help_text=_('The action type for this action entry.'),
        label=_('Action'), widget=forms.Select(attrs={'class': 'select2'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_path'].choices = ImportSetupActionBackend.get_choices()


class ImportSetupActionDynamicForm(DynamicModelForm):
    class Meta:
        fields = ('label', 'enabled', 'order', 'backend_data')
        model = ImportSetupAction
        widgets = {'backend_data': forms.widgets.HiddenInput}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.backend_path = kwargs.pop('backend_path')
        super().__init__(*args, **kwargs)
        self.instance.backend_path = self.backend_path
        backend_data = self.instance.get_backend_data()

        if backend_data:
            for field in self.fields:
                self.fields[field].initial = backend_data.get(field)

    def clean(self):
        cleaned_data = super().clean()
        dynamic_form_data = {}

        for field_name, field_data in self.schema['fields'].items():
            dynamic_form_data[field_name] = cleaned_data.pop(
                field_name, field_data.get('default', None)
            )
            if isinstance(dynamic_form_data[field_name], QuerySet):
                # Flatten the queryset to a list of ids
                dynamic_form_data[field_name] = list(
                    dynamic_form_data[field_name].values_list('id', flat=True)
                )
            elif isinstance(dynamic_form_data[field_name], Model):
                # Store only the ID of a model instance
                dynamic_form_data[field_name] = dynamic_form_data[field_name].pk

        cleaned_data = self.instance.get_backend().clean(
            cleaned_data=cleaned_data, dynamic_form_data=dynamic_form_data,
            request=self.request
        )

        return cleaned_data


class ImportSetupBackendSelectionForm(forms.Form):
    backend = forms.ChoiceField(
        choices=(), help_text=_('The backend to use for the import setup.'),
        label=_('Backend')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['backend'].choices = ImportSetupBackend.get_choices()


class ImportSetupBackendDynamicForm(DynamicModelForm):
    class Meta:
        fields = (
            'label', 'credential', 'document_type', 'process_size',
            'backend_data'
        )
        model = ImportSetup
        widgets = {'backend_data': forms.widgets.HiddenInput}

    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        if self.instance.backend_data:
            backend_data = json.loads(s=self.instance.backend_data)
            for key in self.instance.get_backend().fields:
                self.fields[key].initial = backend_data.get(key)

        return result

    def clean(self):
        data = super().clean()

        # Consolidate the dynamic fields into a single JSON field called
        # 'backend_data'.
        backend_data = {}

        for field_name, field_data in self.schema['fields'].items():
            backend_data[field_name] = data.pop(
                field_name, field_data.get('default', None)
            )

        data['backend_data'] = json.dumps(obj=backend_data)
        return data


class ModelFilerUpload(forms.Form):
    uploaded_file = forms.FileField(
        help_text=_('CSV file that contain rows of model data'),
        label=_('File')
    )
