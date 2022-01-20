# coding: utf-8
from __future__ import unicode_literals

from itertools import chain

from django import forms
from django.forms.formsets import TOTAL_FORM_COUNT
from django.forms.models import fields_for_model
from django.utils.translation import ngettext

from modeltranslation_rosetta.settings import (
    DEFAULT_FROM_LANG,
    DEFAULT_TO_LANG,
    LANGUAGES,
)
from .import_translation import parse_po, parse_xlsx, parse_xml
from .utils import build_localized_fieldname
from .utils import get_model, build_model_name, get_models


class ImportTranslationForm(forms.Form):
    file = forms.FileField()

    from_lang = forms.ChoiceField(
        choices=[("", "Auto detect (only xlsx)")] + LANGUAGES,
        initial=DEFAULT_FROM_LANG,
        required=False,
    )
    to_lang = forms.ChoiceField(
        choices=[("", "Auto detect (only xlsx)")] + LANGUAGES,
        initial=DEFAULT_TO_LANG,
        required=False,
    )

    def clean(self):
        data = dict(self.cleaned_data)
        _file = data["file"]
        from_lang = data["from_lang"]
        to_lang = data["to_lang"]
        if all([from_lang, to_lang]) and from_lang == to_lang:
            self.add_error("from_lang", "Lang must be not equal")
            self.add_error("to_lang", "Lang must be not equal")
            return
        if _file.name.lower().endswith(".po"):
            file_format = "po"
            for f in ["to_lang", "from_lang"]:
                if not data[f]:
                    self.add_error(f, "No possible detect, must be define lang")
                    return
            try:
                dataset = parse_po(_file, from_lang=from_lang, to_lang=to_lang)
            except Exception as e:
                self.add_error("file", "Invalid po file: %s" % e)
                return

        elif _file.name.lower().endswith(".xlsx"):
            file_format = "xlsx"
            try:
                dataset = parse_xlsx(_file)
            except Exception as e:
                self.add_error("file", "Invalid xlsx file: %s" % e)
                return
        elif _file.name.lower().endswith(".xml"):
            file_format = "xml"
            for f in ["to_lang", "from_lang"]:
                if not data[f]:
                    self.add_error(f, "No possible detect, must be define lang")
                    return
            try:
                dataset = parse_xml(_file, from_lang=from_lang, to_lang=to_lang)
            except Exception as e:
                self.add_error("file", "Invalid xml file: %s" % e)
                return

        else:
            self.add_error("file", "Invalid file extension. Must be .po or .xlsx")
            return

        if file_format == "xlsx":
            try:
                row = dataset.__next__()
            except StopIteration:
                self.add_error("file", "No rows!")
                return

            for f in ["to_lang", "from_lang"]:
                _lang = data[f]
                if not _lang:
                    _lang = row[f]

                if _lang != row[f]:
                    self.add_error(f, "Must be set correct lang by file")
                else:
                    data[f] = _lang
            # Restore iterator
            dataset = chain([row], dataset)

        data["dataset"] = dataset
        return data


class ExportTranslationForm(forms.Form):
    translation_models = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple, required=False
    )
    format = forms.ChoiceField(
        choices=[
            ("po", ".PO file"),
            ("xlsx", ".XLSX file"),
            ("xml", ".XML file"),
            ("xml_merged", ".XML merged"),
        ]
    )
    from_lang = forms.ChoiceField(choices=LANGUAGES, initial=DEFAULT_FROM_LANG)
    to_lang = forms.ChoiceField(choices=LANGUAGES, initial=DEFAULT_TO_LANG)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [
            (key, f"{info['meta'].verbose_name} [{key}]")
            for key, info in get_models().items()
        ]
        self.fields["translation_models"].choices = choices

    def clean(self):
        data = dict(self.cleaned_data)
        if data["from_lang"] == data["to_lang"]:
            self.add_error("to_lang", "from_lang equals to_lang")
            self.add_error("from_lang", "from_lang equals to_lang")
        return data


class FieldFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self._only_fields = kwargs.pop("fields", None)
        self.from_lang = kwargs.pop("from_lang")
        self.to_lang = kwargs.pop("to_lang")
        super(FieldFormSet, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["fields"] = self._only_fields
        kwargs["from_lang"] = self.from_lang
        kwargs["to_lang"] = self.to_lang
        return kwargs

    def _construct_form(self, i, **kwargs):
        return super(FieldFormSet, self)._construct_form(i, **kwargs)

    def get_changed_forms(self):
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if form.has_changed():
                yield form

    def clean(self):
        pass

    def is_valid(self):
        """
        Returns True if every form in self.forms is valid.
        """
        if not self.is_bound:
            return False
        # We loop over every form.errors here rather than short circuiting on the
        # first failure to make sure validation gets triggered for every form.
        forms_valid = True
        # This triggers a full clean.
        self.errors
        for form in self.get_changed_forms():
            if self.can_delete:
                if self._should_delete_form(form):
                    # This form is going to be deleted so any of its errors
                    # should not cause the entire formset to be invalid.
                    continue
            forms_valid &= form.is_valid()
        return forms_valid and not self.non_form_errors()

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self._non_form_errors.
        """
        self._errors = []
        self._non_form_errors = self.error_class()

        if not self.is_bound:  # Stop further processing.
            return
        for form in self.get_changed_forms():
            self._errors.append(form.errors)
        try:
            if (
                (
                    self.validate_max
                    and self.total_form_count() - len(self.deleted_forms) > self.max_num
                )
                or self.management_form.cleaned_data[TOTAL_FORM_COUNT]
                > self.absolute_max
            ):
                raise forms.ValidationError(
                    ngettext(
                        "Please submit %d or fewer forms.",
                        "Please submit %d or fewer forms.",
                        self.max_num,
                    )
                    % self.max_num,
                    code="too_many_forms",
                )
            if (
                self.validate_min
                and self.total_form_count() - len(self.deleted_forms) < self.min_num
            ):
                raise forms.ValidationError(
                    ngettext(
                        "Please submit %d or more forms.",
                        "Please submit %d or more forms.",
                        self.min_num,
                    )
                    % self.min_num,
                    code="too_few_forms",
                )
            # Give self.clean() a chance to do cross-form validation.
            self.clean()
        except forms.ValidationError as e:
            self._non_form_errors = self.error_class(e.error_list)


class FieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._only_fields = kwargs.pop("fields", None)
        self._from_lang = kwargs.pop("from_lang")
        self._to_lang = kwargs.pop("to_lang")
        super(FieldForm, self).__init__(*args, **kwargs)
        self.model_info = get_model(build_model_name(self.instance))
        self.build_fields()

    def get_translated_fields(self):
        opts = self.model_info["opts"]
        fields = [
            [
                field_name,
                (
                    build_localized_fieldname(field_name, self._from_lang),
                    build_localized_fieldname(field_name, self._to_lang),
                ),
            ]
            for field_name in sorted(opts.fields.keys())
            if not self._only_fields or field_name in self._only_fields
        ]
        return fields

    def build_fields(self):
        fields = []

        for b_f, translated_fields in self.get_translated_fields():
            fields.extend(translated_fields)

        self._meta.fields += fields
        self.fields.update(fields_for_model(self.model_info["model"], fields))

    def group_fields(self):
        fields = []
        for b_f, translated_fields in self.get_translated_fields():
            fields.append([self[tf] for tf in translated_fields])
        return fields
