from django.forms import ModelForm
from opcalendar.models import (
    Event,
    EventMember,
    EventCategory,
    EventHost,
    EventVisibility,
)
from django.forms.widgets import TextInput
from django import forms
from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class EventForm(ModelForm):
    class Meta:
        model = Event
        # datetime-local is a HTML5 input type, format to make date time show on fields
        exclude = ["user", "eve_character", "created_date", "external"]

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["host"].queryset = EventHost.objects.filter(external=False)
        self.fields["event_visibility"].required = True
        self.fields["event_visibility"].queryset = EventVisibility.objects.filter(
            is_visible=True, is_active=True
        )
        try:
            self.initial["event_visibility"] = EventVisibility.objects.get(
                is_default=True
            )
        except Exception:
            logger.debug("Form defaults: No default visibility set")

        try:
            self.initial["host"] = EventHost.objects.get(is_default=True)
        except Exception:
            logger.debug("Form defaults: No default host set")


class EventEditForm(ModelForm):
    class Meta:
        model = Event
        # datetime-local is a HTML5 input type, format to make date time show on fields
        exclude = ["user", "eve_character", "created_date", "external"]

    def __init__(self, *args, **kwargs):
        super(EventEditForm, self).__init__(*args, **kwargs)

        self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["host"].queryset = EventHost.objects.filter(external=False)
        self.fields["event_visibility"].required = True
        self.fields["event_visibility"].queryset = EventVisibility.objects.filter(
            is_visible=True, is_active=True
        )


class SignupForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = EventMember
        fields = ["character"]


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = "__all__"


class EventVisibilityAdminForm(forms.ModelForm):
    class Meta:
        model = EventVisibility
        fields = "__all__"
        widgets = {
            "color": TextInput(attrs={"type": "color"}),
        }


class EventCategoryAdminForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = "__all__"
        widgets = {
            "color": TextInput(attrs={"type": "color"}),
        }
