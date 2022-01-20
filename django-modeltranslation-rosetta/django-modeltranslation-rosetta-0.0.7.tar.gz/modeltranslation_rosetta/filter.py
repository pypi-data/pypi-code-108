# coding: utf-8
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.db.models import Q
from modeltranslation.utils import build_localized_fieldname

from modeltranslation_rosetta.settings import (
    LANGUAGES,
    DEFAULT_FROM_LANG,
    DEFAULT_TO_LANG,
)
from .export_translation import (
    TRANSLATED,
    UNTRANSLATED,
    filter_queryset,
    get_opts_from_model,
)
from .utils import get_model, build_model_name

SEARCH_FIELDS = (
    getattr(settings, "MODELTRANSLATION_ROSETTA_MODEL_SEARCH_FIELDS", None) or {}
)
SEARCH_FIELDS = {k.lower(): o for k, o in SEARCH_FIELDS.items()}


class FilterForm(forms.Form):
    TRANSLATE_STATUS = (
        ("", "All"),
        (UNTRANSLATED, "Untranslated"),
        (TRANSLATED, "Translated"),
    )

    translate_status = forms.ChoiceField(
        label="Translate status", choices=TRANSLATE_STATUS, required=False
    )

    fields = forms.MultipleChoiceField(
        label="Fields", choices=(), required=False, widget=forms.CheckboxSelectMultiple
    )
    from_lang = forms.ChoiceField(
        choices=LANGUAGES, initial=DEFAULT_FROM_LANG, required=False
    )
    to_lang = forms.ChoiceField(
        choices=LANGUAGES, initial=DEFAULT_TO_LANG, required=False
    )

    search = forms.CharField(label="Search", required=False)

    def __init__(self, queryset, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.queryset = queryset
        model = self._model = queryset.model
        self.model_info = get_model(build_model_name(model))
        self["fields"].field.choices = [
            (name, model._meta.get_field(name).verbose_name)
            for name in self.model_info["opts"].fields
        ]

    def get_search_query(self):
        data = self.cleaned_data
        search_str = (data.get("search") or "").strip()
        search_fields = SEARCH_FIELDS.get(self.model_info["model_key"], ["pk"])
        q = Q()
        if not search_str or not search_fields:
            return q

        for f in search_fields:
            q |= Q(**{f: search_str})
        return q

    def clean(self):
        data = self.cleaned_data
        if data["from_lang"] == data["to_lang"]:
            self.add_error("from_lang", "Lang must be not equal")
            self.add_error("to_lang", "Lang must be not equal")
            return
        return data

    @property
    def qs(self):
        qs = filter_queryset(self.queryset, get_opts_from_model(self.queryset.model))
        if self.is_valid():
            data = self.cleaned_data

            if not any(data.values()):
                return qs

            translate_status = data.get("translate_status")
            from_lang = data["from_lang"]
            to_lang = data["to_lang"]

            base_fields = data.get("fields") or self.model_info["opts"].fields.keys()

            fields = [
                build_localized_fieldname(f, lang)
                for f in base_fields
                for lang in [from_lang, to_lang]
            ]

            q_filter = Q()
            if translate_status:
                for f in fields:
                    if translate_status == UNTRANSLATED:
                        q_filter |= Q(**{f + "__isnull": True}) | Q(**{f: ""})
                    else:
                        q_filter |= Q(**{f + "__isnull": False}) & ~Q(**{f: ""})
            q_filter &= self.get_search_query()
            return qs.filter(q_filter)
        return qs
