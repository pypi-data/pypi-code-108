import math
from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import HttpResponse, get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.eveonline.evelinks import dotlan
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag
from app_utils.views import (
    JSONResponseMixin,
    bootstrap_label_html,
    fontawesome_link_button_html,
    link_html,
    no_wrap_html,
    yesno_str,
)

from . import __title__
from .app_settings import (
    STRUCTURETIMERS_DEFAULT_PAGE_LENGTH,
    STRUCTURETIMERS_PAGING_ENABLED,
)
from .constants import EveCategoryId, EveGroupId, EveTypeId
from .forms import TimerForm
from .models import DistancesFromStaging, StagingSystem, Timer

logger = LoggerAddTag(get_extension_logger(__name__), __title__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
MAX_HOURS_PASSED = 2


class TimerListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "structuretimers/timer_list.html"
    permission_required = "structuretimers.basic_access"

    def get_context_data(self, **kwargs):
        staging_systems_qs = StagingSystem.objects.select_related(
            "eve_solar_system", "eve_solar_system__eve_constellation__eve_region"
        ).filter(eve_solar_system__isnull=False)
        selected_staging_system = None
        staging_system_name = self.request.GET.get("staging")
        if staging_system_name:
            try:
                selected_staging_system = staging_systems_qs.get(
                    eve_solar_system__name=self.request.GET.get("staging")
                )
            except (StagingSystem.DoesNotExist, ValueError):
                pass
        if not selected_staging_system:
            selected_staging_system = staging_systems_qs.filter(is_main=True).first()
            if not selected_staging_system:
                selected_staging_system = staging_systems_qs.first()
        stageing_systems = staging_systems_qs.order_by("eve_solar_system__name")
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "current_time": now().strftime("%Y-%m-%d %H:%M:%S"),
                "max_hours_expired": MAX_HOURS_PASSED,
                "title": __title__,
                "data_tables_page_length": STRUCTURETIMERS_DEFAULT_PAGE_LENGTH,
                "data_tables_paging": STRUCTURETIMERS_PAGING_ENABLED,
                "selected_staging_system": selected_staging_system,
                "stageing_systems": stageing_systems,
                "tab": self.request.GET.get("tab", "current"),
            }
        )
        return context


class TimerListDataView(
    LoginRequiredMixin, PermissionRequiredMixin, JSONResponseMixin, ListView
):
    """Produce timer list in JSON for AJAX call."""

    model = Timer
    permission_required = "structuretimers.basic_access"

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        timers_qs = qs.visible_to_user(self.request.user)
        timers_qs = timers_qs.filter_by_tab(
            tab_name=self.kwargs.get("tab_name"), max_hours_passed=MAX_HOURS_PASSED
        )
        timers_qs = timers_qs.select_related(
            "eve_solar_system__eve_constellation__eve_region",
            "structure_type",
            "structure_type__eve_group",
            "eve_character",
            "eve_corporation",
            "eve_alliance",
        )
        return timers_qs

    def get_data(self, context):
        staging_system_pk = self.request.GET.get("staging")
        if staging_system_pk:
            distances_map = {
                obj.timer_id: obj
                for obj in DistancesFromStaging.objects.filter(
                    staging_system__pk=staging_system_pk
                ).all()
            }
        else:
            distances_map = dict()
        data = list()
        for timer in self.object_list:
            # location
            location = link_html(
                dotlan.solar_system_url(timer.eve_solar_system.name),
                timer.eve_solar_system.name,
            )
            if timer.location_details:
                location += format_html("<br><em>{}</em>", timer.location_details)

            location += format_html(
                "<br>{}", timer.eve_solar_system.eve_constellation.eve_region.name
            )
            # distance
            try:
                distances = distances_map[timer.id]
            except KeyError:
                distance_text = "?"
                distances = None
            else:
                light_years_text = (
                    f"{math.ceil(distances.light_years * 10) / 10} ly"
                    if distances.light_years is not None
                    else "N/A"
                )
                jumps_text = (
                    f"{distances.jumps} jumps" if distances.jumps is not None else "N/A"
                )
                distance_text = format_html("{}<br>{}", light_years_text, jumps_text)

            # structure & timer type & fitting image
            timer_type = bootstrap_label_html(
                timer.get_timer_type_display(), timer.label_type_for_timer_type()
            )
            if timer.structure_type:
                structure_type_icon_url = timer.structure_type.icon_url(size=64)
                structure_type_name = timer.structure_type.name
            else:
                structure_type_icon_url = ""
                structure_type_name = "(unknown)"

            structure = format_html(
                '<div class="flex-container">'
                '  <div style="padding-top: 4px;"><img src="{}" width="40"></div>'
                '  <div style="text-align: left;">'
                "    {}&nbsp;<br>"
                "    {}"
                "  </div>"
                "</div>",
                structure_type_icon_url,
                mark_safe(bootstrap_label_html(structure_type_name, "info")),
                timer_type,
            )

            # objective & tags
            tags = list()
            is_restricted = False
            if timer.is_opsec:
                tags.append(bootstrap_label_html("OPSEC", "danger"))
                is_restricted = True

            if timer.visibility != Timer.Visibility.UNRESTRICTED:
                tags.append(
                    bootstrap_label_html(timer.get_visibility_display(), "info")
                )
                is_restricted = True

            if timer.is_important:
                tags.append(bootstrap_label_html("Important", "warning"))

            objective = format_html(
                "{}<br>{}",
                mark_safe(
                    bootstrap_label_html(
                        timer.get_objective_display(), timer.label_type_for_objective()
                    )
                ),
                mark_safe(" ".join(tags)),
            )

            # name & owner
            if timer.owner_name:
                owner_name = timer.owner_name
                owner = owner_name
            else:
                owner = "-"
                owner_name = ""

            structure_name = timer.structure_name if timer.structure_name else "-"
            name = format_html("{}<br>{}", structure_name, owner)

            if timer.eve_corporation:
                corporation_name = timer.eve_corporation.corporation_name
            else:
                corporation_name = "-"

            # creator
            # if timer.eve_character:
            #     creator = format_html(
            #         "{}<br>{}",
            #         link_html(
            #             evewho.character_url(timer.eve_character.character_id),
            #             timer.eve_character.character_name,
            #         ),
            #         corporation_name,
            #     )
            # elif corporation_name:
            #     creator = corporation_name
            # else:
            #     creator = "-"

            # visibility
            visibility = ""
            if timer.visibility == Timer.Visibility.ALLIANCE and timer.eve_alliance:
                visibility = timer.eve_alliance.alliance_name
            elif timer.visibility == Timer.Visibility.CORPORATION:
                visibility = corporation_name
            distances_light_years = distances.light_years if distances else None
            data.append(
                {
                    "id": timer.id,
                    "local_time": timer.date.isoformat() if timer.date else "",
                    "date": timer.date.isoformat() if timer.date else "",
                    "location": location,
                    "structure_details": structure,
                    "name_objective": name,
                    "owner": objective,
                    # "creator": creator,
                    "distance": {
                        "display": distance_text,
                        "sort": distances_light_years,
                    },
                    "distance_light_years": distances_light_years,
                    "distance_jumps": distances.jumps if distances else None,
                    "actions": self._get_data_actions(timer),
                    "timer_type_name": timer.get_timer_type_display(),
                    "objective_name": timer.get_objective_display(),
                    "system_name": timer.eve_solar_system.name,
                    "region_name": timer.eve_solar_system.eve_constellation.eve_region.name,
                    "structure_type_name": timer.structure_type.name,
                    "owner_name": owner_name,
                    "visibility": visibility,
                    "opsec_str": yesno_str(timer.is_opsec),
                    "is_opsec": timer.is_opsec,
                    "is_passed": timer.date < now() if timer.date else None,
                    "is_important": timer.is_important,
                    "is_restricted": is_restricted,
                    "last_updated_at": timer.last_updated_at.isoformat(),
                }
            )

        return data

    def _get_data_actions(self, timer):
        actions = ""
        if timer.details_image_url or timer.details_notes:
            disabled_html = ""
            button_type = "primary"
            data_toggle = 'data-toggle="modal" data-target="#modalTimerDetails" '
            title = "Show details of this timer"
        else:
            button_type = "default"
            disabled_html = ' disabled="disabled"'
            data_toggle = ""
            title = "No details available"
        actions += (
            format_html(
                '<a type="button" id="timerboardBtnDetails" '
                f'class="btn btn-{button_type}" title="{title}"'
                f"{data_toggle}"
                f'data-timerpk="{timer.pk}"{disabled_html}>'
                '<i class="fas fa-search-plus"></i></a>'
            )
            + "&nbsp;"
        )
        if timer.user_can_edit(self.request.user):
            actions += (
                fontawesome_link_button_html(
                    reverse("structuretimers:delete", args=(timer.pk,)),
                    "far fa-trash-alt",
                    "danger",
                    "Delete this timer",
                )
                + "&nbsp;"
                + fontawesome_link_button_html(
                    reverse("structuretimers:edit", args=(timer.pk,)),
                    "far fa-edit",
                    "warning",
                    "Edit this timer",
                )
            )
        if self.request.user.has_perm("structuretimers.create_timer"):
            actions += "&nbsp;" + fontawesome_link_button_html(
                reverse("structuretimers:copy", args=(timer.pk,)),
                "far fa-copy",
                "success",
                "Copy this timer",
            )
        return no_wrap_html(actions)


class TimerDetailDataView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "structuretimers.basic_access"
    model = Timer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.visible_to_user(self.request.user).select_related(
            "structure_type", "eve_solar_system"
        )


class TimerManagementView(LoginRequiredMixin, PermissionRequiredMixin, View):
    model = Timer
    form_class = TimerForm
    title = _("Edit Structure Timer")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def send_success_message(self, keyword: str) -> None:
        """Inform user about result of his action via message."""
        timer = self.object
        messages.info(self.request, f"{keyword}: {timer}.")


class AddUpdateMixin:
    def get_form_kwargs(self):
        """Inject the request user into the kwargs passed to the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class CreateTimerView(TimerManagementView, AddUpdateMixin, CreateView):
    template_name_suffix = "_create_form"
    permission_required = (
        "structuretimers.basic_access",
        "structuretimers.create_timer",
    )
    title = _("Create New Timer")

    def form_valid(self, form):
        result = super().form_valid(form)
        timer = self.object
        logger.info(
            "Created new timer in %s at %s by user %s",
            timer.eve_solar_system,
            timer.date,
            self.request.user,
        )
        self.send_success_message(_("Added"))
        return result


class EditTimerMixin:
    permission_required = "structuretimers.basic_access"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 200:
            if (
                not self.object.user_can_edit(self.request.user)
                or not Timer.objects.filter(pk=self.object.pk)
                .visible_to_user(self.request.user)
                .exists()
            ):
                raise PermissionDenied()

        return response


class EditTimerView(EditTimerMixin, TimerManagementView, AddUpdateMixin, UpdateView):
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        result = super().form_valid(form)
        self.send_success_message(_("Updated"))
        return result


class CopyTimerView(CreateTimerView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        old_obj = get_object_or_404(Timer, pk=self.kwargs["pk"])
        new_obj = deepcopy(old_obj)
        new_obj.pk = None
        new_obj.date = None
        kwargs["instance"] = deepcopy(new_obj)
        return kwargs


class RemoveTimerView(EditTimerMixin, TimerManagementView, DeleteView):
    def __init__(self) -> None:
        self.object = None

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        response = super().delete(request, *args, **kwargs)
        self.send_success_message(_("Removed"))
        return response

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class Select2SolarSystemsView(JSONResponseMixin, ListView):
    """Dynamically generated list of solar systems for select2 widget."""

    model = EveSolarSystem

    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get("term")
        if not term:
            return qs.none()
        return qs.filter(name__istartswith=term)

    def get_context_data(self, **kwargs):
        if self.object_list:
            solar_systems = self.object_list.values("id", "name")
            results = [{"id": row["id"], "text": row["name"]} for row in solar_systems]
            results = sorted(results, key=lambda d: d["text"])
        else:
            results = None
        return {"results": results}

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class Select2StructureTypesView(JSONResponseMixin, ListView):
    """Dynamically generated list of types for select2 widget."""

    model = EveType

    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get("term")
        if not term:
            return qs.none()
        qs = (
            qs.filter(
                eve_group__eve_category_id=EveCategoryId.STRUCTURE, published=True
            )
            | qs.filter(
                eve_group_id__in=[EveGroupId.CONTROL_TOWER, EveGroupId.MOBILE_DEPOT],
                published=True,
            )
            | qs.filter(
                id__in=[EveTypeId.CUSTOMS_OFFICE, EveTypeId.IHUB, EveTypeId.TCU]
            )
        )
        return qs.distinct().filter(name__icontains=term)

    def get_context_data(self, **kwargs):
        if self.object_list:
            results = [
                {"id": row["id"], "text": row["name"]}
                for row in self.object_list.values("id", "name").order_by("name")
            ]
            results = sorted(results, key=lambda d: d["text"])
        else:
            results = None
        return {"results": results}

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
