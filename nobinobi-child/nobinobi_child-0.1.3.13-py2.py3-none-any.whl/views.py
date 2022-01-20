# -*- coding: utf-8 -*-

#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView,
    TemplateView, FormView)
from django_weasyprint import WeasyTemplateResponseMixin
from nobinobi_staff.models import Staff
from rest_framework import viewsets
from rest_framework.response import Response

from nobinobi_child.forms import LoginAuthenticationForm, AbsenceCreateForm, ChildPictureSelectForm, ChildPictureForm, \
    ChildPictureUpdateForm
from nobinobi_child.models import (
    Child,
    Language,
    Absence,
    Classroom,
    AgeGroup,
    AbsenceType,
    AbsenceGroup,
    ClassroomDayOff,
    ChildToPeriod,
    Period,
    InformationOfTheDay,
    Allergy,
    ChildToContact,
    Contact,
    Address,
    FoodRestriction,
    ChildSpecificNeed,
)
from nobinobi_child.serializers import ChildSerializer, AbsenceSerializer
from nobinobi_child.utils import get_display_contact_address


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "nobinobi_child/home.html"


class AuthLoginView(LoginView):
    template_name = 'nobinobi_child/pages/login/login.html'
    redirect_authenticated_user = True
    form_class = LoginAuthenticationForm


class ChildCreateView(CreateView):
    model = Child


class ChildDeleteView(DeleteView):
    model = Child


class ChildDetailView(LoginRequiredMixin, DetailView):
    model = Child

    def get_context_data(self, **kwargs):
        context = super(ChildDetailView, self).get_context_data(**kwargs)
        context['title'] = _("{}'s details").format(context['child'].full_name)
        context['display_contacts_address'] = get_display_contact_address()
        context['periods'] = Period.objects.all()
        now = timezone.localdate()
        child_periods = context['child'].childtoperiod_set.filter(start_date__lte=now, end_date__gte=now)
        table_periods_used = {}
        # construction table
        for period in context['periods']:
            if period.weekday not in table_periods_used:
                table_periods_used[period.weekday] = {}
            table_periods_used[period.weekday][period.order] = False

        # fill table
        for ctp in child_periods:
            table_periods_used[ctp.period.weekday][ctp.period.order] = True

        context["folder"] = None
        try:
            from nobinobi_sape_contract.models import Folder
            try:
                context["folder"] = Folder.objects.get(child=context['child'])
            except Folder.DoesNotExist:
                pass
        except ImportError:
            pass
        context['table_periods_used'] = table_periods_used
        return context


class ChildUpdateView(UpdateView):
    model = Child


class ChildListView(LoginRequiredMixin, ListView):
    model = Child

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ChildListView, self).get_context_data(object_list=None, **kwargs)
        context["name_classroom_display"] = getattr(settings, 'NAME_CLASSROOM_DISPLAY', _("Classroom"))
        classroom_allowed = self.request.user.classroom_login.all().values_list("id", flat=True)
        group_classroom_allowed = self.request.user.groups.all().values_list("classroom_group_login", flat=True)
        context['classrooms'] = Classroom.objects.filter(
            Q(id__in=classroom_allowed) | Q(id__in=group_classroom_allowed)
        ).values_list("name", flat=True)
        context['title'] = _("Child list")
        return context


class ChildViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Child.objects.filter(status__in=['in_progress', 'future'])
    serializer_class = ChildSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        classroom_allowed = self.request.user.classroom_login.all().values_list("id", flat=True)
        group_classroom_allowed = self.request.user.groups.all().values_list("classroom_group_login", flat=True)
        new_queryset = self.queryset.filter(
            Q(classroom__in=classroom_allowed) | Q(classroom__in=group_classroom_allowed)
        )

        page = self.paginate_queryset(new_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(new_queryset, many=True)
        return Response(serializer.data)


class AbsenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer


class LanguageCreateView(CreateView):
    model = Language


class LanguageDeleteView(DeleteView):
    model = Language


class LanguageDetailView(DetailView):
    model = Language


class LanguageUpdateView(UpdateView):
    model = Language


class LanguageListView(ListView):
    model = Language


class AbsenceCreateView(BSModalCreateView):
    template_name = 'nobinobi_child/absence/absence_create.html'
    form_class = AbsenceCreateForm
    success_message = _('Success: Absence was created.')
    success_url = reverse_lazy('nobinobi_child:Absence_list')


# Read
class AbsenceDetailView(BSModalReadView):
    model = Absence
    template_name = 'nobinobi_child/absence/absence_detail.html'


# Delete
class AbsenceDeleteView(BSModalDeleteView):
    model = Absence
    template_name = 'nobinobi_child/absence/absence_confirm_delete.html'
    success_message = _('Success: Absence was deleted.')
    success_url = reverse_lazy('nobinobi_child:Absence_list')


class AbsenceUpdateView(BSModalUpdateView):
    model = Absence
    template_name = 'nobinobi_child/absence/absence_update.html'
    form_class = AbsenceCreateForm
    success_message = _('Success: Absence was updated.')
    success_url = reverse_lazy('nobinobi_child:Absence_list')


class AbsenceListView(LoginRequiredMixin, ListView):
    model = Absence
    template_name = "nobinobi_child/absence/absence_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AbsenceListView, self).get_context_data(object_list=None, **kwargs)
        context['title'] = _("Absences list")
        return context


class ClassroomCreateView(CreateView):
    model = Classroom


class ClassroomDeleteView(DeleteView):
    model = Classroom


class ClassroomDetailView(DetailView):
    model = Classroom


class ClassroomUpdateView(UpdateView):
    model = Classroom


class ClassroomListView(ListView):
    model = Classroom


class AgeGroupCreateView(CreateView):
    model = AgeGroup


class AgeGroupDeleteView(DeleteView):
    model = AgeGroup


class AgeGroupDetailView(DetailView):
    model = AgeGroup


class AgeGroupUpdateView(UpdateView):
    model = AgeGroup


class AgeGroupListView(ListView):
    model = AgeGroup


class AbsenceTypeCreateView(CreateView):
    model = AbsenceType


class AbsenceTypeDeleteView(DeleteView):
    model = AbsenceType


class AbsenceTypeDetailView(DetailView):
    model = AbsenceType


class AbsenceTypeUpdateView(UpdateView):
    model = AbsenceType


class AbsenceTypeListView(ListView):
    model = AbsenceType


class AbsenceGroupCreateView(CreateView):
    model = AbsenceGroup


class AbsenceGroupDeleteView(DeleteView):
    model = AbsenceGroup


class AbsenceGroupDetailView(DetailView):
    model = AbsenceGroup


class AbsenceGroupUpdateView(UpdateView):
    model = AbsenceGroup


class AbsenceGroupListView(ListView):
    model = AbsenceGroup


class ClassroomDayOffCreateView(CreateView):
    model = ClassroomDayOff


class ClassroomDayOffDeleteView(DeleteView):
    model = ClassroomDayOff


class ClassroomDayOffDetailView(DetailView):
    model = ClassroomDayOff


class ClassroomDayOffUpdateView(UpdateView):
    model = ClassroomDayOff


class ClassroomDayOffListView(ListView):
    model = ClassroomDayOff


class ChildToPeriodCreateView(CreateView):
    model = ChildToPeriod


class ChildToPeriodDeleteView(DeleteView):
    model = ChildToPeriod


class ChildToPeriodDetailView(DetailView):
    model = ChildToPeriod


class ChildToPeriodUpdateView(UpdateView):
    model = ChildToPeriod


class ChildToPeriodListView(ListView):
    model = ChildToPeriod


class PeriodCreateView(CreateView):
    model = Period


class PeriodDeleteView(DeleteView):
    model = Period


class PeriodDetailView(DetailView):
    model = Period


class PeriodUpdateView(UpdateView):
    model = Period


class PeriodListView(ListView):
    model = Period


class InformationOfTheDayCreateView(CreateView):
    model = InformationOfTheDay


class InformationOfTheDayDeleteView(DeleteView):
    model = InformationOfTheDay


class InformationOfTheDayDetailView(DetailView):
    model = InformationOfTheDay


class InformationOfTheDayUpdateView(UpdateView):
    model = InformationOfTheDay


class InformationOfTheDayListView(LoginRequiredMixin, ListView):
    model = InformationOfTheDay

    def get_context_data(self, **kwargs):
        context = super(InformationOfTheDayListView, self).get_context_data(**kwargs)
        context["name_classroom_display"] = getattr(settings, "NAME_CLASSROOM_DISPLAY", _("Classroom"))
        return context


    def get_queryset(self):
        if self.request.user:
            iotds = self.model.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now(),
                                              classrooms__allowed_login=self.request.user)
        else:
            iotds = []
        return iotds


class AllergyCreateView(CreateView):
    model = Allergy


class AllergyDeleteView(DeleteView):
    model = Allergy


class AllergyDetailView(DetailView):
    model = Allergy


class AllergyUpdateView(UpdateView):
    model = Allergy


class AllergyListView(ListView):
    model = Allergy


class ChildToContactCreateView(CreateView):
    model = ChildToContact


class ChildToContactDeleteView(DeleteView):
    model = ChildToContact


class ChildToContactDetailView(DetailView):
    model = ChildToContact


class ChildToContactUpdateView(UpdateView):
    model = ChildToContact


class ChildToContactListView(ListView):
    model = ChildToContact


class ContactCreateView(CreateView):
    model = Contact


class ContactDeleteView(DeleteView):
    model = Contact


class ContactDetailView(DetailView):
    model = Contact


class ContactUpdateView(UpdateView):
    model = Contact


class ContactListView(ListView):
    model = Contact


class AddressCreateView(CreateView):
    model = Address


class AddressDeleteView(DeleteView):
    model = Address


class AddressDetailView(DetailView):
    model = Address


class AddressUpdateView(UpdateView):
    model = Address


class AddressListView(ListView):
    model = Address


class FoodRestrictionCreateView(CreateView):
    model = FoodRestriction


class FoodRestrictionDeleteView(DeleteView):
    model = FoodRestriction


class FoodRestrictionDetailView(DetailView):
    model = FoodRestriction


class FoodRestrictionUpdateView(UpdateView):
    model = FoodRestriction


class FoodRestrictionListView(ListView):
    model = FoodRestriction


class ChildSpecificNeedCreateView(CreateView):
    model = ChildSpecificNeed


class ChildSpecificNeedDeleteView(DeleteView):
    model = ChildSpecificNeed


class ChildSpecificNeedDetailView(DetailView):
    model = ChildSpecificNeed


class ChildSpecificNeedUpdateView(UpdateView):
    model = ChildSpecificNeed


class ChildSpecificNeedListView(ListView):
    model = ChildSpecificNeed


class StaffListView(ListView):
    model = Staff
    template_name = "nobinobi_child/staff/staff_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StaffListView, self).get_context_data(object_list=None, **kwargs)
        context['title'] = _("Staffs list")
        return context


class ChildPictureSelectView(LoginRequiredMixin, FormView):
    """Vue qui permet de choisir un enfant pour lui ajouter un photo"""
    form_class = ChildPictureSelectForm
    template_name = "nobinobi_child/child_picture_select.html"

    child = None

    def get_context_data(self, **kwargs):
        context = super(ChildPictureSelectView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.child = form.cleaned_data['child']
        return super(ChildPictureSelectView, self).form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_child:child_picture", kwargs={"pk": self.child.pk})


class ChildPictureView(LoginRequiredMixin, UpdateView):
    """Vue qui permet de mettre à jour la photo de l'enfant"""
    model = Child
    form_class = ChildPictureForm
    template_name = "nobinobi_child/child_picture.html"

    def get_context_data(self, **kwargs):
        context = super(ChildPictureView, self).get_context_data(**kwargs)
        context["child"] = get_object_or_404(Child, pk=self.kwargs.get("pk"))
        context["title"] = _("Photo modification form")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("The child's photo has been modified."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("nobinobi_child:child_picture", kwargs={"pk": self.kwargs.get("pk")})


class ChildPictureUpdateView(LoginRequiredMixin, BSModalUpdateView):
    """Vue qui permet de mettre à jour la photo de l'enfant"""
    model = Child
    form_class = ChildPictureUpdateForm
    template_name = "nobinobi_child/child_picture_update.html"
    success_message = _("Success: The child's photo has been modified.")

    def get_context_data(self, **kwargs):
        context = super(ChildPictureUpdateView, self).get_context_data(**kwargs)
        context["child"] = get_object_or_404(Child, pk=self.kwargs.get("pk"))
        return context

    def get_success_url(self):
        return reverse("nobinobi_child:Child_detail", kwargs={"pk": self.kwargs.get("pk")})


class ChildAdminPrintHealCardView(WeasyTemplateResponseMixin, DetailView, LoginRequiredMixin):
    """"""
    model = Child
    template_name = 'admin/nobinobi_child/child/print_heal_card_pdf.html'
    filename = 'heal_card.pdf'

    def get_context_data(self, **kwargs):
        context = super(ChildAdminPrintHealCardView, self).get_context_data(**kwargs)
        context['now'] = timezone.localtime()

        # Parents
        parents_name_list = ["pere", "mere", "mother", "father", "père", "mère", "Father", "Mother", "Père", "Mère"]
        try:

            context['parent_1'] = self.object.childtocontact_set.get(order=0, link_with_child__in=parents_name_list)
        except ChildToContact.DoesNotExist:
            context['parent_1'] = self.object.childtocontact_set.get(order=1, link_with_child__in=parents_name_list)
            try:
                context['parent_2'] = self.object.childtocontact_set.get(order=2, link_with_child__in=parents_name_list)
            except ChildToContact.DoesNotExist:
                context['parent_2'] = None
        else:
            try:
                context['parent_2'] = self.object.childtocontact_set.get(order=1, link_with_child__in=parents_name_list)
            except ChildToContact.DoesNotExist:
                context['parent_2'] = None

        parents_exclude = []
        if context['parent_1']:
            parents_exclude.append(context['parent_1'].id)
        if context['parent_2']:
            parents_exclude.append(context["parent_2"].id)

        # Pickups
        cpickups = self.object.childtocontact_set.filter(contact__authorized_pick_up_child=True).exclude(
            id__in=parents_exclude)

        cpickup_nbr = 1
        for cpickup in cpickups:
            context['c_pickup{}'.format(cpickup_nbr)] = cpickup
            cpickup_nbr += 1

        cpickups_exclude = []
        for cpickup in cpickups:
            cpickups_exclude.append(cpickup.id)

        # Other contacts only
        c_contacts = self.object.childtocontact_set.filter(contact__to_contact_if_needed=True).exclude(
            id__in=parents_exclude).exclude(id__in=cpickups_exclude)

        c_contact_nbr = 1
        for c_contact in c_contacts:
            context['c_contact{}'.format(c_contact_nbr)] = c_contact
            c_contact_nbr += 1

        # Set current academic year.
        # No need to use timezone.localtime(timezone.now()) here.
        current_academic_year_start_date = None
        current_academic_year_end_date = None
        # +1 for accept 12 in range
        day_date = timezone.localdate()
        if day_date.month in range(8, 12 + 1):
            current_academic_year_start_date = make_aware(datetime.datetime(day_date.year, 8, 1))
            current_academic_year_end_date = make_aware(datetime.datetime(day_date.year + 1, 7, 31, 23, 59, 59, 999999))
        else:
            current_academic_year_start_date = make_aware(datetime.datetime(day_date.year - 1, 8, 1))
            current_academic_year_end_date = make_aware(datetime.datetime(day_date.year, 7, 31, 23, 59, 59, 999999))
        context['current_academic_year_start_date'] = current_academic_year_start_date
        context['current_academic_year_end_date'] = current_academic_year_end_date
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # assign the object to the view
        return super(ChildAdminPrintHealCardView, self).get(request)
