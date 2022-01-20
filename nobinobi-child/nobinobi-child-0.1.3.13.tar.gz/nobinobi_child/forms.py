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

import arrow
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Hidden, Field
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.utils.translation import gettext as _

from nobinobi_child.models import Absence, Child


class LoginAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(LoginAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = '/accounts/login/'
        self.helper.form_show_labels = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            AppendedText('username', '<i class="fas fa-user"></i>', placeholder=_("Username")),
            AppendedText('password', '<i class="fas fa-key"></i>', placeholder=_("Password")),
            Hidden('next', '/'),
            Submit("login", _("Sign In"), css_class='btn btn-primary btn-block btn-flat'),
        )


class AbsenceCreateForm(BSModalModelForm):
    child = forms.ModelChoiceField(label=_("Child"),
                                   queryset=Child.objects.filter(status=Child.STATUS.in_progress),
                                   )

    # type = forms.ModelChoiceField(
    #     queryset=AbsenceType.objects.all(),
    #     widget=ModelSelect2Widget(
    #         model=AbsenceType,
    #         search_fields=['name__icontains', 'group__name__icontains']
    #     )
    # )

    class Meta:
        model = Absence
        fields = ["child", "start_date", "end_date", "type"]
        widgets = {
            "start_date": DateTimePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY HH:mm"}),
            # "start_date": DateTimePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY HH:MM"}),
            "end_date": DateTimePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY HH:mm"}),
            # "end_date": DateTimePickerInput(options={"locale": "fr", "format": "DD/MM/YYYY HH:MM"}),
        }

    def __init__(self, *args, **kwargs):
        super(AbsenceCreateForm, self).__init__(*args, **kwargs)
        if not kwargs.get('initial', None):
            if not self.initial.get('start_date', None):
                self.initial['start_date'] = arrow.get(timezone.localtime()).replace(hour=6, minute=0,
                                                                                     second=0).strftime(
                    "%d/%m/%Y %H:%M")

            if not self.initial.get('end_date', None):
                self.initial['end_date'] = arrow.get(timezone.localtime()).replace(hour=22, minute=0,
                                                                                   second=0).strftime(
                    "%d/%m/%Y %H:%M")


class ChildPictureSelectForm(forms.ModelForm):
    child = forms.ModelChoiceField(
        label=_("Child"),
        queryset=Child.objects.filter(status=Child.STATUS.in_progress),
    )

    class Meta:
        model = Child
        fields = ("child",)

    def __init__(self, *args, **kwargs):
        super(ChildPictureSelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-child-picture-select'
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"

        self.helper.add_input(Submit('submit', _("Submit")))


class ChildPictureForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ("picture",)

    def __init__(self, *args, **kwargs):
        super(ChildPictureForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-child-picture-select'
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.form_method = 'post'
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-10"
        self.helper.attrs['enctype'] = "multipart/form-data"
        self.helper.layout = Layout(
            Field("picture"),
            Submit('submit', _("Submit"))
        )


class ChildPictureUpdateForm(BSModalModelForm):
    class Meta:
        model = Child
        fields = ("picture",)
