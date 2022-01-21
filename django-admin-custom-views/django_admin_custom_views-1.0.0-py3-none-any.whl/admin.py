from functools import update_wrapper
from typing import List

from django.contrib import admin
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.urls import path

admin.site.unregister(Site)


def custom_view(function=None, *, permissions=None, description=None, switch_field=None):
    def decorator(func):
        if permissions is not None:
            func.allowed_permissions = permissions
        if description is not None:
            func.short_description = description
            if isinstance(description, dict):
                assert switch_field, 'switch_field argument is required'
                func.switch_field = switch_field
        return func

    if function is None:
        return decorator
    else:
        return decorator(function)


class ViewsModelAdmin(admin.ModelAdmin):
    change_views: List = ()
    list_views: List = ()

    def get_urls(self):
        urls = super(ViewsModelAdmin, self).get_urls()
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        for view, name, _ in self.get_extra_views(self.change_views):
            urls.append(
                path(f'<path:pk>/{name}', self.custom_admin_view(view), name=f'{app_label}_{model_name}_{name}')
            )
        for view, name, _ in self.get_extra_views(self.list_views):
            urls.insert(
                0,
                path(f'{name}/', self.custom_admin_view(view), name=f'{app_label}_{model_name}_{name}')
            )
        return urls

    def changelist_view(self, request, **kwargs):
        extra_context = {'extra_views': self.get_extra_views(self.list_views, request)}
        return super(ViewsModelAdmin, self).changelist_view(request, extra_context=extra_context, **kwargs)

    def change_view(self, request, object_id=None, **kwargs):
        extra_context = {'extra_views': self.get_extra_views(self.change_views, request)}
        return super(ViewsModelAdmin, self).changeform_view(request, object_id, extra_context=extra_context,
                                                            **kwargs)

    def get_extra_views(self, views, request=None):
        for view_name in views:
            view = self.get_view(view_name)
            if request and not self.has_permissions(request, view[0]):
                continue
            yield view

    def get_view(self, view):
        if callable(view):
            view_name = view.__name__
            func = view
        else:
            func = getattr(self, view)
            view_name = view

        description = getattr(func, 'short_description', view_name.replace('_', ' ').title())
        if isinstance(description, dict):
            description['switch_field'] = func.switch_field
        return func, view_name, description

    def get_context(self, request, title):
        opts = self.model._meta
        return {
            **self.admin_site.each_context(request),
            'title': title,
            'module_name': str(opts.verbose_name_plural),
            'opts': opts,
            'preserved_filters': self.get_preserved_filters(request),
        }

    def has_permissions(self, request, view):
        check = []
        allowed_permissions = getattr(view, 'allowed_permissions', [])
        for allowed_permission in allowed_permissions:
            has_permission = getattr(self, f'has_{allowed_permission}_permission')
            check.append(has_permission(request))
        return all(check)

    def custom_admin_view(self, custom_view):
        admin_view = self.admin_site.admin_view(custom_view)

        def wrap(view, cacheable=False):
            def wrapper(request, *args, **kwargs):
                if not self.has_permissions(request, view):
                    raise PermissionDenied
                return self.admin_site.admin_view(view, cacheable)(request, *args, **kwargs)

            return update_wrapper(wrapper, view)

        return wrap(admin_view)

    @staticmethod
    def has_superuser_permission(request):
        return request.user.is_superuser
