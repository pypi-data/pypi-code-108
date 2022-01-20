from functools import wraps

from django.forms.utils import pretty_name
from django.utils.html import format_html

from jnt_django_toolbox.admin.helpers import urls
from jnt_django_toolbox.helpers.objects import getattr_nested


def admin_changelist_link(
    attr,
    short_description=None,
    empty_description="-",
    query_string=None,
):
    """Render a link to the list of a related model in the admin changelist.

    ``attr (str)``
        Name of the related field.
    ``short_description (str)``
        Field display name.
        Default value: None.
    ``empty_description (str)``
        Value to display if the related field is None.
        Default value: -.
    ``query_string (function)``
        Optional callback for adding a query string to the link.
        Receives the object and should return a query string.
        Default value: None.

    The wrapped method receives the related object and
    should return the link text.

    Usage::

        from jnt_admin_tools.decorators import admin_changelist_link
        from django.contrib import admin
        from test_app.models import Bar

        @admin.register(Bar)
        class BarAdmin(admin.ModelAdmin):
            fields = ('name', 'foos', 'custom_field')
            readonly_fields = ('foos', 'custom_field')

            @admin_changelist_link(
                'foos',
                query_string=lambda bar: 'bar_id={0}'.format(bar.pk)
            )
            def foos(self, foos):
                return ', '.join(str(foo) for foo in foos.all())

    .. image:: images/decorators/decorator_admin_changelist_link.png
    """

    def wrap(func):  # noqa: WPS430
        @wraps(func)
        def field_func(self, obj):  # noqa: WPS430
            related_obj = getattr_nested(obj, attr)
            if related_obj is None:
                return empty_description
            url = urls.admin_changelist_url(related_obj.model)
            if query_string:
                url = "{0}?{1}".format(url, query_string(obj))
            return format_html(
                '<a href="{0}">{1}</a>',
                url,
                func(self, related_obj),
            )

        field_func.short_description = (
            short_description if short_description else pretty_name(attr)
        )
        field_func.allow_tags = True
        return field_func

    return wrap
