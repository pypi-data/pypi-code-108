from typing import Sequence

from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _

from django_filters import CharFilter, FilterSet, ModelChoiceFilter, ModelMultipleChoiceFilter
from django_select2.forms import ModelSelect2Widget
from guardian.models import GroupObjectPermission, UserObjectPermission
from material import Layout, Row

from aleksis.core.models import Group, GroupType, Person, SchoolTerm


class MultipleCharFilter(CharFilter):
    """Filter for filtering multiple fields with one input.

    >>> multiple_filter = MultipleCharFilter(["name__icontains", "short_name__icontains"])
    """

    def filter(self, qs, value):  # noqa
        q = None
        for field in self.fields:
            if not q:
                q = Q(**{field: value})
            else:
                q = q | Q(**{field: value})
        return qs.filter(q)

    def __init__(self, fields: Sequence[str], *args, **kwargs):
        self.fields = fields
        super().__init__(self, *args, **kwargs)


class GroupFilter(FilterSet):
    school_term = ModelChoiceFilter(queryset=SchoolTerm.objects.all())
    group_type = ModelChoiceFilter(queryset=GroupType.objects.all())
    parent_groups = ModelMultipleChoiceFilter(queryset=Group.objects.all())

    search = MultipleCharFilter(["name__icontains", "short_name__icontains"], label=_("Search"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.layout = Layout(Row("search"), Row("school_term", "group_type", "parent_groups"))
        self.form.initial = {"school_term": SchoolTerm.current}


class PersonFilter(FilterSet):
    name = MultipleCharFilter(
        [
            "first_name__icontains",
            "additional_name__icontains",
            "last_name__icontains",
            "short_name__icontains",
            "user__username__icontains",
        ],
        label=_("Search by name"),
    )
    contact = MultipleCharFilter(
        [
            "street__icontains",
            "housenumber__icontains",
            "postal_code__icontains",
            "place__icontains",
            "phone_number__icontains",
            "mobile_number__icontains",
            "email__icontains",
        ],
        label=_("Search by contact details"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.layout = Layout(Row("name", "contact"), Row("sex", "primary_group"))

    class Meta:
        model = Person
        fields = ["sex", "primary_group"]


class PermissionFilter(FilterSet):
    """Common filter for permissions."""

    permission = ModelChoiceFilter(
        queryset=Permission.objects.all(),
        widget=ModelSelect2Widget(
            search_fields=["name__icontains", "codename__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        label=_("Permission"),
    )
    permission__content_type = ModelChoiceFilter(
        queryset=ContentType.objects.all(),
        widget=ModelSelect2Widget(
            search_fields=["app_label__icontains", "model__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        label=_("Content type"),
    )


class UserPermissionFilter(PermissionFilter):
    """Common filter for user permissions."""

    user = ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=ModelSelect2Widget(
            search_fields=["username__icontains", "first_name__icontains", "last_name__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        label=_("User"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.layout = Layout(Row("user", "permission", "permission__content_type"))

    class Meta:
        fields = ["user", "permission", "permission__content_type"]


class GroupPermissionFilter(PermissionFilter):
    """Common filter for group permissions."""

    group = ModelChoiceFilter(
        queryset=DjangoGroup.objects.all(),
        widget=ModelSelect2Widget(
            search_fields=[
                "name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        label=_("Group"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.layout = Layout(Row("group", "permission", "permission__content_type"))

    class Meta:
        fields = ["group", "permission", "permission__content_type"]


class UserGlobalPermissionFilter(UserPermissionFilter):
    """Filter for global user permissions."""

    class Meta(UserPermissionFilter.Meta):
        model = User.user_permissions.through


class GroupGlobalPermissionFilter(GroupPermissionFilter):
    """Filter for global group permissions."""

    class Meta(GroupPermissionFilter.Meta):
        model = DjangoGroup.permissions.through


class UserObjectPermissionFilter(UserPermissionFilter):
    """Filter for object user permissions."""

    class Meta(UserPermissionFilter.Meta):
        model = UserObjectPermission


class GroupObjectPermissionFilter(GroupPermissionFilter):
    """Filter for object group permissions."""

    class Meta(GroupPermissionFilter.Meta):
        model = GroupObjectPermission
