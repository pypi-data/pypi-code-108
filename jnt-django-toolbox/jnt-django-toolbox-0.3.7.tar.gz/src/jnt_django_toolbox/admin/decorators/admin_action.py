from functools import wraps


def admin_action(short_description=None):
    """Wrapper for admin action.

    ``short_description (str)``
    Description of the function.

    Usage::

        from jnt_admin_tools.decorators import admin_action
        from django.contrib import admin
        from test_app.models import Bar

        @admin.register(Bar)
        class BarAdmin(admin.ModelAdmin):
            fields = ("name",)
            actions = ("update_objs",)

            @admin_action("Update objs")
            def update_objs(self, request, queryset):
                pass

    The wrapped method receives the action method.
    """

    def wrap(func):  # noqa: WPS430
        @wraps(func)
        def action_func(self, request, queryset):  # noqa: WPS430
            return func(self, request, queryset)

        action_func.short_description = short_description
        return action_func

    return wrap
