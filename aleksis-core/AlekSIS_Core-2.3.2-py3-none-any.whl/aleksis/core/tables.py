from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A


class SchoolTermTable(tables.Table):
    """Table to list persons."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    name = tables.LinkColumn("edit_school_term", args=[A("id")])
    date_start = tables.Column()
    date_end = tables.Column()
    edit = tables.LinkColumn(
        "edit_school_term",
        args=[A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
        verbose_name=_("Actions"),
    )


class PersonsTable(tables.Table):
    """Table to list persons."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    first_name = tables.LinkColumn("person_by_id", args=[A("id")])
    last_name = tables.LinkColumn("person_by_id", args=[A("id")])


class GroupsTable(tables.Table):
    """Table to list groups."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    name = tables.LinkColumn("group_by_id", args=[A("id")])
    short_name = tables.LinkColumn("group_by_id", args=[A("id")])
    school_term = tables.Column()


class AdditionalFieldsTable(tables.Table):
    """Table to list group types."""

    class Meta:
        attrs = {"class": "responsive-table hightlight"}

    title = tables.LinkColumn("edit_additional_field_by_id", args=[A("id")])
    delete = tables.LinkColumn(
        "delete_additional_field_by_id",
        args=[A("id")],
        verbose_name=_("Delete"),
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red"}},
    )


class GroupTypesTable(tables.Table):
    """Table to list group types."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    name = tables.LinkColumn("edit_group_type_by_id", args=[A("id")])
    description = tables.LinkColumn("edit_group_type_by_id", args=[A("id")])
    delete = tables.LinkColumn(
        "delete_group_type_by_id", args=[A("id")], verbose_name=_("Delete"), text=_("Delete")
    )


class DashboardWidgetTable(tables.Table):
    """Table to list dashboard widgets."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    widget_name = tables.Column(accessor="pk")
    title = tables.LinkColumn("edit_dashboard_widget", args=[A("id")])
    active = tables.BooleanColumn(yesno="check,cancel", attrs={"span": {"class": "material-icons"}})
    delete = tables.LinkColumn(
        "delete_dashboard_widget",
        args=[A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
        verbose_name=_("Actions"),
    )

    def render_widget_name(self, value, record):
        return record._meta.verbose_name


class PermissionDeleteColumn(tables.LinkColumn):
    """Link column with label 'Delete'."""

    def __init__(self, url, **kwargs):
        super().__init__(
            url,
            args=[A("pk")],
            text=_("Delete"),
            attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
            verbose_name=_("Actions"),
            **kwargs
        )


class PermissionTable(tables.Table):
    """Table to list permissions."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    permission = tables.Column()


class ObjectPermissionTable(PermissionTable):
    """Table to list object permissions."""

    content_object = tables.Column()


class GlobalPermissionTable(PermissionTable):
    """Table to list global permissions."""

    pass


class GroupObjectPermissionTable(ObjectPermissionTable):
    """Table to list assigned group object permissions."""

    group = tables.Column()
    delete = PermissionDeleteColumn("delete_group_object_permission")


class UserObjectPermissionTable(ObjectPermissionTable):
    """Table to list assigned user object permissions."""

    user = tables.Column()
    delete = PermissionDeleteColumn("delete_user_object_permission")


class GroupGlobalPermissionTable(GlobalPermissionTable):
    """Table to list assigned global user permissions."""

    group = tables.Column()
    delete = PermissionDeleteColumn("delete_group_global_permission")


class UserGlobalPermissionTable(GlobalPermissionTable):
    """Table to list assigned global group permissions."""

    user = tables.Column()
    delete = PermissionDeleteColumn("delete_user_global_permission")
