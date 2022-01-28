#    Copyright (C) Prolibre Sarl 2019 <Florian Alu> <alu@prolibre.com>
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License and any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
from bootstrap_datepicker_plus.widgets import TimePickerInput, DatePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin, PopRequestMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelForm
from django.forms.renderers import get_default_renderer
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_select2.forms import ModelSelect2Widget
from nobinobi_child.models import Classroom, Child
from nobinobi_staff.models import Staff

from nobinobi_daily_follow_up.models import Reception, MealDailyFollowUp, Nap, LotionDailyFollowUp, DiaperChange, \
    Activity, Medication, DailyFollowUp, Presence, TypeActivity, GiveMedication, DailyFollowUpToMedication, \
    EarlyTroubleshooting
from nobinobi_daily_follow_up.utils import GroupedModelMultiChoiceField


class FaTimePickerInput(TimePickerInput):
    template_name = 'nobinobi_daily_follow_up/bootstrap_datepicker_plus/time-picker.html'


class InlineImgRadioInput(forms.RadioSelect):
    template_name = 'nobinobi_daily_follow_up/forms/widgets/inline-img-radio.html'
    option_template_name = 'nobinobi_daily_follow_up/forms/widgets/inline-img-radio-input.html'


class InlineImgMealCheckboxInput(forms.CheckboxSelectMultiple):
    template_name = 'nobinobi_daily_follow_up/forms/widgets/inline_img_checkbox_select.html'
    option_template_name = 'nobinobi_daily_follow_up/forms/widgets/inline_img_checkbox_option.html'

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        context = self.get_context(name, value, attrs)
        for opt in context["widget"]["optgroups"]:
            opt[1][0]['obj'] = self.choices.queryset.get(name=opt[1][0]['label'])
        if renderer is None:
            renderer = get_default_renderer()
        return mark_safe(renderer.render(self.template_name, context))


class PresenceChoiceForm(forms.Form):
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.all(),
        widget=ModelSelect2Widget(
            model=Classroom,
            search_fields=["name__icontains"],
            data_view='nobinobi_daily_follow_up:classroom_allowed_json'
        )
    )

    class Meta:
        fields = ["classroom", ]

    def __init__(self, request=None, *args, **kwargs):
        super(PresenceChoiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.helper.form_tag = True
        # self.helper.layout = Layout(        )
        self.helper.add_input(Submit("submit", _("Submit")))


class PresenceCreateForm(BSModalModelForm):
    # child = forms.ModelChoiceField(
    #     queryset=Child.objects.filter(status=Child.STATUS.in_progress),
    #     widget=ModelSelect2Widget(
    #         model=Child,
    #         search_fields=['first_name__icontains']
    #     )
    # )

    class Meta:
        model = Presence
        fields = ("child", "arrival_time", "departure_time")

        widgets = {
            "arrival_time": FaTimePickerInput(options={"locale": "fr"}).start_of('presence days'),
            "departure_time": FaTimePickerInput(options={"locale": "fr"}).end_of('presence days'),
        }

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop("date", None)
        self.classroom = kwargs.pop("classroom", None)
        self.child_pk = kwargs.pop("child_pk", None)
        if self.classroom:
            if self.child_pk is not None:
                kwargs.update(initial={
                    'child': [self.child_pk],
                    'arrival_time': timezone.localtime().strftime("%H:%M")
                })

        super(PresenceCreateForm, self).__init__(*args, **kwargs)
        # if not preselect image before add
        if self.classroom:
            if self.child_pk is None:
                self.fields['child'].queryset = Child.objects.filter(classroom=self.classroom,
                                                                     status=Child.STATUS.in_progress)


    def save(self, commit=True):
        if not self.request.is_ajax():
            instance = super(PresenceCreateForm, self).save(commit=False)
            instance.date = self.date
            instance.classroom = self.classroom
            try:
                Presence.objects.get(child=instance.child, date=self.date)
            except Presence.DoesNotExist:
                # medication
                return super(PresenceCreateForm, self).save(commit=commit)
            else:
                messages.error(request=self.request, message=_("Presence already exists."))
                return super(PresenceCreateForm, self).save(commit=False)
        else:
            instance = super(PresenceCreateForm, self).save(commit=False)
        return instance


class PresenceDepartureForm(CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Presence
        fields = ("departure_time",)

        widgets = {
            "departure_time": FaTimePickerInput(options={"locale": "fr"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.date = kwargs.pop("date", None)
        self.classroom = kwargs.pop("classroom", None)
        self.child_pk = kwargs.pop("child_pk", None)
        self.obj = kwargs.pop("obj", None)
        if not kwargs["instance"].departure_time:
            kwargs.update(initial={
                'departure_time': timezone.localtime().strftime("%H:%M")
            })
        super(PresenceDepartureForm, self).__init__(*args, **kwargs)

    def clean_departure_time(self):
        data = self.cleaned_data['departure_time']
        # data = Time()
        if data <= self.obj.arrival_time:
            raise ValidationError(_("The departure time is less than the arrival time."), code="invalid")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data


class PresenceintermediateDepartureForm(CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Presence
        fields = ("intermediate_departure_time", "intermediate_arrival_time")

        widgets = {
            "intermediate_departure_time": FaTimePickerInput(options={"locale": "fr"}).start_of(
                'presence days intermediate'),
            "intermediate_arrival_time": FaTimePickerInput(options={"locale": "fr"}).end_of(
                'presence days intermediate'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.date = kwargs.pop("date", None)
        self.classroom = kwargs.pop("classroom", None)
        self.child_pk = kwargs.pop("child_pk", None)
        if not kwargs["instance"].intermediate_departure_time:
            kwargs.update(initial={
                'intermediate_departure_time': timezone.localtime().strftime("%H:%M")
            })
        super(PresenceintermediateDepartureForm, self).__init__(*args, **kwargs)


class ReceptionForm(BSModalModelForm):
    class Meta:
        model = Reception
        fields = ["wake_up_time", "breakfast", "breakfast_time", "sleep", "sick", "fever", "condition", "comment"]
        widgets = {
            "breakfast_time": FaTimePickerInput(options={"locale": "fr"}),
            "breakfast": InlineImgRadioInput(),
            "sleep": InlineImgRadioInput(),
            "condition": InlineImgRadioInput(),
        }


class MealDailyFollowUpForm(BSModalModelForm):
    class Meta:
        model = MealDailyFollowUp
        fields = ["snack_time", "snack_quality", "snack_meals", "lunch_time", "lunch_quality", "lunch_meals",
                  "afternoon_snack_time", "afternoon_snack_quality", "afternoon_snack_meals", "comment"]
        widgets = {
            "snack_quality": InlineImgRadioInput(),
            "snack_meals": InlineImgMealCheckboxInput(),
            "lunch_quality": InlineImgRadioInput(),
            "lunch_meals": InlineImgMealCheckboxInput(),
            "afternoon_snack_quality": InlineImgRadioInput(),
            "afternoon_snack_meals": InlineImgMealCheckboxInput(),
            "snack_time": FaTimePickerInput(options={"locale": "fr"}),
            "lunch_time": FaTimePickerInput(options={"locale": "fr"}),
            "afternoon_snack_time": FaTimePickerInput(options={"locale": "fr"}),
        }

    def full_clean(self):
        return super(MealDailyFollowUpForm, self).full_clean()

    # def __init__(self, *args, **kwargs):
    #     super(MealDailyFollowUpForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_method = 'post'
    #     self.helper.form_show_labels = True
    #     self.helper.form_tag = False
    #     self.helper.layout = Layout(
    #         Div(
    #             Field("snack_time"),
    #             InlineImgRadioInput("snack_quality"),
    #             InlineCheckboxesImage("snack_meals"),
    #             Field("lunch_time"),
    #             InlineRadiosImage("lunch_quality"),
    #             InlineCheckboxesImage("lunch_meals"),
    #             Field("afternoon_snack_time"),
    #             InlineRadiosImage("afternoon_snack_quality"),
    #             InlineCheckboxesImage("afternoon_snack_meals"),
    #             Field("comment")
    #             , css_class="mx-auto col-md-12"
    #         )
    #     )


class NapForm(BSModalModelForm):
    class Meta:
        model = Nap
        fields = ["start_time", "end_time"]
        widgets = {
            # "start_time": TimePickerInput(options={"locale": "fr"}),
            "start_time": FaTimePickerInput(options={"locale": "fr"}).start_of('nap time'),
            # "end_time": FaTimePickerInput(options={"locale": "fr"}),
            "end_time": FaTimePickerInput(options={"locale": "fr"}).end_of('nap time'),
        }


class DiaperChangeForm(BSModalModelForm):
    class Meta:
        model = DiaperChange
        fields = ["hour", "feces"]
        widgets = {
            "hour": FaTimePickerInput(
                options={"locale": "fr"}),
            "feces": InlineImgRadioInput(),
        }


class LotionDailyFollowUpForm(BSModalModelForm):
    class Meta:
        model = LotionDailyFollowUp
        fields = ["lotion", "comment"]


class ActivityForm(BSModalModelForm):
    class Meta:
        model = Activity
        fields = ["type_activity", "comment"]


class DailyFollowUpToMedicationForm(BSModalModelForm):
    class Meta:
        model = DailyFollowUpToMedication
        fields = ["medication", "daily_follow_up"]


class MedicationForm(BSModalModelForm):
    class Meta:
        model = Medication
        fields = ["from_date", "end_date", "type_medication", "comment", "attachment"]
        widgets = {
            "from_date": DatePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY"}).start_of('medic days'),
            "end_date": DatePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY"}).end_of('medic days'),
        }

    def __init__(self, *args, **kwargs):
        self.daily_follow_up = kwargs.pop("daily_follow_up", None)
        self.child = kwargs.pop("child", None)
        super(MedicationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.request.is_ajax():
            self.instance.child_id = self.child
            instance = super(MedicationForm, self).save(commit=commit)
            #     ici on cree la jonction de table avec les medocs
            dtm, created = DailyFollowUpToMedication.objects.get_or_create(
                medication_id=instance.pk,
                daily_follow_up_id=self.daily_follow_up
            )
        else:
            instance = super(MedicationForm, self).save(commit=False)
        return instance


class GiveMedicationForm(BSModalModelForm):
    staff = forms.ModelChoiceField(label=_("Staff"), queryset=Staff.objects.filter(status=Staff.STATUS.active),
                                   required=False)

    class Meta:
        model = GiveMedication
        fields = ["staff", "give_hour", "given_hour"]
        widgets = {
            "give_hour": FaTimePickerInput(options={"locale": "fr"}),
            "given_hour": FaTimePickerInput(options={"locale": "fr"}),
        }

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop("date", None)
        super(GiveMedicationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.request.is_ajax():
            self.instance.date = self.date
            instance = super(GiveMedicationForm, self).save(commit=commit)
        else:
            instance = super(GiveMedicationForm, self).save(commit=False)
        return instance


class GiveMedicationDelayForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.Form):
    check = forms.BooleanField(
        label=_("Check"),
        help_text=_("By checking this box you confirm that you want to delay taking the medication."),
        required=True
    )

    class Meta:
        fields = ["check", ]

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop("date", None)
        self.classroom = kwargs.pop("classroom", None)
        super(GiveMedicationDelayForm, self).__init__(*args, **kwargs)


class DailyFollowUpForm(BSModalModelForm):
    class Meta:
        model = DailyFollowUp
        fields = ["important", "comment"]


class ChoiceChildDateForm(forms.Form):
    child = forms.ModelChoiceField(
        queryset=Child.objects.filter(status=Child.STATUS.in_progress),
        label=_("Child"),
        widget=ModelSelect2Widget(
            model=Child,
            queryset=Child.objects.filter(status=Child.STATUS.in_progress),
            search_fields=['first_name__icontains'],
        ),
        required=True
    )

    date = forms.DateField(
        label=_("Date"),
        widget=DatePickerInput(options={
            "locale": "fr",
            "format": "DD/MM/YYYY"
        }),
    )

    class Meta:
        fields = ("child", "date")

    def __init__(self, *args, **kwargs):
        super(ChoiceChildDateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'id-choice-child-date-form'
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"
        self.helper.layout = Layout(
            Div(
                Field("child"),
                Field("date"),
                Submit('submit', _('Submit'))
                , css_class="mx-auto col-md-10"
            )
        )
        # self.helper.add_input(Submit('submit', _("Submit")))


class ChoiceClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ("id",)

    def __init__(self, *args, **kwargs):
        # get userid from view
        userid = kwargs.pop("userid")
        super(ChoiceClassroomForm, self).__init__(*args, **kwargs)
        user = get_user_model()
        user = user.objects.get(id=userid)
        group = user.groups.values_list('id', flat=True)

        # create field id for form with only the child class of login
        self.fields['id'] = forms.ModelChoiceField(
            label=_("Classroom"),
            queryset=Classroom.objects.filter(
                Q(allowed_login=userid) | Q(allowed_group_login__in=group)
            ).distinct()
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-choice-classroom-index-form'
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"

        self.helper.add_input(Submit('submit', _("Submit")))


class GroupActivityForm(ModelForm):
    """
        :param cr: database cursor
        :param uid: current user id
        :param ids: list of ids
        :rtype: dictionary with a

        This function is used for mettre a jourles information des activites
    """
    children_get_name = GroupedModelMultiChoiceField(label=_("Name of children") + ":", queryset=None,
                                                     group_by_field='age_group')
    activity = GroupedModelMultiChoiceField(
        label=_("Activity"),
        queryset=TypeActivity.objects.filter().order_by("group"),
        group_by_field='group',
        required=True,
    )
    comment = forms.CharField(label=_("Comment"), widget=forms.Textarea(), required=False)

    class Meta:
        fields = ["children_get_name", 'activity', 'comment']
        model = Activity

    def __init__(self, *args, **kwargs):
        # on recupere les kwargs fourni par la vue
        self.classroom_id = kwargs.pop('classroom_id', None)

        super(GroupActivityForm, self).__init__(*args, **kwargs)
        # Redefinition de la query qui get les enfants qui sont dans le groupe
        # fournie par la page d'avant dans le url
        self.fields['children_get_name'].queryset = Child.objects.filter(
            classroom_id=self.classroom_id, status=Child.STATUS.in_progress).order_by("age_group", 'first_name',
                                                                                      'last_name')
        self.fields['children_get_name'].initial = [u for u in self.fields['children_get_name'].queryset]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"

        self.helper.add_input(Submit('submit', _("Submit")))


class GroupDailyFollowUpForm(ModelForm):
    """
        :param cr: database cursor
        :param uid: current user id
        :param ids: list of ids
        :rtype: dictionary with a

        This function is used for mettre a jourles information des activites
    """
    children_get_name = GroupedModelMultiChoiceField(label=_("Name of children") + ":", queryset=None,
                                                     group_by_field='age_group')
    comment = forms.CharField(label=_("Comment"), widget=forms.Textarea())
    important = forms.BooleanField(label=_("Important"), required=False)

    class Meta:
        fields = ["children_get_name", 'comment', 'important']
        model = DailyFollowUp

    def __init__(self, *args, **kwargs):
        # on recupere les kwargs fourni par la vue
        self.classroom_id = kwargs.pop('classroom_id', None)

        super(GroupDailyFollowUpForm, self).__init__(*args, **kwargs)
        # Redefinition de la query qui get les enfants qui sont dans le groupe
        # fournie par la page d'avant dans le url
        self.fields['children_get_name'].queryset = Child.objects.filter(
            classroom_id=self.classroom_id, status=Child.STATUS.in_progress).order_by("age_group", 'first_name',
                                                                                      'last_name')
        self.fields['children_get_name'].initial = [u for u in self.fields['children_get_name'].queryset]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"

        self.helper.add_input(Submit('submit', _("Submit")))


class MultiDayMedicationForm(ModelForm):
    give_hour = forms.TimeField(label=_("Give hour"), widget=TimePickerInput(options={"locale": "fr"}))
    give_hour2 = forms.TimeField(label=_("Give hour") + " 2", widget=TimePickerInput(options={"locale": "fr"}),
                                 required=False)
    give_hour3 = forms.TimeField(label=_("Give hour") + " 3", widget=TimePickerInput(options={"locale": "fr"}),
                                 required=False)
    give_hour4 = forms.TimeField(label=_("Give hour") + " 4", widget=TimePickerInput(options={"locale": "fr"}),
                                 required=False)
    give_hour5 = forms.TimeField(label=_("Give hour") + " 5", widget=TimePickerInput(options={"locale": "fr"}),
                                 required=False)
    child = forms.ModelChoiceField(
        queryset=Child.objects.filter(status=Child.STATUS.in_progress).order_by("age_group",
                                                                                'first_name',
                                                                                'last_name'),
        label=_("Child"),
        widget=ModelSelect2Widget(
            model=Child,
            queryset=Child.objects.filter(status=Child.STATUS.in_progress).order_by("age_group",
                                                                                    'first_name',
                                                                                    'last_name'),
            search_fields=['first_name__icontains', 'last_name__icontains'],
        ),
        required=True
    )

    class Meta:
        model = Medication
        fields = ["child", "from_date", "end_date", "type_medication", "attachment", "comment", "give_hour",
                  "give_hour2", "give_hour3", "give_hour4", "give_hour5", ]
        widgets = {
            "from_date": DatePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY"}).start_of('medic days'),
            "end_date": DatePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY"}).end_of('medic days'),
        }

    def __init__(self, *args, **kwargs):
        super(MultiDayMedicationForm, self).__init__(*args, **kwargs)
        # Redefinition de la query qui get les enfants qui sont dans le groupe
        # fournie par la page d'avant dans le url

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"

        self.helper.add_input(Submit('submit', _("Submit")))


class EarlyTroubleshootingForm(BSModalModelForm):
    date = forms.DateField(
        label=_("Date"),
        widget=DatePickerInput(options={
            "locale": "fr",
            "format": "DD/MM/YYYY"
        }),
    )

    class Meta:
        model = EarlyTroubleshooting
        fields = ("child", "date", "periods")

    def clean_periods(self):
        periods = self.cleaned_data.get("periods")
        for period in periods:
            if period.weekday != self.cleaned_data['date'].isoweekday():
                # Good
                periods = periods.exclude(id=period.id)
        if periods.count() > 0:
            return periods
        else:
            raise ValidationError(_("No valid period selected."), code="invalid")
