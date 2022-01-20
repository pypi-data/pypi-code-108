from functools import wraps

from django.forms.utils import pretty_name
from django.utils.html import format_html

from jnt_django_toolbox.admin.helpers import urls
from jnt_django_toolbox.helpers.objects import getattr_nested


def admin_link(attr, short_description=None, empty_description="-"):
    """Render a link to a related model in the admin detail page.

    ``attr (str)``
        Name of the related field.
    ``short_description (str)``
        Name if the field.
        Default value: None.
    ``empty_description (str)``
        Value to display if the related field is None.
        Default value: -.

    The wrapped method receives the related object and should
    return the link text.

    Usage::

        from django.contrib import admin
        from jnt_admin_tools.decorators import admin_link
        from test_app.models import Foo

        @admin.register(Foo)
        class FooAdmin(admin.ModelAdmin):
            fields = ('name', 'bar', 'bar_link')
            readonly_fields = ('bar_link',)

            @admin_link('bar')
            def bar_link(self, obj):
                return obj.name

    .. image:: images/decorators/decorator_admin_link.png
    """

    def wrap(func):  # noqa: WPS430
        @wraps(func)
        def field_func(self, isntance):  # noqa: WPS430
            related_obj = getattr_nested(isntance, attr)
            if related_obj is None:
                return empty_description
            url = urls.admin_change_url(related_obj)
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
