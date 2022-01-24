from datetime import datetime, time
from typing import Any, Callable, Dict, Sequence

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from allauth.account.forms import SignupForm
from allauth.account.utils import setup_user_email
from dj_cleavejs import CleaveWidget
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget, Select2Widget
from dynamic_preferences.forms import PreferenceForm
from guardian.shortcuts import assign_perm
from material import Fieldset, Layout, Row

from .mixins import ExtensibleForm, SchoolTermRelatedExtensibleForm
from .models import (
    AdditionalField,
    Announcement,
    DashboardWidget,
    Group,
    GroupType,
    OAuthApplication,
    Person,
    SchoolTerm,
)
from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .util.auth_helpers import AppScopes
from .util.core_helpers import get_site_preferences


class PersonForm(ExtensibleForm):
    """Form to edit or add a person object in the frontend."""

    layout = Layout(
        Fieldset(
            _("Base data"),
            "short_name",
            Row("user", "primary_group"),
            Row("first_name", "additional_name", "last_name"),
        ),
        Fieldset(_("Address"), Row("street", "housenumber"), Row("postal_code", "place")),
        Fieldset(_("Contact data"), "email", Row("phone_number", "mobile_number")),
        Fieldset(
            _("Advanced personal data"),
            Row("date_of_birth", "place_of_birth"),
            Row("sex"),
            Row("photo", "avatar"),
            "guardians",
        ),
    )

    class Meta:
        model = Person
        fields = [
            "user",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "street",
            "housenumber",
            "postal_code",
            "place",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "photo",
            "avatar",
            "guardians",
            "primary_group",
        ]
        widgets = {
            "user": Select2Widget(attrs={"class": "browser-default"}),
            "primary_group": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "guardians": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }

    new_user = forms.CharField(
        required=False, label=_("New user"), help_text=_("Create a new account")
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if (
            request
            and self.instance
            and not request.user.has_perm("core.change_person", self.instance)
        ):
            # Disable non-editable fields
            allowed_person_fields = get_site_preferences()["account__editable_fields_person"]
            for field in self.fields:
                if field not in allowed_person_fields:
                    self.fields[field].disabled = True

    def clean(self) -> None:
        user = get_user_model()

        if self.cleaned_data.get("new_user", None):
            if self.cleaned_data.get("user", None):
                # The user selected both an existing user and provided a name to create a new one
                self.add_error(
                    "new_user",
                    _("You cannot set a new username when also selecting an existing user."),
                )
            elif user.objects.filter(username=self.cleaned_data["new_user"]).exists():
                # The user tried to create a new user with the name of an existing user
                self.add_error("new_user", _("This username is already in use."))
            else:
                # Create new User object and assign to form field for existing user
                new_user_obj = user.objects.create_user(
                    self.cleaned_data["new_user"],
                    self.instance.email,
                    first_name=self.instance.first_name,
                    last_name=self.instance.last_name,
                )

                self.cleaned_data["user"] = new_user_obj


class EditGroupForm(SchoolTermRelatedExtensibleForm):
    """Form to edit an existing group in the frontend."""

    layout = Layout(
        Fieldset(_("School term"), "school_term"),
        Fieldset(_("Common data"), "name", "short_name", "group_type"),
        Fieldset(_("Persons"), "members", "owners", "parent_groups"),
        Fieldset(_("Additional data"), "additional_fields"),
        Fieldset(_("Photo"), "photo", "avatar"),
    )

    class Meta:
        model = Group
        exclude = []
        widgets = {
            "members": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "owners": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "parent_groups": ModelSelect2MultipleWidget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "additional_fields": ModelSelect2MultipleWidget(
                search_fields=[
                    "title__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }


class AnnouncementForm(ExtensibleForm):
    """Form to create or edit an announcement in the frontend."""

    valid_from = forms.DateTimeField(required=False)
    valid_until = forms.DateTimeField(required=False)

    valid_from_date = forms.DateField(label=_("Date"))
    valid_from_time = forms.TimeField(label=_("Time"))

    valid_until_date = forms.DateField(label=_("Date"))
    valid_until_time = forms.TimeField(label=_("Time"))

    persons = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        label=_("Persons"),
        required=False,
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Groups"),
        required=False,
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )

    layout = Layout(
        Fieldset(
            _("From when until when should the announcement be displayed?"),
            Row("valid_from_date", "valid_from_time", "valid_until_date", "valid_until_time"),
        ),
        Fieldset(_("Who should see the announcement?"), Row("groups", "persons")),
        Fieldset(_("Write your announcement:"), "title", "description"),
    )

    def __init__(self, *args, **kwargs):
        if "instance" not in kwargs:
            # Default to today and whole day for new announcements
            kwargs["initial"] = {
                "valid_from_date": datetime.now(),
                "valid_from_time": time(0, 0),
                "valid_until_date": datetime.now(),
                "valid_until_time": time(23, 59),
            }
        else:
            announcement = kwargs["instance"]

            # Fill special fields from given announcement instance
            kwargs["initial"] = {
                "valid_from_date": announcement.valid_from.date(),
                "valid_from_time": announcement.valid_from.time(),
                "valid_until_date": announcement.valid_until.date(),
                "valid_until_time": announcement.valid_until.time(),
                "groups": announcement.get_recipients_for_model(Group),
                "persons": announcement.get_recipients_for_model(Person),
            }

        super().__init__(*args, **kwargs)

        self.fields["groups"].queryset = Group.objects.for_current_school_term_or_all()

    def clean(self):
        data = super().clean()

        # Combine date and time fields into datetime objects
        valid_from = datetime.combine(data["valid_from_date"], data["valid_from_time"])
        valid_until = datetime.combine(data["valid_until_date"], data["valid_until_time"])

        # Sanity check validity range
        if valid_until < datetime.now():
            raise ValidationError(
                _("You are not allowed to create announcements which are only valid in the past.")
            )
        elif valid_from > valid_until:
            raise ValidationError(
                _("The from date and time must be earlier then the until date and time.")
            )

        # Inject real time data if all went well
        data["valid_from"] = valid_from
        data["valid_until"] = valid_until

        # Ensure at least one group or one person is set as recipient
        if "groups" not in data and "persons" not in data:
            raise ValidationError(_("You need at least one recipient."))

        # Unwrap all recipients into single user objects and generate final list
        data["recipients"] = []
        data["recipients"] += data.get("groups", [])
        data["recipients"] += data.get("persons", [])

        return data

    def save(self, _=False):
        # Save announcement, respecting data injected in clean()
        if self.instance is None:
            self.instance = Announcement()
        self.instance.valid_from = self.cleaned_data["valid_from"]
        self.instance.valid_until = self.cleaned_data["valid_until"]
        self.instance.title = self.cleaned_data["title"]
        self.instance.description = self.cleaned_data["description"]
        self.instance.save()

        # Save recipients
        self.instance.recipients.all().delete()
        for recipient in self.cleaned_data["recipients"]:
            self.instance.recipients.create(recipient=recipient)
        self.instance.save()

        return self.instance

    class Meta:
        model = Announcement
        exclude = []


class ChildGroupsForm(forms.Form):
    """Inline form for group editing to select child groups."""

    child_groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())


class SitePreferenceForm(PreferenceForm):
    """Form to edit site preferences."""

    registry = site_preferences_registry


class PersonPreferenceForm(PreferenceForm):
    """Form to edit preferences valid for one person."""

    registry = person_preferences_registry


class GroupPreferenceForm(PreferenceForm):
    """Form to edit preferences valid for members of a group."""

    registry = group_preferences_registry


class EditAdditionalFieldForm(forms.ModelForm):
    """Form to manage additional fields."""

    class Meta:
        model = AdditionalField
        exclude = []


class EditGroupTypeForm(forms.ModelForm):
    """Form to manage group types."""

    class Meta:
        model = GroupType
        exclude = []


class SchoolTermForm(ExtensibleForm):
    """Form for managing school years."""

    layout = Layout("name", Row("date_start", "date_end"))

    class Meta:
        model = SchoolTerm
        exclude = []


class DashboardWidgetOrderForm(ExtensibleForm):
    pk = forms.ModelChoiceField(
        queryset=None,
        widget=forms.HiddenInput(attrs={"class": "pk-input"}),
    )
    order = forms.IntegerField(initial=0, widget=forms.HiddenInput(attrs={"class": "order-input"}))

    class Meta:
        model = DashboardWidget
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set queryset here to prevent problems with not migrated database due to special queryset
        self.fields["pk"].queryset = DashboardWidget.objects.all()


DashboardWidgetOrderFormSet = forms.formset_factory(
    form=DashboardWidgetOrderForm, max_num=0, extra=0
)


class InvitationCodeForm(forms.Form):
    """Form to enter an invitation code."""

    code = forms.CharField(
        label=_("Invitation code"),
        help_text=_("Please enter your invitation code."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Calculate number of fields
        length = get_site_preferences()["auth__invite_code_length"]
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        blocks = [
            packet_size,
        ] * length

        self.fields["code"].widget = CleaveWidget(blocks=blocks, delimiter="-", uppercase=True)


class SelectPermissionForm(forms.Form):
    """Select a permission to assign."""

    selected_permission = forms.ModelChoiceField(
        queryset=Permission.objects.all(),
        widget=ModelSelect2Widget(
            search_fields=["name__icontains", "codename__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )


class AssignPermissionForm(forms.Form):
    """Assign a permission to user/groups for all/some objects."""

    layout = Layout(
        Fieldset(_("Who should get the permission?"), "groups", "persons"),
        Fieldset(_("On what?"), "objects", "all_objects"),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=ModelSelect2MultipleWidget(
            search_fields=["name__icontains", "short_name__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        required=False,
    )
    persons = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        required=False,
    )

    objects = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        label=_("Select objects which the permission should be granted for:"),
    )
    all_objects = forms.BooleanField(
        required=False, label=_("Grant the permission for all objects")
    )

    def clean(self) -> Dict[str, Any]:
        """Clean form to ensure that at least one target and one type is selected."""
        cleaned_data = super().clean()
        if not cleaned_data.get("persons") and not cleaned_data.get("groups"):
            raise ValidationError(
                _("You must select at least one group or person which should get the permission.")
            )

        if not cleaned_data.get("objects") and not cleaned_data.get("all_objects"):
            raise ValidationError(
                _("You must grant the permission to all objects and/" "or to some objects.")
            )
        return cleaned_data

    def __init__(self, *args, permission: Permission, **kwargs):
        self.permission = permission
        super().__init__(*args, **kwargs)

        model_class = self.permission.content_type.model_class()
        if model_class._meta.managed and not model_class._meta.abstract:
            queryset = model_class.objects.all()
        else:
            # The following queryset is just a dummy one. It has no real meaning.
            # We need it as there are permissions without real objects,
            # but we want to use the same form.
            queryset = Site.objects.none()
        self.fields["objects"].queryset = queryset
        search_fields = getattr(model_class, "get_filter_fields", lambda: [])()

        # Use select2 only if there are any searchable fields as it can't work without
        if search_fields:
            self.fields["objects"].widget = ModelSelect2MultipleWidget(
                search_fields=search_fields,
                queryset=queryset,
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            )

    def save_perms(self):
        """Save permissions for selected user/groups and selected/all objects."""
        persons = self.cleaned_data["persons"]
        groups = self.cleaned_data["groups"]
        all_objects = self.cleaned_data["all_objects"]
        objects = self.cleaned_data["objects"]
        permission_name = f"{self.permission.content_type.app_label}.{self.permission.codename}"
        created = 0

        # Create permissions for users
        for person in persons:
            if getattr(person, "user", None):
                # Global permission
                if all_objects:
                    assign_perm(permission_name, person.user)
                # Object permissions
                for instance in objects:
                    assign_perm(permission_name, person.user, instance)

        # Create permissions for users
        for group in groups:
            django_group = group.django_group
            # Global permission
            if all_objects:
                assign_perm(permission_name, django_group)
            # Object permissions
            for instance in objects:
                assign_perm(permission_name, django_group, instance)


class AccountRegisterForm(SignupForm, ExtensibleForm):
    """Form to register new user accounts."""

    class Meta:
        model = Person
        fields = [
            "first_name",
            "additional_name",
            "last_name",
            "street",
            "housenumber",
            "postal_code",
            "place",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "photo",
            "mobile_number",
            "phone_number",
            "short_name",
            "description",
        ]

    layout = Layout(
        Fieldset(
            _("Base data"),
            Row("first_name", "additional_name", "last_name"),
            "short_name",
        ),
        Fieldset(
            _("Adress data"),
            Row("street", "housenumber"),
            Row("postal_code", "place"),
        ),
        Fieldset(_("Contact data"), Row("mobile_number", "phone_number")),
        Fieldset(
            _("Additional data"),
            Row("date_of_birth", "place_of_birth"),
            Row("sex", "photo"),
            "description",
        ),
        Fieldset(
            _("Account data"),
            "username",
            Row("email", "email2"),
            Row("password1", "password2"),
        ),
    )

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    if settings.SIGNUP_PASSWORD_ENTER_TWICE:
        password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(AccountRegisterForm, self).__init__(*args, **kwargs)

        if request.session.get("account_verified_email"):
            email = request.session["account_verified_email"]

            try:
                person = Person.objects.get(email=email)
            except (Person.DoesNotExist, Person.MultipleObjectsReturned):
                raise SuspiciousOperation()

            self.fields["email"].disabled = True
            self.fields["email2"].disabled = True

            if person:
                available_fields = [field.name for field in Person._meta.get_fields()]
                for field in self.fields:
                    if field in available_fields and getattr(person, field):
                        self.fields[field].disabled = True
                        self.fields[field].initial = getattr(person, field)

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        # Create person
        data = {}
        for field in Person._meta.get_fields():
            if field.name in self.cleaned_data:
                data[field.name] = self.cleaned_data[field.name]
        if not Person.objects.filter(email=data["email"]):
            _person, created = Person.objects.update_or_create(user=user, **data)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class ActionForm(forms.Form):
    """Generic form for executing actions on multiple items of a queryset.

    This should be used together with a ``Table`` from django-tables2
    which includes a ``SelectColumn``.

    The queryset can be defined in two different ways:
    You can use ``get_queryset`` or provide ``queryset`` as keyword argument
    at the initialization of this form class.
    If both are declared, it will use the keyword argument.

    Any actions can be defined using the ``actions`` class attribute
    or overriding the method ``get_actions``.
    The actions use the same syntax like the Django Admin actions with one important difference:
    Instead of the related model admin,
    these actions will get the related ``ActionForm`` as first argument.
    Here you can see an example for such an action:

    .. code-block:: python

        from django.utils.translation import gettext as _

        def example_action(form, request, queryset):
            # Do something with this queryset

        example_action.short_description = _("Example action")

    If you can include the ``ActionForm`` like any other form in your views,
    but you must add the request as first argument.
    When the form is valid, you should run ``execute``:

    .. code-block:: python

        from aleksis.core.forms import ActionForm

        def your_view(request, ...):
            # Something
            action_form = ActionForm(request, request.POST or None, ...)
            if request.method == "POST" and form.is_valid():
                form.execute()

            # Something
    """

    layout = Layout("action")
    actions = []

    def get_actions(self) -> Sequence[Callable]:
        """Get all defined actions."""
        return self.actions

    def _get_actions_dict(self) -> dict[str, Callable]:
        """Get all defined actions as dictionary."""
        return {value.__name__: value for value in self.get_actions()}

    def _get_action_choices(self) -> list[tuple[str, str]]:
        """Get all defined actions as Django choices."""
        return [
            (value.__name__, getattr(value, "short_description", value.__name__))
            for value in self.get_actions()
        ]

    def get_queryset(self) -> QuerySet:
        """Get the related queryset."""
        raise NotImplementedError("Queryset necessary.")

    action = forms.ChoiceField(choices=[])
    selected_objects = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, request: HttpRequest, *args, queryset: QuerySet = None, **kwargs):
        self.request = request
        self.queryset = queryset if isinstance(queryset, QuerySet) else self.get_queryset()
        super().__init__(*args, **kwargs)
        self.fields["selected_objects"].queryset = self.queryset
        self.fields["action"].choices = self._get_action_choices()

    def execute(self) -> bool:
        """Execute the selected action on all selected objects.

        :return: If the form is not valid, it will return ``False``.
        """
        if self.is_valid():
            data = self.cleaned_data["selected_objects"]
            action = self._get_actions_dict()[self.cleaned_data["action"]]
            action(None, self.request, data)
            return True
        return False


class ListActionForm(ActionForm):
    """Generic form for executing actions on multiple items of a list of dictionaries.

    Sometimes you want to implement actions for data from different sources
    than querysets or even querysets from multiple models. For these cases,
    you can use this form.

    To provide an unique identification of each item, the dictionaries **must**
    include the attribute ``pk``. This attribute has to be unique for the whole list.
    If you don't mind this aspect, this will cause unexpected behavior.

    Any actions can be defined as described in ``ActionForm``, but, of course,
    the last argument won't be a queryset but a list of dictionaries.

    For further information on usage, you can take a look at ``ActionForm``.
    """

    selected_objects = forms.MultipleChoiceField(choices=[])

    def get_queryset(self):
        # Return None in order not to raise an unwanted exception
        return None

    def _get_dict(self) -> dict[str, dict]:
        """Get the items sorted by pk attribute."""
        return {item["pk"]: item for item in self.items}

    def _get_choices(self) -> list[tuple[str, str]]:
        """Get the items as Django choices."""
        return [(item["pk"], item["pk"]) for item in self.items]

    def _get_real_items(self, items: Sequence[dict]) -> list[dict]:
        """Get the real dictionaries from a list of pks."""
        items_dict = self._get_dict()
        real_items = []
        for item in items:
            if item not in items_dict:
                raise ValidationError(_("No valid selection."))
            real_items.append(items_dict[item])
        return real_items

    def clean_selected_objects(self) -> list[dict]:
        data = self.cleaned_data["selected_objects"]
        items = self._get_real_items(data)
        return items

    def __init__(self, request: HttpRequest, items, *args, **kwargs):
        self.items = items
        super().__init__(request, *args, **kwargs)
        self.fields["selected_objects"].choices = self._get_choices()


class OAuthApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["allowed_scopes"].widget = forms.SelectMultiple(
            choices=list(AppScopes().get_all_scopes().items())
        )

    class Meta:
        model = OAuthApplication
        fields = (
            "name",
            "icon",
            "client_id",
            "client_secret",
            "client_type",
            "algorithm",
            "allowed_scopes",
            "redirect_uris",
            "skip_authorization",
        )
