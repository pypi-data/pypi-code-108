from collections import OrderedDict
from typing import Any, Dict

from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from django.forms import CharField, Form, Textarea, TypedChoiceField, model_to_dict
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from django_tables2 import SingleTableView
from formtools.wizard.views import CookieWizardView
from material import Layout
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.apps.evalu.forms import (
    AgreementWidget,
    ComparisonGroupFormSet,
    EvaluationFinishForm,
    EvaluationItemFormSet,
    EvaluationPartForm,
    EvaluationPhaseForm,
    PasswordForm,
    RegisterForEvaluationForm,
)
from aleksis.apps.evalu.models import (
    Answer,
    DoneEvaluation,
    EvaluationGroup,
    EvaluationPart,
    EvaluationPhase,
    EvaluationRegistration,
    EvaluationResult,
    QuestionType,
)
from aleksis.apps.evalu.tables import EvaluationPartTable, EvaluationPhaseTable
from aleksis.core.mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView
from aleksis.core.util.pdf import render_pdf


class EvaluationPartListView(PermissionRequiredMixin, SingleTableView):
    """Table of all extra marks."""

    model = EvaluationPart
    table_class = EvaluationPartTable
    permission_required = "evalu.view_evaluationparts_rule"
    template_name = "evalu/part/list.html"


@method_decorator(never_cache, name="dispatch")
class EvaluationPartCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for extra marks."""

    model = EvaluationPart
    form_class = EvaluationPartForm
    permission_required = "evalu.add_evaluationpart_rule"
    template_name = "evalu/part/create.html"
    success_message = _("The evaluation part has been created.")

    def get_success_url(self):
        return reverse("edit_evaluation_part", args=[self.object.pk])


@method_decorator(never_cache, name="dispatch")
class EvaluationPartDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """Delete view for extra marks."""

    model = EvaluationPart
    permission_required = "evalu.delete_evaluationpart_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("evaluation_parts")
    success_message = _("The evaluation part has been deleted.")


@method_decorator(never_cache, name="dispatch")
class EvaluationPartEditView(PermissionRequiredMixin, AdvancedEditView):
    model = EvaluationPart
    form_class = EvaluationPartForm
    success_message = _("The evaluation part and it's items have been updated successfully.")
    permission_required = "abi.edit_evaluationpart_rule"
    template_name = "evalu/part/edit.html"

    def get_success_url(self):
        return reverse("edit_evaluation_part", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = EvaluationItemFormSet(self.request.POST or None, instance=self.object)
        context["formset"] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        form = self.get_form()
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.formset.instance = self.object
        self.formset.save()
        return super().form_valid(form)


class EvaluationPhaseListView(PermissionRequiredMixin, SingleTableView):
    """View to list all evaluation phases."""

    model = EvaluationPhase
    table_class = EvaluationPhaseTable
    permission_required = "evalu.view_evaluationphases_rule"
    template_name = "evalu/phase/list.html"


class EvaluationPhaseDetailView(PermissionRequiredMixin, DetailView):
    """Detail view for evaluation phases."""

    model = EvaluationPhase
    permission_required = "evalu.view_evaluationphase_rule"
    template_name = "evalu/phase/detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["members"] = self.object.members_with_registration
        return context


@method_decorator(never_cache, name="dispatch")
class EvaluationPhaseCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for evaluation phases."""

    model = EvaluationPhase
    form_class = EvaluationPhaseForm
    permission_required = "evalu.create_evaluationphase_rule"
    template_name = "evalu/phase/create.html"
    success_message = _("The evaluation phase has been created.")

    def get_success_url(self):
        return reverse("edit_evaluation_phase", args=[self.object.pk])


@method_decorator(never_cache, name="dispatch")
class EvaluationPhaseDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """Delete view for evaluation phases."""

    model = EvaluationPhase
    permission_required = "evalu.delete_evaluationphase_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("evaluation_phases")
    success_message = _("The evaluation phase has been deleted.")


@method_decorator(never_cache, name="dispatch")
class EvaluationPhaseEditView(PermissionRequiredMixin, AdvancedEditView):
    model = EvaluationPhase
    form_class = EvaluationPhaseForm
    success_message = _("The evaluation phase has been updated.")
    permission_required = "abi.edit_evaluationphase_rule"
    template_name = "evalu/phase/edit.html"

    def get_success_url(self):
        return reverse("evaluation_phase", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = ComparisonGroupFormSet(self.request.POST or None, instance=self.object)
        context["formset"] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        form = self.get_form()
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.formset.instance = self.object
        self.formset.save()
        return super().form_valid(form)


class EvaluationPhaseOverviewView(PermissionRequiredMixin, ListView):
    """View to list all evaluation phases a user can register or is registered for."""

    model = EvaluationPhase
    permission_required = "evalu.view_evaluationphases_overview_rule"
    template_name = "evalu/list.html"

    def get_queryset(self):
        return EvaluationPhase.objects.for_person_with_registrations(self.request.user.person)


class RegisterForEvaluationView(PermissionRequiredMixin, DetailView):
    """View to register for an evaluation phase."""

    model = EvaluationPhase
    permission_required = "evalu.register_for_evaluation_rule"
    template_name = "evalu/registration/register.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = RegisterForEvaluationForm(self.request.POST or None)
        return context

    def get_queryset(self):
        return EvaluationPhase.objects.can_register(self.request.user.person)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        form = context["form"]

        if form.is_valid():
            data = form.cleaned_data
            registration = EvaluationRegistration.register(
                self.object, self.request.user.person, data["password"], data["delete_after_phase"]
            )
            res = registration.generate_privacy_form()
            messages.success(
                request, _("You have successfully registered yourself for the evaluation.")
            )
            return redirect("evaluation_registration", registration.pk)

        return self.render_to_response(context)


class EvaluationGroupMixin:
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.object.sync_evaluation_groups()
        context["possible_groups"] = self.object.evaluation_groups_with_stats

        return context


class RegistrationDetailView(PermissionRequiredMixin, EvaluationGroupMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.view_evaluationregistration_rule"
    template_name = "evalu/registration/detail.html"


class ManageEvaluationProcessView(PermissionRequiredMixin, EvaluationGroupMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.manage_evaluation_process_rule"
    template_name = "evalu/registration/manage.html"


class StartEvaluationForGroupView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = "evalu.start_evaluation_for_group_rule"
    model = EvaluationGroup

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        group.unlock()
        messages.success(
            request,
            _("The evaluation for the group {} has been successfully unlocked.").format(
                group.group_name
            ),
        )
        return redirect("manage_evaluation_process", group.registration.pk)


class StopEvaluationForGroupView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = "evalu.stop_evaluation_for_group_rule"
    model = EvaluationGroup

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        group.lock()
        messages.success(
            request,
            _("The evaluation for the group {} has been successfully locked.").format(
                group.group_name
            ),
        )
        return redirect("manage_evaluation_process", group.registration.pk)


class EvaluationsAsParticipantListView(PermissionRequiredMixin, ListView):
    permission_required = "evalu.view_evaluations_as_participant_rule"
    template_name = "evalu/participate/list.html"

    def get_queryset(self):
        now_date = timezone.now().date()
        person = self.request.user.person
        return (
            EvaluationGroup.objects.for_person_with_done_evaluations(person)
            .filter(registration__phase__evaluation_date_start__lte=now_date)
            .distinct()
        )


class EvaluationFormView(PermissionRequiredMixin, SingleObjectMixin, CookieWizardView):
    permission_required = "evalu.evaluate_person_rule"
    model = EvaluationGroup
    template_name = "evalu/participate/form.html"
    field_mapping = {}
    headings = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_initkwargs(cls, *args, **kwargs):
        kwargs["form_list"] = cls._build_forms()
        kwargs["headings"] = cls.headings
        return super().get_initkwargs(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["headings"] = self.headings

        # Get data for preview table (last step)
        if self.steps.current == self.steps.last:
            forms = []
            for i, form_key in enumerate(self.get_form_list()):
                form = self.get_form(
                    step=form_key,
                    data=self.storage.get_step_data(form_key),
                    files=self.storage.get_step_files(form_key),
                )

                # Skip the form if it has no fields (e. g. finish form)
                if not form.fields:
                    continue

                # Make sure cleaned_data is filled
                form.is_valid()

                form_data = []
                for key, value in form.fields.items():
                    value_to_show = form.cleaned_data.get(key)

                    # Use speaking value from choices if set
                    if getattr(value, "choices", None):
                        value_to_show = dict(value.choices)[value_to_show]

                    form_data.append((value.label, value_to_show))
                forms.append((self.headings[i], form_data))
            context["form_data"] = forms

        return context

    @classmethod
    def _build_forms(cls):
        forms = []

        try:
            for i, part in enumerate(EvaluationPart.objects.order_by("order")):
                cls.headings[i] = part.name
                layout = []
                form_class_attrs = {}

                for item in part.items.order_by("order"):
                    field_name = f"item_{item.pk}"

                    # Build different types of form fields
                    if item.item_type == QuestionType.AGREEMENT:
                        field = TypedChoiceField(
                            coerce=int,
                            choices=Answer.choices,
                            label=item.question,
                            widget=AgreementWidget(),
                        )
                    elif item.item_type == QuestionType.FREE_TEXT:
                        field = CharField(
                            required=False, label=item.question, widget=Textarea(attrs={"rows": 4})
                        )
                    else:
                        continue

                    form_class_attrs[field_name] = field
                    cls.field_mapping[field_name] = item
                    layout.append(field_name)

                # Build final evaluation form
                form_class_attrs["layout"] = Layout(*layout)
                form = type(Form)(f"EvaluationForm{part.pk}", (Form,), form_class_attrs)

                forms.append(form)
        except (OperationalError, ProgrammingError):
            pass

        # Add dummy form for review page (just to make sure that it appears)
        forms.append(EvaluationFinishForm)
        cls.headings[len(forms) - 1] = _("Finish")

        return forms

    def done(self, form_list, **kwargs):
        # Prevent errors with doubled evaluations
        if DoneEvaluation.objects.filter(
            group=self.object, evaluated_by=self.request.user.person
        ).exists():
            return redirect("evaluations_as_participant")

        done_evaluation = DoneEvaluation(group=self.object, evaluated_by=self.request.user.person)
        for form in form_list:
            for key, value in form.cleaned_data.items():
                item = self.field_mapping[key]
                result = EvaluationResult(group=self.object, item=item)
                result.store_result(value)
                result.save()
                result.add_comparison_results(value)
        done_evaluation.save()
        messages.success(
            self.request,
            _("The evaluation has been finished. Thank you for doing this evaluation!"),
        )
        return redirect("evaluations_as_participant")


class FinishEvaluationView(PermissionRequiredMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.finish_evaluation_rule"
    template_name = "evalu/registration/finish.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if "finish" in request.POST:
            self.object.finish()
            return redirect("evaluation_phases_overview")

        return self.get(request, *args, **kwargs)


class EvaluationResultsView(PermissionRequiredMixin, EvaluationGroupMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.view_evaluation_results_rule"
    template_name = "evalu/password.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["as_pdf"] = self.kwargs.get("as_pdf", False)

        self.form = PasswordForm(self.request.POST or None)
        context["form"] = self.form

        return context

    def post(self, request, as_pdf: bool, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.form.is_valid():
            password = self.form.cleaned_data["password"]
            keys = self.object.keys

            try:
                keys.test(password)
            except ValueError:
                messages.error(
                    request,
                    _(
                        "There was an error with decrypting the data. "
                        "Please check if you have entered the correct password."
                    ),
                )
                return self.render_to_response(context)

        # Result calculation
        groups = self.object.groups_with_done_evaluations
        context["groups"] = groups

        all_results = []
        for group in groups:
            results_per_group = {}
            results_per_group["choices"] = {key: value for key, value in Answer.choices}
            results_per_group["average"] = group.get_average_results(password)
            results_per_group["comparison"] = group.get_comparison_results()

            by_part = OrderedDict()
            for result in results_per_group["average"]:
                part_id = result["part"]["id"]
                by_part.setdefault(part_id, {"part": result["part"], "results": []})
                by_part[part_id]["results"].append(result)
            results_per_group["average_by_part"] = by_part

            results_per_group["frequency"] = group.get_frequency_results(password)
            results_per_group["free_text"] = group.get_free_text_results(password)

            all_results.append((model_to_dict(group), results_per_group))

        context["results"] = all_results

        if as_pdf:
            return render_pdf(request, "evalu/results_pdf.html", context)

        return render(request, "evalu/results.html", context)
