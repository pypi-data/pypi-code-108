import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import DynamicModelForm

from .classes import CredentialBackend
from .models import StoredCredential


class StoredCredentialBackendSelectionForm(forms.Form):
    backend = forms.ChoiceField(
        choices=(), help_text=_('The backend to use for the credential.'),
        label=_('Backend')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['backend'].choices = CredentialBackend.get_choices()


class StoredCredentialBackendDynamicForm(DynamicModelForm):
    class Meta:
        fields = ('label', 'internal_name', 'backend_data')
        model = StoredCredential
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
