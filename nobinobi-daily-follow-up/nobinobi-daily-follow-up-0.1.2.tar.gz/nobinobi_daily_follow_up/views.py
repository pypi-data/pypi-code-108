# -*- coding: utf-8 -*-
import datetime

import arrow
from bootstrap_modal_forms.generic import BSModalUpdateView, BSModalCreateView, BSModalDeleteView, BSModalReadView
from bootstrap_modal_forms.mixins import PassRequestMixin
from datetimerange import DateTimeRange
from dateutil.rrule import *
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_naive, make_aware
from django.utils.translation import gettext as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView,
    FormView, TemplateView)
from django_select2.views import AutoResponseView
from django_weasyprint import WeasyTemplateResponseMixin
from nobinobi_child.models import Classroom, Child, Absence, Period, ChildToPeriod, ClassroomDayOff
from nobinobi_core.models import Holiday, OrganisationClosure
from notifications.models import Notification
from notifications.settings import get_config
from notifications.utils import id2slug
from notifications.views import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_datatables.renderers import DatatablesRenderer

from nobinobi_daily_follow_up.forms import PresenceChoiceForm, ReceptionForm, MealDailyFollowUpForm, NapForm, \
    LotionDailyFollowUpForm, DiaperChangeForm, ActivityForm, MedicationForm, DailyFollowUpForm, PresenceCreateForm, \
    PresenceDepartureForm, ChoiceClassroomForm, ChoiceChildDateForm, GroupActivityForm, GroupDailyFollowUpForm, \
    GiveMedicationForm, GiveMedicationDelayForm, DailyFollowUpToMedicationForm, MultiDayMedicationForm, \
    EarlyTroubleshootingForm, PresenceintermediateDepartureForm
from nobinobi_daily_follow_up.models import (
    Presence,
    Activity,
    TypeActivity,
    Nap,
    DailyFollowUp,
    LotionDailyFollowUp,
    DiaperChange,
    Lotion,
    Medication,
    TypeMedication,
    Reception,
    GiveMedication,
    MealDailyFollowUp,
    Meal,
    ActivityGroup, DailyFollowUpToMedication, EarlyTroubleshooting)
from nobinobi_daily_follow_up.serializers import PresenceSerializer, EarlyTroubleshootingSerializer
from nobinobi_daily_follow_up.utils import get_display_age_group_in_presence


class PresenceChoiceView(LoginRequiredMixin, FormView):
    form_class = PresenceChoiceForm
    template_name = "nobinobi_daily_follow_up/presence_choice.html"

    def get_context_data(self, **kwargs):
        context = super(PresenceChoiceView, self).get_context_data()
        context['title'] = _("Choice a classroom")
        return context

    def form_valid(self, form):
        pk = form.cleaned_data['classroom'].pk
        return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:Presence_detail_list", kwargs={"pk": pk}))


class PresenceCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Presence
    form_class = PresenceCreateForm
    template_name = 'nobinobi_daily_follow_up/presence/presence_create.html'
    success_message = _('Success: Presence was created.')

    def get_form_kwargs(self):
        kwargs = super(PresenceCreateView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        kwargs['classroom'] = Classroom.objects.get(pk=self.kwargs.get("pk"))
        kwargs['date'] = timezone.localtime().date()
        kwargs['child_pk'] = self.kwargs.pop("child_pk", None)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PresenceCreateView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(pk=self.kwargs.get("pk"))
        context['date'] = timezone.now().date()
        context['child_pk'] = self.kwargs.pop("child_pk", None)
        return context

    def get_success_url(self):
        url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": self.kwargs.get("pk")})
        return url


class PresenceDepartureView(LoginRequiredMixin, BSModalUpdateView):
    model = Presence
    form_class = PresenceDepartureForm
    template_name = 'nobinobi_daily_follow_up/presence/presence_update.html'
    success_message = _('Success: Presence was updated.')
    pk_url_kwarg = "presence_pk"

    def get_form_kwargs(self):
        kwargs = super(PresenceDepartureView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        kwargs['classroom'] = Classroom.objects.get(pk=self.kwargs.get("pk"))
        kwargs['date'] = timezone.localtime().date()
        kwargs['obj'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PresenceDepartureView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(pk=self.kwargs.get("pk"))
        context['date'] = timezone.localtime().date()
        return context

    def get_success_url(self):
        classroom = self.kwargs.get("pk")
        child = self.object.child_id
        date = self.object.date
        classroom_id_now = self.object.child.get_now_classroom(date).id
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom_id_now})
        return url


class PresenceIntermediateDepartureView(LoginRequiredMixin, BSModalUpdateView):
    model = Presence
    form_class = PresenceintermediateDepartureForm
    template_name = 'nobinobi_daily_follow_up/presence/presence_update.html'
    success_message = _('Success: Presence was updated.')
    pk_url_kwarg = "presence_pk"

    def get_form_kwargs(self):
        kwargs = super(PresenceIntermediateDepartureView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        kwargs['classroom'] = Classroom.objects.get(pk=self.kwargs.get("pk"))
        kwargs['date'] = timezone.localtime().date()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PresenceIntermediateDepartureView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(pk=self.kwargs.get("pk"))
        context['date'] = timezone.localtime().date()
        return context

    def get_success_url(self):
        classroom = self.kwargs.get("pk")
        child = self.object.child_id
        date = self.object.date
        classroom_id_now = self.object.child.get_now_classroom(date).id
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom_id_now})
        return url


class PresenceDeleteView(LoginRequiredMixin, DeleteView):
    model = Presence


class PresenceDetailView(LoginRequiredMixin, DetailView):
    model = Presence


class PresenceDetailListView(LoginRequiredMixin, ListView):
    template_name = "nobinobi_daily_follow_up/presence_detail_list.html"

    def get_queryset(self):
        return Presence.objects.filter(classroom=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(PresenceDetailListView, self).get_context_data(**kwargs)
        now = timezone.localtime()
        context['display_age_group_in_presence'] = get_display_age_group_in_presence()
        context['now'] = now.date()
        context['classroom'] = get_object_or_404(Classroom, pk=self.kwargs['pk'])
        context['child_in_classroom'] = self.get_list_children(context['classroom'], now)
        context['status_children'], context['children'] = self.get_status_children(context['classroom'],
                                                                                   context['child_in_classroom'])
        context['presence_day_sorting'] = getattr(settings, "PRESENCE_DAY_SORTING", "usual_name")

        context['title'] = _("Presence of the day")
        return context

    def get_list_children(self, classroom, now: datetime.datetime):
        """
        Function return two dict for list children
        :type now: timezone.localtime()
        :type classroom: Classroom
        """

        childs = Child.objects.filter(
            Q(classroom=classroom) |
            (Q(replacementclassroom__classroom=classroom) & Q(
                replacementclassroom__from_date__lte=now.date()) & (
                 Q(replacementclassroom__end_date__gte=now.date()) | Q(
                 replacementclassroom__end_date__isnull=True))),
            status=Child.STATUS.in_progress,
            childtoperiod__start_date__lte=now.date(),
            childtoperiod__end_date__gte=now.date(),
            childtoperiod__period__start_time__lte=now.time(),
            childtoperiod__period__end_time__gte=now.time(),
            childtoperiod__period__weekday=now.isoweekday()
        )
        # get child normaly present on date and time
        children_normaly = list(childs)

        for child in childs:
            if child.has_replacement_classroom(now.date()):
                if child.classroom == classroom:
                    children_normaly.remove(child)

        # ).distinct("first_name", "last_name"))
        # children_troubleshooting =
        children_missing = [abs.child for abs in
                            Absence.objects.filter(
                                Q(child__classroom=classroom) |
                                (Q(child__replacementclassroom__classroom=classroom) & Q(
                                    child__replacementclassroom__from_date__lte=now.date()) & (
                                     Q(child__replacementclassroom__end_date__gte=now.date()) | Q(
                                     child__replacementclassroom__end_date__isnull=True))),
                                start_date__date__lte=now.date(),
                                end_date__date__gte=now.date())
                            ]

        for child in children_missing:
            if child.has_replacement_classroom(now.date()):
                if child.classroom == classroom:
                    children_missing.remove(child)

        if classroom.mode == Classroom.OPERATION_MODE.creche:
            children_present = [pres.child for pres in Presence.objects.filter(classroom=classroom, date=now.date())]
        else:
            # jardin d'enfant
            children_present = []
            presences_in_classroom = filter_presence_by_range_arrival_departure(now, now.date(), classroom.id)
            for pres in presences_in_classroom:
                children_present.append(pres.child)

        children_list = []
        for child in children_normaly:
            if child not in children_list:
                children_list.append(child)
        for child in children_missing:
            if child in children_normaly:
                if child not in children_list:
                    children_list.append(child)
        for child in children_present:
            if child not in children_list:
                children_list.append(child)
        presence_day_sorting = getattr(settings, 'PRESENCE_DAY_SORTING', "usual_name")
        if presence_day_sorting == "birth_date":
            sorted_children_list = sorted(children_list,
                                          key=lambda x: x.birth_date if x.birth_date else datetime.date(2020, 1, 1),
                                          reverse=True)
        else:
            sorted_children_list = sorted(children_list, key=lambda x: x.usual_name)
        return sorted_children_list

    def get_status_children(self, classroom, children_in_classroom, *date):
        """
        Function to get status of children in dict
        :param classroom:
        :param children_in_classroom:
        :param date:
        :return:
        """
        children = {"present": [], "missing": [], "expected": [], "troubleshooting": [], "leave": []}
        status_children = {"present": 0, "missing": 0, "expected": 0, "troubleshooting": 0}
        if not date:
            now = timezone.localtime()
        else:
            now = arrow.get(date)

        presences = Presence.objects.filter(date=now.date(), classroom=classroom)

        # present
        presences_with_arrival = presences.filter(arrival_time__isnull=False, departure_time__isnull=True)
        presences_with_departure = presences.filter(arrival_time__isnull=False, departure_time__isnull=False)

        children['present'] = list(presences_with_arrival.values_list("child", flat=True))
        children['leave'] = list(presences_with_departure.values_list("child", flat=True))
        status_children['present'] = presences_with_arrival.count()
        status_children['present'] = presences_with_arrival.count()

        # expected
        expected = []
        children_missing = {abs.child_id: abs.child for abs in
                            Absence.objects.filter(
                                Q(child__classroom=classroom) |
                                (Q(child__replacementclassroom__classroom=classroom) & Q(
                                    child__replacementclassroom__from_date__lte=now.date()) & (
                                     Q(child__replacementclassroom__end_date__gte=now.date()) | Q(
                                     child__replacementclassroom__end_date__isnull=True))),
                                start_date__date__lte=now,
                                end_date__date__gte=now)
                            }

        child_to_remove = []
        for child_id, child in children_missing.items():
            if child.has_replacement_classroom(now.date()):
                if child.classroom == classroom:
                    child_to_remove.append(child)
        for child in child_to_remove:
            del children_missing[child.id]

        for child in children_in_classroom:
            periods = child.childtoperiod_set.all()
            weekday = now.isoweekday()
            if periods:
                for period in periods:
                    if period.start_date <= now.date() <= period.end_date:
                        if period.period.weekday == weekday:
                            if child.id not in expected:
                                if child.id not in children_missing:
                                    if child.id not in children['present']:
                                        if child.id not in children['leave']:
                                            expected.append(child.id)
        children['expected'] = expected
        status_children['expected'] = len(expected)

        # troubleshooting
        troubleshooting = []
        for presence in presences_with_arrival:
            try:
                presence.dailyfollowup.troubleshooting
                # for period in presence.dailyfollowup.troubleshooting.periods.filter(period__weekday=weekday):
                if presence.child_id not in troubleshooting:
                    troubleshooting.append(presence.child_id)
            except DailyFollowUp.troubleshooting.RelatedObjectDoesNotExist:
                pass
        children['troubleshooting'] = troubleshooting
        status_children['troubleshooting'] = len(troubleshooting)

        # absence
        missing = []
        # absences = Absence.objects.filter(start_date__lte=now, end_date__gte=now, child__classroom=classroom)
        for child_id, child in children_missing.items():
            if child_id not in children['expected']:
                if child_id not in children['troubleshooting']:
                    if child_id not in children['present']:
                        if child_id not in children['leave']:
                            missing.append(child_id)
        children['missing'] = missing
        status_children['missing'] = len(missing)

        # remove from present if kindergarten when child leave intermediary
        if classroom.mode == Classroom.OPERATION_MODE.kindergarten:
            leaves_intermediary = presences_with_arrival.filter(intermediate_departure_time__isnull=False,
                                                                intermediate_arrival_time__isnull=True)
            for pres in leaves_intermediary:
                status_children['present'] -= 1
                children['present'].remove(pres.child_id)

        return status_children, children


class PresenceUpdateView(LoginRequiredMixin, UpdateView):
    model = Presence


class PresenceListView(LoginRequiredMixin, ListView):
    model = Presence


def filter_presence_by_range_arrival_departure(now, date, classroom_id):
    now_datetimerange = DateTimeRange(make_naive(now), make_naive(now))
    periods = list(
        Period.objects.filter(weekday__exact=now.isoweekday()).values_list("start_time", "end_time").order_by(
            "order"))
    hour = None
    for period in periods:
        start_datetime = datetime.datetime.combine(now, period[0])
        end_datetime = datetime.datetime.combine(now, period[1])
        period_datetimerange = DateTimeRange(start_datetime, end_datetime)
        if now_datetimerange.is_intersection(period_datetimerange):
            hour0 = period[0]
            hour1 = period[1]

    presence_day_sorting = getattr(settings, "PRESENCE_DAY_SORTING", "usual_name")
    qs_order = "child__usual_name"
    if presence_day_sorting == "birth_date":
        qs_order = "-child__birth_date"
    presences_in_classroom = Presence.objects.filter(date=date, classroom_id=classroom_id)

    presences_in_classroom = presences_in_classroom.filter(
        Q(arrival_time__lte=hour0) & Q(departure_time__isnull=True) | Q(arrival_time__gte=hour0) | Q(
            arrival_time__lte=hour0) & Q(departure_time__gte=hour0))
    presences_in_classroom = presences_in_classroom.filter(
        Q(departure_time__lte=hour1) | Q(departure_time__isnull=True))

    return presences_in_classroom.order_by(qs_order)


class PresenceViewSet(viewsets.ModelViewSet):
    serializer_class = PresenceSerializer

    def get_queryset(self):
        presence_day_sorting = getattr(settings, "PRESENCE_DAY_SORTING", "usual_name")
        qs_order = "child__usual_name"
        if presence_day_sorting == "birth_date":
            qs_order = "-child__birth_date"
        return Presence.objects.filter(date=timezone.now().date()).order_by(qs_order)

    @action(detail=False, methods=['GET'])
    def presence_by_weeks(self, request, **kwargs):
        recent_presence_in_weeks = Presence.objects.filter(date__gte=kwargs.get("from_date"),
                                                           date__lte=kwargs.get("end_date")).order_by("date")

        page = self.paginate_queryset(recent_presence_in_weeks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_presence_in_weeks, many=True)
        return Response(serializer.data)

    @action(detail=False, renderer_classes=[DatatablesRenderer])
    def presence_by_classroom(self, request, **kwargs):
        presence_day_sorting = getattr(settings, "PRESENCE_DAY_SORTING", "usual_name")
        qs_order = "child__usual_name"
        if presence_day_sorting == "birth_date":
            qs_order = "-child__birth_date"
        presences_in_classroom = Presence.objects.filter(date=kwargs.get("date"),
                                                         classroom_id=kwargs.get("classroom_id")).order_by(qs_order)

        # page = self.paginate_queryset(presences_in_classroom)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(presences_in_classroom, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def presence_by_weeks_and_child(self, request, **kwargs):
        recent_presence_in_weeks = Presence.objects.filter(child_id=kwargs.get("child_pk"),
                                                           date__gte=kwargs.get("from_date"),
                                                           date__lte=kwargs.get("end_date")).order_by("date")

        page = self.paginate_queryset(recent_presence_in_weeks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_presence_in_weeks, many=True)
        return Response(serializer.data)


class PresenceClassroomDateViewSet(viewsets.ModelViewSet):
    serializer_class = PresenceSerializer

    def get_queryset(self):
        presence_day_sorting = getattr(settings, "PRESENCE_DAY_SORTING", "usual_name")
        qs_order = "child__usual_name"
        if presence_day_sorting == "birth_date":
            qs_order = "-child__birth_date"
        return Presence.objects.filter(date=self.kwargs.get("date"),
                                       classroom_id=self.kwargs.get("classroom_id")).order_by(qs_order)


class PresenceKindergartenClassroomDateViewSet(viewsets.ModelViewSet):
    serializer_class = PresenceSerializer

    def get_queryset(self):
        now = timezone.localtime()
        date = self.kwargs.get("date")
        classroom_id = self.kwargs.get("classroom_id")
        now_datetimerange = DateTimeRange(make_naive(now), make_naive(now))
        periods = list(
            Period.objects.filter(weekday__exact=now.isoweekday()).values_list("start_time", "end_time").order_by(
                "order"))
        hour0 = None
        hour1 = None

        presence_day_sorting = getattr(settings, "PRESENCE_DAY_SORTING", "usual_name")
        qs_order = "child__usual_name"
        if presence_day_sorting == "birth_date":
            qs_order = "-child__birth_date"

        for period in periods:
            start_datetime = datetime.datetime.combine(now, period[0])
            end_datetime = datetime.datetime.combine(now, period[1])
            period_datetimerange = DateTimeRange(start_datetime, end_datetime)
            if now_datetimerange.is_intersection(period_datetimerange):
                hour0 = period[0]
                hour1 = period[1]

        presences_in_classroom = Presence.objects.filter(date=date, classroom_id=classroom_id)
        if hour0 is not None:
            presences_in_classroom = presences_in_classroom.filter(
                Q(arrival_time__lte=hour0) & Q(departure_time__isnull=True) | Q(arrival_time__gte=hour0) | Q(
                    arrival_time__lte=hour0) & Q(departure_time__gte=hour0))
        if hour1 is not None:
            presences_in_classroom = presences_in_classroom.filter(
                Q(departure_time__lte=hour1) | Q(departure_time__isnull=True))

        return presences_in_classroom.order_by(qs_order)


class PresenceWeekListChoiceView(LoginRequiredMixin, FormView):
    """Choice View for display presence for all children for a week"""
    template_name = "nobinobi_daily_follow_up/presence/presence_choice_classroom.html"
    form_class = ChoiceClassroomForm
    classroom = None

    def get(self, request, *args, **kwargs):
        """ redirect auto si un seul groupe"""
        try:
            allowed_classroom = Classroom.objects.get(allowed_login=request.user)
        except Classroom.MultipleObjectsReturned:
            pass
        except Classroom.DoesNotExist:
            pass
        else:
            self.classroom = allowed_classroom
            return HttpResponseRedirect(self.get_success_url())
        return super(PresenceWeekListChoiceView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PresenceWeekListChoiceView, self).get_form_kwargs()
        userid = self.request.user.id
        kwargs.update(userid=userid)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PresenceWeekListChoiceView, self).get_context_data(**kwargs)
        context["title"] = _("Classroom choice for presence week list")
        return context

    def form_valid(self, form):
        self.classroom = form.cleaned_data['id']
        return super(PresenceWeekListChoiceView, self).form_valid(form)

    def get_success_url(self):
        if self.classroom.mode == Classroom.OPERATION_MODE.creche:
            return reverse("nobinobi_daily_follow_up:presence_week_list", kwargs={"classroom_id": self.classroom.pk})
        elif self.classroom.mode == Classroom.OPERATION_MODE.kindergarten:
            return reverse("nobinobi_daily_follow_up:presence_week_kindergarten_list",
                           kwargs={"classroom_id": self.classroom.pk})


class PresenceWeekListView(LoginRequiredMixin, TemplateView):
    """View for display presence for all children for a week"""
    model = Presence
    template_name = "nobinobi_daily_follow_up/presence/presence_week_list.html"

    def get_context_data(self, **kwargs):
        context = super(PresenceWeekListView, self).get_context_data(**kwargs)
        now = self.kwargs.get("date", timezone.localtime())
        context['now'] = arrow.get(now)
        context['today'] = timezone.localtime()
        context['display_age_group_in_presence'] = get_display_age_group_in_presence()
        first_last_day_week = arrow.get(now).span('week')

        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]
        context['month_before'] = arrow.get(week_dates[0]).shift(months=-1)
        context['week_before'] = arrow.get(week_dates[0]).shift(weeks=-1)
        context['week_after'] = arrow.get(week_dates[-1]).shift(weeks=+1)
        context['month_after'] = arrow.get(week_dates[-1]).shift(months=+1)
        context['classroom'] = get_object_or_404(Classroom, id=kwargs.get("classroom_id"))
        context['title'] = _("Presence week list")
        context['dict_table_child'], context['dict_table'], errors = self.create_dict_table_child(
            request=self.request,
            classroom=context['classroom'],
            date_received=context['now'],
            dict_table=self.create_dict_table(context['now'], context['classroom']))
        for error in errors:
            messages.error(self.request, error)
        return context

    @staticmethod
    def create_dict_table(today, classroom):
        """
        Function to create dict for page presence week list
        """
        # create dict
        dict = {}
        # append day
        today = today
        # get first and last day from week
        first_last_day_week = arrow.get(today).span('week')
        # Business days list
        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]
        classroom_dayoffs = ClassroomDayOff.objects.filter(classrooms__id__exact=classroom.id).values_list(
            "weekday",
            flat=True)
        # add in dict day
        periods = list(Period.objects.all().order_by("order"))
        for week_date in week_dates:
            dict[week_date.date().isoweekday()] = {
                "datetime": week_date,
                "periods": {}
            }
            # add in dict period
            if periods:
                for period in periods:
                    if period.weekday == week_date.date().isoweekday():
                        dict[week_date.date().isoweekday()]["periods"][period.order] = {
                            "name": period.name,
                            "start_time": period.start_time,
                            "end_time": period.end_time,
                            "expected": 0,
                            "present": 0,
                            "dayoff": False,
                        }
                        ctps_qs = ChildToPeriod.objects.filter(
                            Q(child__classroom=classroom) |
                            (Q(child__replacementclassroom__classroom=classroom) & Q(
                                child__replacementclassroom__from_date__lte=week_date.date()) & (
                                 Q(child__replacementclassroom__end_date__gte=week_date.date()) | Q(
                                 child__replacementclassroom__end_date__isnull=True))),
                            child__status=Child.STATUS.in_progress,
                            start_date__lte=week_date.date(),
                            end_date__gte=week_date.date(),
                            period=period
                        ).distinct()
                        ctps = []
                        for ctp in ctps_qs:
                            if ctp.child.get_now_classroom(date=week_date.date()) == classroom:
                                ctps.append(ctp)

                        dict[week_date.date().isoweekday()]["periods"][period.order]['expected'] = len(ctps)
                        # day off
                        if week_date.isoweekday() in classroom_dayoffs:
                            dict[week_date.date().isoweekday()]["periods"][period.order]['dayoff'] = True
        return dict

    @staticmethod
    def create_dict_table_child(request, classroom, date_received, dict_table):
        dict_children = {}
        errors = []
        # get first and last day from week
        first_last_day_week = arrow.get(date_received).span('week')
        # Business days list
        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]

        # Holiday
        holidays = Holiday.objects.filter(date__in=week_dates).values_list("date", flat=True)
        # closures
        closures_dates = []
        try:
            closures = OrganisationClosure.objects.filter(from_date__lte=week_dates[-1],
                                                          end_date__gte=week_dates[0],
                                                          organisation_id=classroom.organisation.id)
        except AttributeError:
            messages.warning(request, _(
                "You have not entered an organization for this classroom, "
                "institutional closures will not be taken into account."))
        else:
            for closure in closures:
                for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                               dtstart=closure.from_date,
                               until=closure.end_date):
                    closures_dates.append(r.date())

        classroom_dayoffs = ClassroomDayOff.objects.filter(classrooms__id__exact=classroom.id).values_list(
            "weekday",
            flat=True)
        periods = Period.objects.all().order_by("order")
        period_for_day = list(periods.values("id", "weekday", 'order', 'type').order_by("order"))
        presence_day_sorting = getattr(settings, 'PRESENCE_DAY_SORTING', "child__usual_name")
        # on set le reverse pour la requete
        if presence_day_sorting == "birth_date":
            presence_day_sorting = "-child__birth_date"
        elif presence_day_sorting == "usual_name":
            presence_day_sorting = "child__usual_name"
        children = ChildToPeriod.objects.filter(
            Q(child__classroom=classroom) |
            (Q(child__replacementclassroom__classroom=classroom) & Q(
                child__replacementclassroom__from_date__lte=week_dates[-1].date()) & (
                 Q(child__replacementclassroom__end_date__gte=week_dates[0].date()) | Q(
                 child__replacementclassroom__end_date__isnull=True))),
            start_date__lte=week_dates[-1].date(),
            end_date__gte=week_dates[0].date(),
            child__status=Child.STATUS.in_progress
        ).order_by(presence_day_sorting)

        for ctp in children:
            PresenceWeekListView.create_dict_struct_for_child(classroom_dayoffs, ctp, dict_children, period_for_day,
                                                              week_dates, holidays, closures_dates)

        # get absence
        week_dates_date = [d.date() for d in week_dates]

        # get expected child
        for week_date in week_dates:
            # period_for_day = list(periods.filter(weekday=week_date.isoweekday()).order_by("order"))
            period_for_day_list = {period["id"]: period['order'] for period in period_for_day if
                                   period['weekday'] == week_date.isoweekday()}
            for period_id, period_order in period_for_day_list.items():
                # children_expected = list(children.filter(childtoperiod__period_id=period_id,
                #                                          childtoperiod__start_date__lte=week_date.date(),
                #                                          childtoperiod__end_date__gte=week_date.date()))
                children_expected = list(
                    ChildToPeriod.objects.filter(period_id=period_id, start_date__lte=week_date.date(),
                                                 end_date__gte=week_date.date(), child__in=list(dict_children)))

                if children_expected:
                    for child_to_period in children_expected:
                        if child_to_period.child.get_now_classroom(date=week_date.date()) == classroom:
                            dict_children[child_to_period.child][week_date.isoweekday()]["periods"][period_order][
                                'status'] = "expected"
                        else:
                            dict_children[child_to_period.child][week_date.isoweekday()]["periods"][period_order][
                                'status'] = "replacement_classroom"
                        if child_to_period.child.has_replacement_classroom(week_date.date()):
                            dict_children[child_to_period.child][week_date.isoweekday()]["periods"][period_order][
                                'replacement_classroom'] = True

        absences = Absence.objects.filter(
            child__classroom=classroom,
            child__status=Child.STATUS.in_progress,
            start_date__lte=datetime.datetime.combine(week_dates_date[-1], datetime.time(23, 59)),
            end_date__gte=datetime.datetime.combine(week_dates_date[0], datetime.time(0)),
        )
        absences_list = []
        for absence in absences:
            absences_list.append(absence)

        for absence in absences_list:
            if absence.child.classroom == classroom:
                try:
                    dict_children[absence.child]
                except KeyError:
                    pass
                else:
                    if make_naive(absence.start_date) > make_naive(absence.end_date):
                        errors.append(_("The absence {} has a start date after the end date.").format(absence))
                    else:
                        # absence.start_date = absence.start_date.to("")
                        # create range absence date_received
                        time_range_absence = DateTimeRange(make_naive(absence.start_date),
                                                           make_naive(absence.end_date))
                        # get period from day child
                        for date_absence in time_range_absence.range(datetime.timedelta(days=1)):
                            if date_absence.date() in week_dates_date:
                                periods_child = absence.child.periods.filter(weekday=date_absence.isoweekday())
                                for period in periods_child:
                                    # create time range of period
                                    start_date = datetime.datetime.combine(date_absence, period.start_time)
                                    end_date = datetime.datetime.combine(date_absence, period.end_time)
                                    time_range_period = DateTimeRange(start_date, end_date)

                                    # if time range period is in time range absence
                                    if time_range_absence.is_intersection(time_range_period):
                                        # for date_received in time_range_absence.range(datetime.timedelta(days=1)):
                                        # set information in dict
                                        if date_absence.isoweekday() not in [6, 7]:
                                            if not \
                                                dict_children[absence.child][date_absence.isoweekday()]["periods"][
                                                    period.order][
                                                    "status"] == "absence":
                                                if dict_children[absence.child][date_absence.isoweekday()]["periods"][
                                                    period.order][
                                                    "status"] == "expected":
                                                    dict_table[date_absence.isoweekday()]["periods"][period.order][
                                                        'expected'] -= 1

                                                dict_children[absence.child][date_absence.isoweekday()]["periods"][
                                                    period.order][
                                                    "absence"] = absence
                                                dict_children[absence.child][date_absence.isoweekday()]["periods"][
                                                    period.order]["status"] = "absence"

        # early troubleshooting
        early_troubleshootings = EarlyTroubleshooting.objects.filter(date__gte=week_dates_date[0],
                                                                     date__lte=week_dates_date[-1],
                                                                     child__classroom=classroom)
        for et in early_troubleshootings:
            for per in et.periods.all():
                dict_children[et.child][et.date.isoweekday()]["periods"][per.order][
                    'status'] = "troubleshooting"
                dict_children[et.child][et.date.isoweekday()]["periods"][per.order][
                    'troubleshooting'] = True
                dict_table[et.date.isoweekday()]["periods"][per.order]['expected'] += 1

        # get child present
        children_present = Presence.objects.filter(date__in=week_dates, arrival_time__isnull=False, classroom=classroom)
        children_leave = children_present.filter(departure_time__isnull=False)

        # troubleshooting
        troubleshooting = []
        for presence in children_present:
            try:
                presence.dailyfollowup.troubleshooting
                # for period in presence.dailyfollowup.troubleshooting.periods.filter(period__weekday=weekday):
                if presence not in troubleshooting:
                    troubleshooting.append(presence)
            except DailyFollowUp.troubleshooting.RelatedObjectDoesNotExist:
                pass

        for ts in troubleshooting:
            # on creer le dict
            PresenceWeekListView.create_dict_struct_for_child(classroom_dayoffs, ts, dict_children, period_for_day,
                                                              week_dates, holidays, closures_dates)

            child_period = ts.dailyfollowup.troubleshooting.periods.all()
            for period in child_period:
                # create time range of period
                start_date = datetime.datetime.combine(ts.date, period.start_time)
                end_date = datetime.datetime.combine(ts.date, period.end_time)
                time_range_period = DateTimeRange(start_date, end_date)
                now = make_naive(timezone.localtime())
                if datetime.datetime.combine(ts.date, ts.arrival_time) in time_range_period or now in time_range_period:
                    # set information in dict_children
                    dict_children[ts.child][ts.date.isoweekday()]["periods"][period.order]["status"] = "troubleshooting"
                    dict_children[ts.child][ts.date.isoweekday()]["periods"][period.order]["troubleshooting"] = True
                    dict_table[ts.date.isoweekday()]["periods"][period.order]['present'] += 1

        for presence in children_present:
            PresenceWeekListView.create_dict_struct_for_child(classroom_dayoffs, presence, dict_children,
                                                              period_for_day,
                                                              week_dates, holidays, closures_dates)
            child_period = presence.child.periods.filter(weekday=presence.date.isoweekday())
            for period in child_period:
                # create time range of period
                start_date = make_aware(datetime.datetime.combine(presence.date, period.start_time))
                end_date = make_aware(datetime.datetime.combine(presence.date, period.end_time))
                time_range_period = DateTimeRange(start_date, end_date)
                start_date_presence = make_aware(datetime.datetime.combine(presence.date, presence.arrival_time))
                time_range_arrival_now = DateTimeRange(start_date_presence, timezone.localtime())
                if time_range_period.is_intersection(time_range_arrival_now):
                    # set information in dict_children
                    if dict_children[presence.child][presence.date.isoweekday()]["periods"][period.order][
                        "status"] == "expected":
                        dict_children[presence.child][presence.date.isoweekday()]["periods"][period.order][
                            "status"] = "present"
                        dict_table[presence.date.isoweekday()]["periods"][period.order]['expected'] -= 1
                        dict_table[presence.date.isoweekday()]["periods"][period.order]['present'] += 1
        for presence in children_leave:
            try:
                periods_list = []
                presence.dailyfollowup.troubleshooting
                child_period = presence.dailyfollowup.troubleshooting.periods.filter(weekday=presence.date.isoweekday())
                for period in child_period:
                    periods_list.append(period)
                child_period_normal = presence.child.periods.filter(weekday=presence.date.isoweekday())
                for period in child_period_normal:
                    if period not in periods_list:
                        periods_list.append(period)
            except DailyFollowUp.troubleshooting.RelatedObjectDoesNotExist:
                periods_list = presence.child.periods.filter(weekday=presence.date.isoweekday())

            for period in periods_list:
                # create time range of period
                start_date = make_aware(datetime.datetime.combine(presence.date, period.start_time))
                end_date = make_aware(datetime.datetime.combine(presence.date, period.end_time))
                time_range_period = DateTimeRange(start_date, end_date)
                start_date_presence = make_aware(datetime.datetime.combine(presence.date, presence.arrival_time))
                end_date_presence = make_aware(datetime.datetime.combine(presence.date, presence.departure_time))
                time_range_arrival_now = DateTimeRange(start_date_presence, end_date_presence)
                if time_range_period.is_intersection(time_range_arrival_now):
                    # set information in dict_children
                    if dict_children[presence.child][presence.date.isoweekday()]["periods"][period.order][
                        "status"] in ["present", "troubleshooting"]:
                        dict_children[presence.child][presence.date.isoweekday()]["periods"][period.order][
                            "status"] = "leave"
                        # dict_table[presence.date.isoweekday()]["periods"][period.order]['expected'] -= 1
                        dict_table[presence.date.isoweekday()]["periods"][period.order]['present'] -= 1

        return dict_children, dict_table, errors

    @staticmethod
    def create_dict_struct_for_child(classroom_dayoffs, child, dict_children, period_for_day, week_dates, holidays,
                                     closures_dates):
        if child.child not in dict_children:
            dict_children[child.child] = {}

            # add in dict day
            for week_date in week_dates:
                dict_children[child.child][week_date.isoweekday()] = {
                    "datetime": week_date,
                    "periods": {}
                }
                # period_for_day = periods.filter(weekday=week_date.isoweekday()).order_by("order")
                period_for_day_list = {period["id"]: period['order'] for period in period_for_day if
                                       period['weekday'] == week_date.isoweekday()}
                for period_id, period_order in period_for_day_list.items():
                    #
                    # for period in period_for_day:
                    if period_order not in dict_children[child.child][week_date.isoweekday()]["periods"]:
                        dict_children[child.child][week_date.isoweekday()]["periods"][period_order] = {
                            "status": "",
                            "troubleshooting": None,
                            "absence": None,
                            "dayoff": False,
                            "holiday": False,
                            "closure": False,
                            "birthday": False,
                            "replacement_classroom": None,
                        }

                    # Holidays
                    if week_date.date() in holidays:
                        dict_children[child.child][week_date.isoweekday()]["periods"][period_order]["holiday"] = True
                    # Closures
                    if week_date.date() in closures_dates:
                        dict_children[child.child][week_date.isoweekday()]["periods"][period_order]["closure"] = True

                    if week_date.isoweekday() in classroom_dayoffs:
                        dict_children[child.child][week_date.isoweekday()]["periods"][period_order]["dayoff"] = True
                    # birthday
                    if child.child.birth_date:
                        if week_date.date().day == child.child.birth_date.day and week_date.date().month == child.child.birth_date.month:
                            dict_children[child.child][week_date.isoweekday()]["periods"][period_order][
                                "birthday"] = True


class AdminPresenceWeekListView(LoginRequiredMixin, TemplateView):
    """View for display presence for all children for a week"""
    model = Presence
    template_name = "nobinobi_daily_follow_up/presence/admin_presence_week_list.html"

    def get_context_data(self, **kwargs):
        context = super(AdminPresenceWeekListView, self).get_context_data(**kwargs)
        now = self.kwargs.get("date", timezone.localtime())
        context['now'] = arrow.get(now)
        context['today'] = timezone.localtime()
        context['display_age_group_in_presence'] = get_display_age_group_in_presence()
        first_last_day_week = arrow.get(now).span('week')

        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]
        context['month_before'] = arrow.get(week_dates[0]).shift(months=-1)
        context['week_before'] = arrow.get(week_dates[0]).shift(weeks=-1)
        context['week_after'] = arrow.get(week_dates[-1]).shift(weeks=+1)
        context['month_after'] = arrow.get(week_dates[-1]).shift(months=+1)
        context['classrooms'] = Classroom.objects.all()
        context['title'] = _("Admin Presence week list")
        dict_classrooms = {}
        for classroom in context['classrooms']:
            if classroom.mode == Classroom.OPERATION_MODE.creche:
                dict_table_child, dict_table, errors_creche = PresenceWeekListView.create_dict_table_child(
                    request=self.request,
                    classroom=classroom,
                    date_received=context['now'],
                    dict_table=PresenceWeekListView.create_dict_table(context['now'], classroom))
                for error in errors_creche:
                    messages.error(self.request, error)

            elif classroom.mode == Classroom.OPERATION_MODE.kindergarten:
                dict_table_child, dict_table, errors_kindergarten = PresenceWeekKinderGartenListView.create_dict_table_child(
                    request=self.request,
                    classroom=classroom,
                    date_received=context['now'],
                    dict_table=PresenceWeekKinderGartenListView.create_dict_table(context['now'], classroom))
                for error in errors_kindergarten:
                    messages.error(self.request, error)

            dict_classrooms[classroom] = {
                "dict_table_child": dict_table_child,
                "dict_table": dict_table,
                "type": classroom.mode,
            }
        context['dict_classrooms'] = dict_classrooms
        return context


class PresenceWeekKinderGartenListView(LoginRequiredMixin, TemplateView):
    """View for display presence for all children for a week"""
    model = Presence
    template_name = "nobinobi_daily_follow_up/presence/presence_week_kindergarten_list.html"

    def get_context_data(self, **kwargs):
        context = super(PresenceWeekKinderGartenListView, self).get_context_data(**kwargs)
        now = self.kwargs.get("date", timezone.localtime())
        context['now'] = arrow.get(now)
        context['today'] = timezone.localtime()
        context['display_age_group_in_presence'] = get_display_age_group_in_presence()
        first_last_day_week = arrow.get(now).span('week')

        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]
        context['month_before'] = arrow.get(week_dates[0]).shift(months=-1)
        context['week_before'] = arrow.get(week_dates[0]).shift(weeks=-1)
        context['week_after'] = arrow.get(week_dates[-1]).shift(weeks=+1)
        context['month_after'] = arrow.get(week_dates[-1]).shift(months=+1)
        context['classroom'] = get_object_or_404(Classroom, id=kwargs.get("classroom_id"))
        context['title'] = _("Presence week list")
        context['dict_table_child'], context['dict_table'], errors = self.create_dict_table_child(
            request=self.request,
            classroom=context['classroom'],
            date_received=context['now'],
            dict_table=self.create_dict_table(context['now'], context['classroom']))
        for error in errors:
            messages.error(self.request, error)

        return context

    @staticmethod
    def create_dict_table(today, classroom):
        """
        Function to create dict for page presence week list
        """
        # create dict
        dict = {}
        # append day
        today = today
        # get first and last day from week
        first_last_day_week = arrow.get(today).span('week')
        # Business days list
        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]
        classroom_dayoffs = ClassroomDayOff.objects.filter(classrooms__id__exact=classroom.id).values_list(
            "weekday",
            flat=True)
        # add in dict day
        periods = list(Period.objects.all().order_by("order"))
        for week_date in week_dates:
            dict[week_date.date().isoweekday()] = {
                "datetime": week_date,
                "periods": {}
            }
            # add in dict period
            if periods:
                for period in periods:
                    if period.weekday == week_date.date().isoweekday():
                        try:
                            dict[week_date.date().isoweekday()]["periods"][period.type]
                        except KeyError:
                            dict[week_date.date().isoweekday()]["periods"][period.type] = {}
                            try:
                                dict[week_date.date().isoweekday()]["periods"][period.type][period.order]
                            except KeyError:
                                dict[week_date.date().isoweekday()]["periods"][period.type][period.order] = {
                                    "name": period.name,
                                    "start_time": period.start_time,
                                    "end_time": period.end_time,
                                    "expected": 0,
                                    "present": 0,
                                    "dayoff": False,
                                }
                                ctps = ChildToPeriod.objects.filter(child__status=Child.STATUS.in_progress,
                                                                    start_date__lte=week_date.date(),
                                                                    end_date__gte=week_date.date(),
                                                                    period=period, child__classroom=classroom)
                                dict[week_date.date().isoweekday()]["periods"][period.type][period.order][
                                    'expected'] = ctps.count()
                                # day off
                                if week_date.isoweekday() in classroom_dayoffs:
                                    dict[week_date.date().isoweekday()]["periods"][period.type][period.order][
                                        'dayoff'] = True

        return dict

    @staticmethod
    def create_dict_table_child(request, classroom, date_received, dict_table):
        dict_children = {}
        errors = []
        # get first and last day from week
        first_last_day_week = arrow.get(date_received).span('week')
        # Business days list
        week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                       dtstart=first_last_day_week[0],
                                       until=first_last_day_week[-1])]
        # Holiday
        holidays = Holiday.objects.filter(date__in=week_dates).values_list("date", flat=True)
        # closures
        closures_dates = []
        try:
            closures = OrganisationClosure.objects.filter(from_date__lte=week_dates[-1],
                                                          end_date__gte=week_dates[0],
                                                          organisation_id=classroom.organisation.id)
        except AttributeError:
            messages.warning(request, _(
                "You have not entered an organization for this classroom, "
                "institutional closures will not be taken into account."))
        else:
            for closure in closures:
                for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                               dtstart=closure.from_date,
                               until=closure.end_date):
                    closures_dates.append(r.date())

        classroom_dayoffs = ClassroomDayOff.objects.filter(classrooms__id__exact=classroom.id).values_list(
            "weekday",
            flat=True)
        periods = Period.objects.all().order_by("order")
        period_for_day = list(periods.values("id", "weekday", 'order', 'type').order_by("order"))
        presence_day_sorting = getattr(settings, 'PRESENCE_DAY_SORTING', "child__usual_name")
        # on set le reverse pour la requete
        if presence_day_sorting == "birth_date":
            presence_day_sorting = "-child__birth_date"
        elif presence_day_sorting == "usual_name":
            presence_day_sorting = "child__usual_name"
        children = ChildToPeriod.objects.filter(child__classroom=classroom, start_date__lte=week_dates[-1].date(),
                                                end_date__gte=week_dates[0].date(),
                                                child__status=Child.STATUS.in_progress).order_by(presence_day_sorting)

        for ctp in children:
            PresenceWeekKinderGartenListView.create_dict_struct_for_child(classroom_dayoffs, ctp, dict_children,
                                                                          period_for_day,
                                                                          week_dates, holidays, closures_dates)
        # get absence
        week_dates_date = [d.date() for d in week_dates]

        # get expected child
        for week_date in week_dates:
            # period_for_day = list(periods.filter(weekday=week_date.isoweekday()).order_by("order"))
            period_for_day_list = {period["id"]: [period['order'], period['type']] for period in period_for_day
                                   if
                                   period['weekday'] == week_date.isoweekday()}
            for period_id, period_info in period_for_day_list.items():
                # children_expected = list(children.filter(childtoperiod__period_id=period_id,
                #                                          childtoperiod__start_date__lte=week_date.date(),
                #                                          childtoperiod__end_date__gte=week_date.date()))
                children_expected = list(
                    ChildToPeriod.objects.filter(period_id=period_id, start_date__lte=week_date.date(),
                                                 end_date__gte=week_date.date(), child__in=list(dict_children)))

                if children_expected:
                    for child_to_period in children_expected:
                        dict_children[child_to_period.child]["days"][week_date.isoweekday()]["periods"][period_info[1]][
                            period_info[0]][
                            'status'] = "expected"
                        dict_children[child_to_period.child]["type"][period_info[1]] = True

        absences = Absence.objects.filter(
            child__classroom=classroom,
            child__status=Child.STATUS.in_progress,
            start_date__lte=datetime.datetime.combine(week_dates_date[-1], datetime.time(23, 59)),
            end_date__gte=datetime.datetime.combine(week_dates_date[0], datetime.time(0)),
        )
        absences_list = []
        for absence in absences:
            absences_list.append(absence)

        for absence in absences_list:
            if absence.child.classroom == classroom:
                try:
                    dict_children[absence.child]
                except KeyError:
                    pass
                else:
                    if make_naive(absence.start_date) > make_naive(absence.end_date):
                        errors.append(_("The absence {} has a start date after the end date.").format(absence))
                    else:
                        # absence.start_date = absence.start_date.to("")
                        # create range absence date_received
                        time_range_absence = DateTimeRange(make_naive(absence.start_date),
                                                           make_naive(absence.end_date))
                        # get period from day child
                        for date_absence in time_range_absence.range(datetime.timedelta(days=1)):
                            if date_absence.date() in week_dates_date:
                                periods_child = absence.child.periods.filter(weekday=date_absence.isoweekday())
                                for period in periods_child:
                                    # create time range of period
                                    start_date = datetime.datetime.combine(date_absence, period.start_time)
                                    end_date = datetime.datetime.combine(date_absence, period.end_time)
                                    time_range_period = DateTimeRange(start_date, end_date)

                                    # if time range period is in time range absence
                                    if time_range_absence.is_intersection(time_range_period):
                                        # for date_received in time_range_absence.range(datetime.timedelta(days=1)):
                                        # set information in dict
                                        if date_absence.isoweekday() not in [6, 7]:
                                            try:
                                                dict_children[absence.child]
                                            except KeyError:
                                                pass
                                            else:
                                                if not \
                                                    dict_children[absence.child]["days"][date_absence.isoweekday()][
                                                        "periods"][
                                                        period.type][
                                                        period.order][
                                                        "status"] == "absence":
                                                    if \
                                                        dict_children[absence.child]["days"][date_absence.isoweekday()][
                                                            "periods"][
                                                            period.type][
                                                            period.order][
                                                            "status"] == "expected":
                                                        dict_table[date_absence.isoweekday()]["periods"][period.type][
                                                            period.order][
                                                            'expected'] -= 1

                                                    dict_children[absence.child]["days"][date_absence.isoweekday()][
                                                        "periods"][
                                                        period.type][
                                                        period.order][
                                                        "absence"] = absence
                                                    dict_children[absence.child]["days"][date_absence.isoweekday()][
                                                        "periods"][
                                                        period.type][
                                                        period.order]["status"] = "absence"

        # early troubleshooting
        early_troubleshootings = EarlyTroubleshooting.objects.filter(date__gte=week_dates_date[0],
                                                                     date__lte=week_dates_date[-1],
                                                                     child__classroom=classroom)
        for et in early_troubleshootings:
            for per in et.periods.all():
                dict_children[et.child]["days"][et.date.isoweekday()]["periods"][per.type][per.order][
                    'status'] = "troubleshooting"
                dict_children[et.child]["days"][et.date.isoweekday()]["periods"][per.type][per.order][
                    'troubleshooting'] = True
                dict_children[et.child]["type"][per.type] = True
                dict_table[et.date.isoweekday()]["periods"][per.type][per.order]['expected'] += 1

        # get child present
        children_present = Presence.objects.filter(date__in=week_dates, arrival_time__isnull=False, classroom=classroom)
        children_leave = children_present.filter(departure_time__isnull=False)

        # troubleshooting
        troubleshooting = []
        for presence in children_present:
            try:
                presence.dailyfollowup.troubleshooting
                # for period in presence.dailyfollowup.troubleshooting.periods.filter(period__weekday=weekday):
                if presence not in troubleshooting:
                    troubleshooting.append(presence)
            except DailyFollowUp.troubleshooting.RelatedObjectDoesNotExist:
                pass

        for ts in troubleshooting:
            # on creer le dict
            PresenceWeekKinderGartenListView.create_dict_struct_for_child(classroom_dayoffs, ts, dict_children,
                                                                          period_for_day,
                                                                          week_dates, holidays, closures_dates)
            child_period = ts.dailyfollowup.troubleshooting.periods.all()
            for period in child_period:
                # create time range of period
                start_date = datetime.datetime.combine(ts.date, period.start_time)
                end_date = datetime.datetime.combine(ts.date, period.end_time)
                time_range_period = DateTimeRange(start_date, end_date)
                if datetime.datetime.combine(ts.date, ts.arrival_time) in time_range_period:
                    # set information in dict_children
                    dict_children[ts.child]["days"][ts.date.isoweekday()]["periods"][period.type][period.order][
                        "status"] = "troubleshooting"
                    dict_children[ts.child]["days"][ts.date.isoweekday()]["periods"][period.type][period.order][
                        "troubleshooting"] = True
                    dict_children[ts.child]["type"][period.type] = True
                    dict_table[ts.date.isoweekday()]["periods"][period.type][period.order]['present'] += 1

        for presence in children_present:
            PresenceWeekKinderGartenListView.create_dict_struct_for_child(classroom_dayoffs, presence,
                                                                          dict_children, period_for_day,
                                                                          week_dates, holidays, closures_dates)
            child_period = presence.child.periods.filter(weekday=presence.date.isoweekday())
            for period in child_period:
                # create time range of period
                start_date = make_aware(datetime.datetime.combine(presence.date, period.start_time))
                end_date = make_aware(datetime.datetime.combine(presence.date, period.end_time))
                time_range_period = DateTimeRange(start_date, end_date)
                start_date_presence = make_aware(datetime.datetime.combine(presence.date, presence.arrival_time))
                time_range_arrival_now = DateTimeRange(start_date_presence, timezone.localtime())
                if time_range_period.is_intersection(time_range_arrival_now):
                    # set information in dict_children
                    if dict_children[presence.child]["days"][presence.date.isoweekday()]["periods"][period.type][
                        period.order][
                        "status"] == "expected":
                        dict_table[presence.date.isoweekday()]["periods"][period.type][period.order]['expected'] -= 1
                        if presence.intermediate_departure_time and presence.intermediate_departure_time <= timezone.localtime().time() and not presence.intermediate_arrival_time:
                            dict_children[presence.child]["days"][presence.date.isoweekday()]["periods"][period.type][
                                period.order][
                                "status"] = "awaiting_return"
                        else:
                            dict_children[presence.child]["days"][presence.date.isoweekday()]["periods"][period.type][
                                period.order][
                                "status"] = "present"
                            dict_table[presence.date.isoweekday()]["periods"][period.type][period.order]['present'] += 1

        for presence in children_leave:
            try:
                periods_list = []
                presence.dailyfollowup.troubleshooting
                child_period = presence.dailyfollowup.troubleshooting.periods.filter(weekday=presence.date.isoweekday())
                for period in child_period:
                    periods_list.append(period)
                child_period_normal = presence.child.periods.filter(weekday=presence.date.isoweekday())
                for period in child_period_normal:
                    if period not in periods_list:
                        periods_list.append(period)
            except DailyFollowUp.troubleshooting.RelatedObjectDoesNotExist:
                periods_list = presence.child.periods.filter(weekday=presence.date.isoweekday())

            for period in periods_list:
                # create time range of period
                start_date = make_aware(datetime.datetime.combine(presence.date, period.start_time))
                end_date = make_aware(datetime.datetime.combine(presence.date, period.end_time))
                time_range_period = DateTimeRange(start_date, end_date)
                start_date_presence = make_aware(datetime.datetime.combine(presence.date, presence.arrival_time))
                end_date_presence = make_aware(datetime.datetime.combine(presence.date, presence.departure_time))
                time_range_arrival_now = DateTimeRange(start_date_presence, end_date_presence)
                if time_range_period.is_intersection(time_range_arrival_now):
                    # set information in dict_children
                    if dict_children[presence.child]["days"][presence.date.isoweekday()]["periods"][period.type][
                        period.order][
                        "status"] in ["present", "troubleshooting"]:
                        dict_children[presence.child]["days"][presence.date.isoweekday()]["periods"][period.type][
                            period.order][
                            "status"] = "leave"
                        # dict_table[presence.date.isoweekday()]["periods"][period.order]['expected'] -= 1
                        dict_table[presence.date.isoweekday()]["periods"][period.type][period.order]['present'] -= 1

        return dict_children, dict_table, errors

    @staticmethod
    def create_dict_struct_for_child(classroom_dayoffs, child, dict_children, period_for_day, week_dates, holidays,
                                     closures_dates):
        if child.child not in dict_children:
            dict_children[child.child] = {"days": {}, "type": {"morning": None, "afternoon": None}}

            # add in dict day
            for week_date in week_dates:
                dict_children[child.child]["days"][week_date.isoweekday()] = {
                    "datetime": week_date,
                    "periods": {}
                }

                # period_for_day = periods.filter(weekday=week_date.isoweekday()).order_by("order")
                period_for_day_list = {period["id"]: [period['order'], period['type']] for period in period_for_day
                                       if
                                       period['weekday'] == week_date.isoweekday()}
                for period_id, period_info in period_for_day_list.items():
                    #
                    # for period in period_for_day:
                    if period_info[1] not in dict_children[child.child]["days"][week_date.isoweekday()]["periods"]:
                        dict_children[child.child]["days"][week_date.isoweekday()]["periods"][period_info[1]] = {}
                    if period_info[0] not in dict_children[child.child]["days"][week_date.isoweekday()]["periods"][
                        period_info[1]]:
                        dict_children[child.child]["days"][week_date.isoweekday()]["periods"][period_info[1]][
                            period_info[0]] = {
                            "status": "",
                            "troubleshooting": None,
                            "absence": None,
                            "dayoff": False,
                            "holiday": False,
                            "closure": False,
                            "birthday": False,
                        }

                    # Holidays
                    if week_date.date() in holidays:
                        dict_children[child.child]['days'][week_date.isoweekday()]["periods"][period_info[1]][
                            period_info[0]][
                            "holiday"] = True
                    # Closures
                    if week_date.date() in closures_dates:
                        dict_children[child.child]['days'][week_date.isoweekday()]["periods"][period_info[1]][
                            period_info[0]][
                            "closure"] = True

                    if week_date.isoweekday() in classroom_dayoffs:
                        dict_children[child.child]["days"][week_date.isoweekday()]["periods"][period_info[1]][
                            period_info[0]][
                            "dayoff"] = True
                    # birthday
                    if child.child.birth_date:
                        if week_date.date().day == child.child.birth_date.day and week_date.date().month == child.child.birth_date.month:
                            dict_children[child.child]["days"][week_date.isoweekday()]["periods"][period_info[1]][
                                period_info[0]]["birthday"] = True


class ActivityCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'nobinobi_daily_follow_up/activity/activity_create.html'
    success_message = _('Success: Activity was created.')

    def form_valid(self, form):
        form.instance.daily_follow_up_id = self.kwargs.get("daily_follow_up")
        return super(ActivityCreateView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class ActivityDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Activity
    template_name = 'nobinobi_daily_follow_up/activity/activity_confirm_delete.html'
    success_message = _('Success: Activity was deleted.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class ActivityDetailView(LoginRequiredMixin, DetailView):
    model = Activity


class ActivityUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'nobinobi_daily_follow_up/activity/activity_update.html'
    success_message = _('Success: Activity was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity


class TypeActivityCreateView(LoginRequiredMixin, CreateView):
    model = TypeActivity


class TypeActivityDeleteView(LoginRequiredMixin, DeleteView):
    model = TypeActivity


class TypeActivityDetailView(LoginRequiredMixin, DetailView):
    model = TypeActivity


class TypeActivityUpdateView(LoginRequiredMixin, UpdateView):
    model = TypeActivity


class TypeActivityListView(LoginRequiredMixin, ListView):
    model = TypeActivity


class ActivityGroupCreateView(LoginRequiredMixin, CreateView):
    model = ActivityGroup


class ActivityGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = ActivityGroup


class ActivityGroupDetailView(LoginRequiredMixin, DetailView):
    model = ActivityGroup


class ActivityGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = ActivityGroup


class ActivityGroupListView(LoginRequiredMixin, ListView):
    model = ActivityGroup


class NapCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Nap
    form_class = NapForm
    template_name = 'nobinobi_daily_follow_up/nap/nap_create.html'
    success_message = _('Success: Nap was created.')

    def form_valid(self, form):
        form.instance.daily_follow_up_id = self.kwargs.get("daily_follow_up")
        return super(NapCreateView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class NapDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Nap
    template_name = 'nobinobi_daily_follow_up/nap/nap_confirm_delete.html'
    success_message = _('Success: Nap was deleted.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class NapDetailView(LoginRequiredMixin, DetailView):
    model = Nap


class NapUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Nap
    form_class = NapForm
    template_name = 'nobinobi_daily_follow_up/nap/nap_update.html'
    success_message = _('Success: Nap was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class NapListView(LoginRequiredMixin, ListView):
    model = Nap


class DailyFollowUpCreateView(LoginRequiredMixin, CreateView):
    model = DailyFollowUp


class DailyFollowUpDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyFollowUp


class DailyFollowUpDetailView(LoginRequiredMixin, DetailView):
    model = DailyFollowUp


class DailyFollowUpUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = DailyFollowUp
    form_class = DailyFollowUpForm
    template_name = 'nobinobi_daily_follow_up/dailyfollowup/dailyfollowup_update.html'
    success_message = _('Success: Daily follow-up was updated.')

    def get_success_url(self):
        classroom = self.object.presence.child.classroom_id
        child = self.object.presence.child_id
        date = self.object.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DailyFollowUpListView(LoginRequiredMixin, ListView):
    model = DailyFollowUp


class DailyFollowUpChoiceSummaryWeek(LoginRequiredMixin, FormView):
    template_name = "nobinobi_daily_follow_up/dailyfollowup/summary_week_choice.html"
    form_class = ChoiceChildDateForm

    def get_context_data(self, **kwargs):
        context = super(DailyFollowUpChoiceSummaryWeek, self).get_context_data(**kwargs)
        context["title"] = _("Choice a summary for a week Daily follow-up")
        return context

    def form_valid(self, form):
        pk = form.cleaned_data['child'].pk
        date = form.cleaned_data['date']
        # super(DailyFollowUpChoiceSummaryWeek, self).form_valid(form)

        return HttpResponseRedirect(
            reverse("nobinobi_daily_follow_up:DailyFollowUp_summary_week",
                    kwargs={"pk": pk, "date": date}))


class DailyFollowUpSummaryWeek(LoginRequiredMixin, TemplateView):
    template_name = "nobinobi_daily_follow_up/dailyfollowup/summary_week.html"

    def get_context_data(self, **kwargs):
        context = super(DailyFollowUpSummaryWeek, self).get_context_data(**kwargs)
        context["title"] = _("Summary for a week Daily follow-up")
        context["child"] = get_object_or_404(Child, pk=self.kwargs.get("pk"))
        context['now'] = arrow.get(self.kwargs.get("date"))
        context['week'] = context['now'].span('week')
        return context


class LotionDailyFollowUpCreateView(LoginRequiredMixin, BSModalCreateView):
    model = LotionDailyFollowUp
    form_class = LotionDailyFollowUpForm
    template_name = 'nobinobi_daily_follow_up/lotiondailyfollowup/lotiondailyfollowup_create.html'
    success_message = _('Success: Lotion was created.')

    def form_valid(self, form):
        form.instance.daily_follow_up_id = self.kwargs.get("daily_follow_up")
        return super(LotionDailyFollowUpCreateView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class LotionDailyFollowUpDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = LotionDailyFollowUp
    template_name = 'nobinobi_daily_follow_up/lotiondailyfollowup/lotiondailyfollowup_confirm_delete.html'
    success_message = _('Success: Lotion was deleted.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class LotionDailyFollowUpDetailView(LoginRequiredMixin, DetailView):
    model = LotionDailyFollowUp


class LotionDailyFollowUpUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = LotionDailyFollowUp
    form_class = LotionDailyFollowUpForm
    template_name = 'nobinobi_daily_follow_up/lotiondailyfollowup/lotiondailyfollowup_update.html'
    success_message = _('Success: Lotion was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class LotionDailyFollowUpListView(LoginRequiredMixin, ListView):
    model = LotionDailyFollowUp


class DiaperChangeCreateView(LoginRequiredMixin, BSModalCreateView):
    model = DiaperChange
    form_class = DiaperChangeForm
    template_name = 'nobinobi_daily_follow_up/diaperchange/diaperchange_create.html'
    success_message = _('Success: Diaper change was created.')

    def form_valid(self, form):
        form.instance.daily_follow_up_id = self.kwargs.get("daily_follow_up")
        return super(DiaperChangeCreateView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DiaperChangeDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = DiaperChange
    template_name = 'nobinobi_daily_follow_up/diaperchange/diaperchange_confirm_delete.html'
    success_message = _('Success: Diaper change was deleted.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DiaperChangeDetailView(LoginRequiredMixin, DetailView):
    model = DiaperChange


class DiaperChangeUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = DiaperChange
    form_class = DiaperChangeForm
    template_name = 'nobinobi_daily_follow_up/diaperchange/diaperchange_update.html'
    success_message = _('Success: Diaper change was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DiaperChangeListView(LoginRequiredMixin, ListView):
    model = DiaperChange


class LotionCreateView(LoginRequiredMixin, CreateView):
    model = Lotion


class LotionDeleteView(LoginRequiredMixin, DeleteView):
    model = Lotion


class LotionDetailView(LoginRequiredMixin, DetailView):
    model = Lotion


class LotionUpdateView(LoginRequiredMixin, UpdateView):
    model = Lotion


class LotionListView(LoginRequiredMixin, ListView):
    model = Lotion


class DailyFollowUpToMedicationCreateView(LoginRequiredMixin, BSModalCreateView):
    form_class = DailyFollowUpToMedicationForm
    template_name = 'nobinobi_daily_follow_up/dailyfollowuptomedication/dailyfollowuptomedication_create.html'
    success_message = _('Success: Daily Follow-Up to Medication was created.')

    def form_valid(self, form):
        form.instance.daily_follow_up_id = self.kwargs.get("daily_follow_up")
        return super(DailyFollowUpToMedicationCreateView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DailyFollowUpToMedicationDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = DailyFollowUpToMedication
    template_name = 'nobinobi_daily_follow_up/dailyfollowuptomedication/dailyfollowuptomedication_confirm_delete.html'
    success_message = _('Success: DailyFollowUpToMedication was deleted.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DailyFollowUpToMedicationDetailView(LoginRequiredMixin, DetailView):
    model = DailyFollowUpToMedication


class DailyFollowUpToMedicationUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = DailyFollowUpToMedication
    form_class = MedicationForm
    template_name = 'nobinobi_daily_follow_up/dailyfollowuptomedication/dailyfollowuptomedication_update.html'
    success_message = _('Success: Medication was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class DailyFollowUpToMedicationListView(LoginRequiredMixin, ListView):
    model = DailyFollowUpToMedication


class MedicationCreateView(LoginRequiredMixin, BSModalCreateView):
    form_class = MedicationForm
    template_name = 'nobinobi_daily_follow_up/medication/medication_create.html'
    success_message = _('Success: Medication was created.')

    def get_form_kwargs(self):
        kwargs = super(MedicationCreateView, self).get_form_kwargs()
        kwargs.update({"daily_follow_up": self.kwargs.get("daily_follow_up")})
        kwargs.update({"child": self.kwargs.get("child")})
        return kwargs

    def get_success_url(self):
        classroom = self.kwargs.get("classroom_id")
        child = self.kwargs.get("child")
        date = Presence.objects.get(dailyfollowup__pk=self.kwargs.get("daily_follow_up")).date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class MedicationDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Medication
    template_name = 'nobinobi_daily_follow_up/medication/medication_confirm_delete.html'
    success_message = _('Success: Medication was deleted.')

    def get_success_url(self):
        classroom = self.kwargs.get("classroom_id")
        child = self.kwargs.get("child")
        date = Presence.objects.get(dailyfollowup__pk=self.kwargs.get("daily_follow_up")).date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class MedicationDetailView(LoginRequiredMixin, DetailView):
    model = Medication


class MedicationUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'nobinobi_daily_follow_up/medication/medication_update.html'
    success_message = _('Success: Medication was updated.')

    def get_form_kwargs(self):
        kwargs = super(MedicationUpdateView, self).get_form_kwargs()
        kwargs.update({"daily_follow_up": self.kwargs.get("daily_follow_up")})
        kwargs.update({"child": self.kwargs.get("child")})
        return kwargs

    def get_success_url(self):
        classroom = self.kwargs.get("classroom_id")
        child = self.kwargs.get("child")
        date = Presence.objects.get(dailyfollowup__pk=self.kwargs.get("daily_follow_up")).date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class MedicationListView(LoginRequiredMixin, ListView):
    model = Medication


class TypeMedicationCreateView(LoginRequiredMixin, CreateView):
    model = TypeMedication


class TypeMedicationDeleteView(LoginRequiredMixin, DeleteView):
    model = TypeMedication


class TypeMedicationDetailView(LoginRequiredMixin, DetailView):
    model = TypeMedication


class TypeMedicationUpdateView(LoginRequiredMixin, UpdateView):
    model = TypeMedication


class TypeMedicationListView(LoginRequiredMixin, ListView):
    model = TypeMedication


class ReceptionCreateView(LoginRequiredMixin, CreateView):
    model = Reception


class ReceptionDeleteView(LoginRequiredMixin, DeleteView):
    model = Reception


class ReceptionDetailView(LoginRequiredMixin, DetailView):
    model = Reception


class ReceptionUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Reception
    form_class = ReceptionForm
    template_name = 'nobinobi_daily_follow_up/reception/reception_update.html'
    success_message = _('Success: Reception was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class ReceptionListView(LoginRequiredMixin, ListView):
    model = Reception


class GiveMedicationCreateView(LoginRequiredMixin, BSModalCreateView):
    model = GiveMedication
    form_class = GiveMedicationForm
    template_name = 'nobinobi_daily_follow_up/givemedication/givemedication_create.html'
    success_message = _('Success: Give Medication was created.')

    def get_form_kwargs(self):
        kwargs = super(GiveMedicationCreateView, self).get_form_kwargs()
        kwargs['date'] = timezone.localtime().date()
        return kwargs

    def form_valid(self, form):
        form.instance.medication = get_object_or_404(Medication, pk=self.kwargs.get("medication"))
        return super(GiveMedicationCreateView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.object.medication.child.classroom_id
        child = self.object.medication.child_id
        date = self.object.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class GiveMedicationDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = GiveMedication
    template_name = 'nobinobi_daily_follow_up/givemedication/givemedication_confirm_delete.html'
    success_message = _('Success: Give Medication was deleted.')

    def get_success_url(self):
        classroom = self.object.medication.child.classroom_id
        child = self.object.medication.child_id
        date = self.object.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class GiveMedicationDetailView(LoginRequiredMixin, DetailView):
    model = GiveMedication


class GiveMedicationUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = GiveMedication
    form_class = GiveMedicationForm
    template_name = 'nobinobi_daily_follow_up/givemedication/givemedication_update.html'
    success_message = _('Success: Give Medication was updated.')

    def get_form_kwargs(self):
        kwargs = super(GiveMedicationUpdateView, self).get_form_kwargs()
        kwargs['date'] = timezone.localtime().date()
        return kwargs

    def get_success_url(self):
        classroom = self.object.medication.child.classroom_id
        child = self.object.medication.child_id
        date = self.object.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class GiveMedicationDelayView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, FormView):
    form_class = GiveMedicationDelayForm
    template_name = 'nobinobi_daily_follow_up/givemedication/givemedication_delay.html'
    success_message = _('Success: Give Medication was delayed.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.classroom = None

    def get_form_kwargs(self):
        kwargs = super(GiveMedicationDelayView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        gm = GiveMedication.objects.get(pk=self.kwargs.get("pk"))
        kwargs['classroom'] = Classroom.objects.get(pk=gm.medication.child.classroom_id)
        kwargs['date'] = timezone.localtime().date()
        return kwargs

    def form_valid(self, form):
        give_medication = get_object_or_404(GiveMedication, id=self.kwargs['pk'])
        delayed_time = arrow.get(timezone.localtime()).shift(minutes=+10)
        givemedication_type = ContentType.objects.get_for_model(GiveMedication)

        try:
            notifs = Notification.objects.filter(actor_content_type=givemedication_type,
                                                 actor_object_id=give_medication.id, level="warning")
            if notifs.count() == 0:
                raise Notification.DoesNotExist
        except Notification.DoesNotExist:
            pass
        else:
            for notif in notifs:
                notif.timestamp = delayed_time.datetime
                notif.save()

        self.classroom = form.classroom
        # notify.send(self.request.user, recipient="Users", verb='You have to give the medicine.', action_object=give_medication, level="warning", timestamp=delayed_time.timestamp)
        return super(GiveMedicationDelayView, self).form_valid(form)

    def get_success_url(self):
        classroom = self.classroom.id
        url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class GiveMedicationListView(LoginRequiredMixin, ListView):
    model = GiveMedication


class MealDailyFollowUpCreateView(LoginRequiredMixin, BSModalCreateView):
    model = MealDailyFollowUp
    form_class = MealDailyFollowUpForm
    template_name = 'nobinobi_daily_follow_up/meals/mealdailyfollowup_create.html'
    success_message = _('Success: Meals was created.')

    def form_valid(self, form):
        return super(MealDailyFollowUpCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(MealDailyFollowUpCreateView, self).form_invalid(form)

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class MealDailyFollowUpDeleteView(LoginRequiredMixin, DeleteView):
    model = MealDailyFollowUp


class MealDailyFollowUpDetailView(LoginRequiredMixin, DetailView):
    model = MealDailyFollowUp


class MealDailyFollowUpUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = MealDailyFollowUp
    form_class = MealDailyFollowUpForm
    template_name = 'nobinobi_daily_follow_up/meals/mealdailyfollowup_update.html'
    success_message = _('Success: Meals was updated.')

    def get_success_url(self):
        classroom = self.object.daily_follow_up.presence.child.classroom_id
        child = self.object.daily_follow_up.presence.child_id
        date = self.object.daily_follow_up.presence.date
        next_url = self.request.GET.get('next')
        if next_url:
            url = reverse_lazy('nobinobi_daily_follow_up:DailyFollowUp_summary_week',
                               kwargs={"pk": child, "date": date})
        else:
            url = reverse_lazy('nobinobi_daily_follow_up:Presence_detail_list', kwargs={"pk": classroom})
        return url


class MealDailyFollowUpListView(LoginRequiredMixin, ListView):
    model = MealDailyFollowUp


class MealCreateView(LoginRequiredMixin, CreateView):
    model = Meal


class MealDeleteView(LoginRequiredMixin, DeleteView):
    model = Meal


class MealDetailView(LoginRequiredMixin, DetailView):
    model = Meal


class MealUpdateView(LoginRequiredMixin, UpdateView):
    model = Meal


class MealListView(LoginRequiredMixin, ListView):
    model = Meal


class StrollChoiceView(LoginRequiredMixin, FormView):
    template_name = "nobinobi_daily_follow_up/stroll/stroll_choice_classroom.html"
    form_class = ChoiceClassroomForm
    classroom = None

    def get(self, request, *args, **kwargs):
        """ redirect auto si un seul groupe"""
        try:
            allowed_classroom = Classroom.objects.get(allowed_login=request.user)
        except Classroom.MultipleObjectsReturned:
            pass
        except Classroom.DoesNotExist:
            pass
        else:
            return HttpResponseRedirect(
                reverse("nobinobi_daily_follow_up:stroll_pdf", kwargs={"classroom_id": allowed_classroom.pk}))
        return super(StrollChoiceView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(StrollChoiceView, self).get_form_kwargs()
        userid = self.request.user.id
        kwargs.update(userid=userid)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StrollChoiceView, self).get_context_data(**kwargs)
        context["title"] = _("Classroom choice for stroll")
        return context

    def form_valid(self, form):
        self.classroom = form.cleaned_data['id']
        return super(StrollChoiceView, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_daily_follow_up:stroll_pdf", kwargs={"classroom_id": self.classroom.pk})


class StrollViewPDF(WeasyTemplateResponseMixin, LoginRequiredMixin, TemplateView):
    model = Presence
    template_name = 'nobinobi_daily_follow_up/stroll/stroll_pdf.html'
    filename = 'stroll.pdf'

    classroom = None
    now = None

    def get_context_data(self, **kwargs):
        context = super(StrollViewPDF, self).get_context_data(**kwargs)
        classroom_id = self.kwargs.get("classroom_id")
        # context["enfants"] = self.model.objects.filter(classroom=classe_id, actif=True)
        context["presences"] = self.model.objects.filter(classroom=classroom_id, date=self.now.date(),
                                                         arrival_time__isnull=False,
                                                         departure_time__isnull=True).order_by("child__first_name",
                                                                                               "child__last_name")
        context['classroom'] = self.classroom
        context['date'] = self.now
        return context

    def get(self, request, *args, **kwargs):
        self.now = arrow.now(tz="Europe/Zurich")
        try:
            self.classroom = Classroom.objects.get(id=self.kwargs.get("classroom_id"))
        except Classroom.DoesNotExist:
            messages.error(self.request, _("The classroom does not exist."))
            return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:stroll_choice"))
        except Classroom.MultipleObjectsReturned:
            messages.error(self.request, _("There are several classrooms with this ID."))
            return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:stroll_choice"))

        return super(StrollViewPDF, self).get(request)


class GroupActivityChoiceView(LoginRequiredMixin, FormView):
    template_name = "nobinobi_daily_follow_up/activity/activity_choice_classroom.html"
    form_class = ChoiceClassroomForm
    classroom = None

    def get(self, request, *args, **kwargs):
        """ redirect auto si un seul groupe"""
        try:
            allowed_classroom = Classroom.objects.get(allowed_login=request.user)
        except Classroom.MultipleObjectsReturned:
            pass
        except Classroom.DoesNotExist:
            pass
        else:
            return HttpResponseRedirect(
                reverse("nobinobi_daily_follow_up:group_activity_view", kwargs={"classroom_id": allowed_classroom.pk}))
        return super(GroupActivityChoiceView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(GroupActivityChoiceView, self).get_form_kwargs()
        userid = self.request.user.id
        kwargs.update(userid=userid)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(GroupActivityChoiceView, self).get_context_data(**kwargs)
        context["title"] = _("Classroom choice for Group activity")
        return context

    def form_valid(self, form):
        self.classroom = form.cleaned_data['id']
        return super(GroupActivityChoiceView, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_daily_follow_up:group_activity_view", kwargs={"classroom_id": self.classroom.pk})


class GroupActivityUpdateView(LoginRequiredMixin, FormView):
    """
        :param cr: database cursor
        :param uid: current user id
        :param ids: list of ids
        :rtype: dictionary with a

        This function is used for mettre a jour les activites
    """
    template_name = 'nobinobi_daily_follow_up/activity/group_activity_update.html'
    form_class = GroupActivityForm
    model = Presence

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.child_class = None

    def get_form_kwargs(self, **kwargs):
        kwargs = super(GroupActivityUpdateView, self).get_form_kwargs()
        kwargs['classroom_id'] = self.kwargs['classroom_id']
        return kwargs

    def get(self, request, *args, **kwargs):
        try:
            self.classroom = Classroom.objects.get(pk=self.kwargs['classroom_id'])
            return self.render_to_response(self.get_context_data())
        except Classroom.DoesNotExist:
            messages.error(request, _("Classroom is not found"))
            return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:Presence_choice"))

    def get_context_data(self, **kwargs):
        context = super(GroupActivityUpdateView, self).get_context_data(**kwargs)
        context['now'] = timezone.localtime()
        context['classroom'] = self.classroom
        context['title'] = _("Classroom activities")
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """

        # self.object = form.save(commit=False)
        date_today = timezone.localtime().date()

        for e in form.cleaned_data['children_get_name']:
            try:
                # recuperation du suivi journalier
                presence = self.model.objects.get(date__exact=date_today, child=e)
                if form.cleaned_data['activity']:
                    # pour chaque activite dans les activites selectionner
                    for act in form.cleaned_data['activity']:
                        # si la remarque du matin est pas vide on ajout au suivijournalier
                        comment = ""
                        if form.cleaned_data['comment'] is not None:
                            if form.cleaned_data['comment'] != "":
                                comment = form.cleaned_data['comment']

                        # ajout des activites au suivi journalier
                        presence.dailyfollowup.activity_set.get_or_create(
                            type_activity=act,
                            defaults={"comment": comment}
                        )
            # le suivi journalier n'existe pas
            except self.model.DoesNotExist:
                messages.error(self.request, _("{} does not have a presence today.").format(e))
                # si pas de suivi journalier au jour
            finally:
                if not self.model.objects.filter(date__exact=date_today).count():
                    messages.error(self.request, _("There is no daily follow-up today."))
                    return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:group_activity_choice_view"))

        messages.success(self.request, _("Activity (s) added"))
        return super(GroupActivityUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_daily_follow_up:group_activity_choice_view")


class GroupDailyFollowUpChoiceView(LoginRequiredMixin, FormView):
    template_name = "nobinobi_daily_follow_up/dailyfollowup/group_choice_classroom.html"
    form_class = ChoiceClassroomForm
    classroom = None

    def get(self, request, *args, **kwargs):
        """ redirect auto si un seul groupe"""
        try:
            allowed_classroom = Classroom.objects.get(allowed_login=request.user)
        except Classroom.MultipleObjectsReturned:
            pass
        except Classroom.DoesNotExist:
            pass
        else:
            return HttpResponseRedirect(
                reverse("nobinobi_daily_follow_up:group_daily_follow_up_view",
                        kwargs={"classroom_id": allowed_classroom.pk}))
        return super(GroupDailyFollowUpChoiceView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(GroupDailyFollowUpChoiceView, self).get_form_kwargs()
        userid = self.request.user.id
        kwargs.update(userid=userid)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(GroupDailyFollowUpChoiceView, self).get_context_data(**kwargs)
        context["title"] = _("Classroom choice for Group daily follow-up")
        return context

    def form_valid(self, form):
        self.classroom = form.cleaned_data['id']
        return super(GroupDailyFollowUpChoiceView, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_daily_follow_up:group_daily_follow_up_view",
                       kwargs={"classroom_id": self.classroom.pk})


class GroupDailyFollowUpUpdateView(LoginRequiredMixin, FormView):
    """
        :param cr: database cursor
        :param uid: current user id
        :param ids: list of ids
        :rtype: dictionary with a

        This function is used for mettre a jour les activites
    """
    template_name = 'nobinobi_daily_follow_up/dailyfollowup/group_daily_follow_up_update.html'
    form_class = GroupDailyFollowUpForm
    model = DailyFollowUp

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.child_class = None

    def get_form_kwargs(self, **kwargs):
        kwargs = super(GroupDailyFollowUpUpdateView, self).get_form_kwargs()
        kwargs['classroom_id'] = self.kwargs['classroom_id']
        return kwargs

    def get(self, request, *args, **kwargs):
        try:
            self.classroom = Classroom.objects.get(pk=self.kwargs['classroom_id'])
            return self.render_to_response(self.get_context_data())
        except Classroom.DoesNotExist:
            messages.error(request, _("Classroom is not found"))
            return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:Presence_choice"))

    def get_context_data(self, **kwargs):
        context = super(GroupDailyFollowUpUpdateView, self).get_context_data(**kwargs)
        context['now'] = timezone.localtime()
        context['classroom'] = self.classroom
        context['title'] = _("Classroom comment & important")
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """

        # self.object = form.save(commit=False)
        date_today = timezone.localtime().date()

        for e in form.cleaned_data['children_get_name']:
            try:
                # recuperation du suivi journalier
                dfp = self.model.objects.get(presence__date__exact=date_today, presence__child=e)
            # le suivi journalier n'existe pas
            except self.model.DoesNotExist:
                messages.error(self.request, _("{} does not have a daily follow-up today.").format(e))
            else:
                if form.cleaned_data['comment'] is not None:
                    if form.cleaned_data['comment'] != "":
                        if not dfp.comment:
                            dfp.comment = ""
                        dfp.comment += form.cleaned_data['comment']

                if dfp.important != form.cleaned_data['important']:
                    dfp.important = form.cleaned_data['important']

                dfp.save()
                # si pas de suivi journalier au jour
            # finally:
            #     return HttpResponseRedirect(reverse("nobinobi_daily_follow_up:group_daily_follow_up_choice_view"))
        messages.success(self.request, _("Group comment or/and important (s) added"))
        return super(GroupDailyFollowUpUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_daily_follow_up:group_daily_follow_up_choice_view")


def dfu_live_all_notification_list(request):
    ''' Return a json with a unread notification list '''
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'all_count': 0,
            'all_list': []
        }
        return JsonResponse(data)

    default_num_to_fetch = get_config()['NUM_TO_FETCH']
    try:
        # If they don't specify, make it 5.
        num_to_fetch = request.GET.get('max', default_num_to_fetch)
        num_to_fetch = int(num_to_fetch)
        if not (1 <= num_to_fetch <= 100):
            num_to_fetch = default_num_to_fetch
    except ValueError:  # If casting to an int fails.
        num_to_fetch = default_num_to_fetch

    all_list = []

    for notification in request.user.notifications.filter(public=True, timestamp__lte=timezone.localtime())[
                        0:num_to_fetch]:
        struct = model_to_dict(notification)
        struct['slug'] = id2slug(notification.id)
        if notification.actor:
            struct['actor'] = str(notification.actor)
        if notification.target:
            struct['target'] = str(notification.target)
        if notification.action_object:
            struct['action_object'] = str(notification.action_object)
        if notification.data:
            struct['data'] = notification.data
        all_list.append(struct)
        if request.GET.get('mark_as_read'):
            notification.mark_as_read()
    data = {
        'all_count': request.user.notifications.filter(public=True, timestamp__lte=timezone.localtime()).count(),
        'all_list': all_list
    }
    return JsonResponse(data)


def dfu_live_all_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'all_count': 0
        }
    else:
        data = {
            'all_count': request.user.notifications.filter(public=True, timestamp__lte=timezone.localtime()).count(),
        }
    return JsonResponse(data)


class ClassroomJsonView(AutoResponseView):

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            raise Http404
        return qs.filter(
            Q(allowed_login=self.request.user) | Q(allowed_group_login__in=self.request.user.groups.all())).distinct()


class MultiDayMedication(LoginRequiredMixin, FormView):
    form_class = MultiDayMedicationForm
    template_name = "nobinobi_daily_follow_up/medication/medication_multiday.html"

    def get_context_data(self, **kwargs):
        context = super(MultiDayMedication, self).get_context_data(**kwargs)
        context["title"] = _("Multi Day Medication")
        return context

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        if self.object:
            messages.success(request=self.request, message=_("The multi-day medication was created."))
        # on creer le give medication
        gives_hour = [
            form.cleaned_data['give_hour'],
            form.cleaned_data['give_hour2'],
            form.cleaned_data['give_hour3'],
            form.cleaned_data['give_hour4'],
            form.cleaned_data['give_hour5']
        ]

        from_date = self.object.from_date
        end_date = self.object.end_date

        if from_date < timezone.localtime().date() < end_date:
            from_date = timezone.localtime().date()
        if end_date < timezone.localtime().date():
            end_date = timezone.localtime().date()

        dates_range = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                        dtstart=from_date,
                                        until=end_date)]
        for date_range in dates_range:
            # check for presence in daterange
            try:
                presence = Presence.objects.get(date=date_range, child_id=form.cleaned_data['child'])
                if presence.dailyfollowup:
                    dtm, created = DailyFollowUpToMedication.objects.get_or_create(
                        medication=self.object,
                        daily_follow_up=presence.dailyfollowup
                    )
            except Presence.DoesNotExist:
                pass

            for give_hour in gives_hour:
                if give_hour:
                    gm, created = GiveMedication.objects.get_or_create(
                        medication=self.object,
                        date=date_range,
                        give_hour=give_hour,
                    )
                    if created:
                        messages.success(request=self.request,
                                         message=_("The give medication for {} was created at {}.").format(date_range,
                                                                                                           give_hour))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_daily_follow_up:Multiday_Medication")


class EarlyTroubleshootingListView(LoginRequiredMixin, TemplateView):
    """
    View for list
    """
    # model = EarlyTroubleshooting
    template_name = "nobinobi_daily_follow_up/earlytroubleshooting/earlytroubleshooting_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(EarlyTroubleshootingListView, self).get_context_data(object_list=None, **kwargs)
        context['title'] = _("Early Troubleshooting list")
        return context


class EarlyTroubleshootingCreateView(LoginRequiredMixin, BSModalCreateView):
    """
    View for create
    """
    template_name = 'nobinobi_daily_follow_up/earlytroubleshooting/earlytroubleshooting_create.html'
    form_class = EarlyTroubleshootingForm
    success_message = _('Success: Early Troubleshooting was created.')
    success_url = reverse_lazy('nobinobi_daily_follow_up:EarlyTroubleshooting_list')


class EarlyTroubleshootingDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = EarlyTroubleshooting
    template_name = 'nobinobi_daily_follow_up/earlytroubleshooting/earlytroubleshooting_confirm_delete.html'
    success_message = _('Success: Early Troubleshooting was deleted.')
    success_url = reverse_lazy('nobinobi_daily_follow_up:EarlyTroubleshooting_list')


class EarlyTroubleshootingUpdateView(LoginRequiredMixin, BSModalUpdateView):
    """
    View for update
    """
    model = EarlyTroubleshooting
    template_name = 'nobinobi_daily_follow_up/earlytroubleshooting/earlytroubleshooting_update.html'
    form_class = EarlyTroubleshootingForm
    success_message = _('Success: Early Troubleshooting was updated.')
    success_url = reverse_lazy('nobinobi_daily_follow_up:EarlyTroubleshooting_list')


# Read
class EarlyTroubleshootingDetailView(LoginRequiredMixin, BSModalReadView):
    model = EarlyTroubleshooting
    template_name = 'nobinobi_daily_follow_up/earlytroubleshooting/earlytroubleshooting_detail.html'


class EarlyTroubleshootingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EarlyTroubleshooting.objects.all()
    serializer_class = EarlyTroubleshootingSerializer
