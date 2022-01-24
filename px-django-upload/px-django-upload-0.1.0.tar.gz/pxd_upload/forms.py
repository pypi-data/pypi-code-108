from uuid import uuid4
from django import forms
from django.forms.models import ModelForm
from django.utils.translation import pgettext_lazy

from .models import Upload
from .utils import filename_splitext, filename_slugify


class UploadForm(ModelForm):
    allow_meta: bool

    class Meta:
        model = Upload
        fields = ['id', 'title', 'file', 'meta']

    def __init__(self, *a, allow_meta: bool = True, **k):
        super().__init__(*a, **k)
        self.allow_meta = allow_meta

    def clean_meta(self):
        value = self.cleaned_data['meta']

        if not self.allow_meta and value:
            raise forms.ValidationError(
                pgettext_lazy('pxd_upload', 'Meta not allowed to store for this file.'),
                'meta_not_allowed'
            )

        return value

    def clean_id(self):
        value = self.cleaned_data['id']
        return value or uuid4()

    def clean(self):
        cleaned_data = super().clean()

        if 'file' in cleaned_data:
            file = cleaned_data['file']
            name, ext = filename_splitext(file.name)

            if not cleaned_data['title']:
                cleaned_data['title'] = name

            file.name = f"{str(cleaned_data['id'])}-{filename_slugify(name)}{ext}"

        return cleaned_data
