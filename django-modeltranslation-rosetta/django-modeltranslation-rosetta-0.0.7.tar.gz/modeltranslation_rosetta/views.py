# coding: utf-8
from __future__ import unicode_literals

from django.contrib import messages
from django.db.transaction import atomic
from django.forms.models import modelform_factory, modelformset_factory
from django.shortcuts import redirect
from django.utils import timezone, translation
from django.utils.timezone import localtime
from django.views.generic.list import MultipleObjectMixin
from modeltranslation.translator import translator

from modeltranslation_rosetta.import_translation import (
    load_translation,
    group_dataset,
    load_same_rows,
)
from modeltranslation_rosetta.utils.signals import DisconnectSignal
from .admin_views import AdminTemplateView, AdminFormView
from .export_translation import (
    export_po,
    collect_translations,
    get_opts_from_model,
    export_xlsx,
    export_xml,
)
from .filter import FilterForm
from .forms import FieldForm, FieldFormSet, ImportTranslationForm, ExportTranslationForm
from .settings import DEFAULT_FROM_LANG, DEFAULT_TO_LANG
from .templates import get_template
from .utils import get_models, get_model
from .utils.response import FileResponse


class ListModelView(AdminTemplateView):
    template_name = get_template("list_models.html")

    def get_context_data(self, **kwargs):
        context = super(ListModelView, self).get_context_data(**kwargs)
        context["translated_models"] = get_models()
        export_form_data = None
        if self.request.method == "POST":
            export_form_data = self.request.POST

        context["export_form"] = ExportTranslationForm(data=export_form_data)
        context["import_form"] = ImportTranslationForm()
        return context

    def get_filename(self, file_format, includes=None):
        now = localtime(timezone.now())
        if includes:
            includes = " ".join(includes)
        else:
            includes = "All models"

        return f"{includes}_{now:%Y-%m-%d %H:%M}.{file_format}"

    def post(self, request, *args, **kwargs):
        if request.GET.get("_export"):
            # TODO select lang
            form = ExportTranslationForm(request.POST)
            if not form.is_valid():
                context = self.get_context_data(**kwargs)
                return self.render_to_response(context)

            form_data = form.cleaned_data
            from_lang = form_data["from_lang"]
            to_lang = form_data["to_lang"]
            file_format = form_data["format"]
            includes = form_data["translation_models"]

            translations = collect_translations(
                from_lang=from_lang, to_lang=to_lang, includes=includes
            )
            if file_format == "po":
                stream = export_po(to_lang=to_lang, translations=translations)
            elif file_format == "xlsx":
                stream = export_xlsx(to_lang=to_lang, translations=translations)
            else:
                raise NotImplementedError("Incorrect format")

            response = FileResponse(
                stream.read(), self.get_filename(file_format, includes)
            )
            return response

        return redirect(".")


class EditTranslationView(AdminFormView, MultipleObjectMixin):
    template_name = get_template("edit_translation.html")
    form_class = FieldForm
    paginate_by = 10

    def get_success_url(self):
        return self.request.META["HTTP_REFERER"]

    def form_valid(self, form):
        form.save()
        return super(EditTranslationView, self).form_valid(form)

    def get_model_info(self):
        return get_model(*self.args)

    def get_model(self):
        return self.get_model_info()["model"]

    def filter_queryset(self, queryset):
        # TODO Migrate to FilterSet
        self.filter_form = FilterForm(queryset, data=self.request.GET or None)
        queryset = self.filter_form.qs
        filter_class = self.get_extra_filter_class()
        self.extra_filter_form = None
        if filter_class:
            _filter = filter_class(
                self.request.GET, queryset=queryset, prefix="extra_filter"
            )
            self.extra_filter_form = _filter.form
            queryset = _filter.qs
        return queryset

    def get_queryset(self):
        opts = self.get_translation_options()
        if hasattr(opts, "get_queryset"):
            return opts.get_queryset()
        return self.get_model().objects.filter()

    def get_form_class(self):
        return modelform_factory(self.get_model(), form=self.form_class, fields=[])

    def get_translation_options(self):
        return translator.get_options_for_model(self.get_model())

    def get_extra_filter_class(self):
        trans_opts = self.get_translation_options()
        filter_class = getattr(trans_opts, "filter_class", None)
        return filter_class

    def get_form(self, form_class=None):
        self.object_list = queryset = self.filter_queryset(self.get_queryset())

        form_kw = self.get_form_kwargs()
        form_class = self.get_form_class()
        ModelFormSet = modelformset_factory(
            self.get_model(),
            form=form_class,
            formset=FieldFormSet,
            extra=0,
            can_delete=False,
            can_order=False,
        )
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset=queryset, page_size=self.paginate_by
        )
        queryset = self.get_model().objects.filter(
            id__in=list(queryset.values_list("id", flat=True))
        )
        fields = None
        from_lang = DEFAULT_FROM_LANG
        to_lang = DEFAULT_TO_LANG
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            fields = data.get("fields")
            from_lang = data["from_lang"]
            to_lang = data["to_lang"]
        return ModelFormSet(
            queryset=queryset,
            fields=fields,
            from_lang=from_lang,
            to_lang=to_lang,
            **form_kw,
        )

    def get_context_data(self, **kwargs):
        context = super(EditTranslationView, self).get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        context["extra_filter_form"] = self.extra_filter_form
        return context

    def get_filename(self):
        model_key = self.get_model_info()["model_key"]
        cleaned_data = self.filter_form.cleaned_data
        from_lang = cleaned_data.get("from_lang") or DEFAULT_FROM_LANG
        to_lang = cleaned_data.get("to_lang") or DEFAULT_TO_LANG
        parts = [
            model_key,
            " ".join(cleaned_data.get("fields") or []),
            cleaned_data.get("search"),
            from_lang,
            to_lang,
        ]
        now = localtime(timezone.now())

        name = "_".join(filter(None, parts))
        file_format = self.request.GET.get("_export")
        if file_format == "xml_merged":
            file_format = "xml"

        return f"{name}_{now:%Y-%m-%d %H:%M}.{file_format}"

    def get_export(self, request, *args, **kwargs):
        file_format = request.GET.get("_export")

        form_data = self.filter_form.cleaned_data

        from_lang = form_data.get("from_lang") or DEFAULT_FROM_LANG
        to_lang = form_data.get("to_lang") or DEFAULT_TO_LANG

        includes = None

        fields = form_data.get("fields")
        if fields:
            opts = get_opts_from_model(self.object_list.model)
            includes = [".".join([opts["model_key"], f]) for f in fields]

        with translation.override(from_lang):
            queryset = self.filter_queryset(self.get_queryset())
            translations = collect_translations(
                from_lang=from_lang,
                to_lang=to_lang,
                translate_status=form_data["translate_status"],
                queryset=queryset,
                includes=includes,
            )
            if file_format == "po":
                stream = export_po(
                    from_lang=from_lang,
                    to_lang=to_lang,
                    translations=translations,
                    queryset=self.object_list,
                )
            elif file_format == "xlsx":
                stream = export_xlsx(
                    translations=translations,
                    from_lang=from_lang,
                    to_lang=to_lang,
                    queryset=self.object_list,
                )
            elif file_format in ["xml", "xml_merged"]:
                stream = export_xml(
                    translations=translations,
                    from_lang=from_lang,
                    to_lang=to_lang,
                    queryset=self.object_list,
                    merge_trans=file_format == "xml_merged",
                )
            else:
                raise NotImplementedError("Unknown format")

        response = FileResponse(stream.read(), self.get_filename())
        return response

    def get(self, request, *args, **kwargs):
        response = super(EditTranslationView, self).get(*args, **kwargs)
        if request.GET.get("_export"):
            return self.get_export(request, *args, **kwargs)
        return response


class ImportTranslationView(AdminFormView):
    form_class = ImportTranslationForm
    template_name = "modeltranslation_rosetta/default/import.html"

    @atomic
    def form_valid(self, form):
        form_data = form.cleaned_data

        # TODO add into filter form
        from_lang = form_data.get("from_lang") or DEFAULT_FROM_LANG
        to_lang = form_data.get("to_lang") or DEFAULT_TO_LANG

        flatten_dataset = list(form_data["dataset"])
        result = load_translation(group_dataset(flatten_dataset), to_lang=to_lang)

        # TODO customize signal  hook
        with DisconnectSignal():
            messages.add_message(self.request, messages.SUCCESS, result["stat"])
            result_same_rows = load_same_rows(
                flatten_dataset, from_lang=from_lang, to_lang=to_lang
            )
            messages.add_message(self.request, messages.SUCCESS, result_same_rows)
        return redirect(".")
