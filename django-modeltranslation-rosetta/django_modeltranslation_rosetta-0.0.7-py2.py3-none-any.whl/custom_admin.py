# coding: utf-8
from __future__ import unicode_literals

from inspect import isclass

import six
from django import forms
from django.conf import settings
from django.db import models
from django.templatetags.static import static
from django.views.generic.base import View

from .admin_views import AdminTemplateView
from .compat import url


# TODO replace to django-admin-view


class ApiJsonContextMixin(object):
    def get_json_context(self, request, object_id=None, form_url=""):
        add = object_id is None

        json_context = {
            "object_id": object_id,
            "add": add,
            "change": not add,
            "admin": {
                "app_label": self.opts.app_label,
                "model_name": self.opts.model_name,
                "object_name": self.opts.object_name,
            },
        }
        if hasattr(self, "has_readonly_permission"):
            json_context["has_readonly_permission"] = self.has_readonly_permission(
                request, None
            )
        return json_context


class PermissionShortcutAdminMixin(object):
    def get_permission_name(self, perm_type="change", opts=None):
        opts = opts or self.opts
        if isinstance(opts, models.Model):
            opts = opts._meta
        return "{}.{}_{}".format(opts.app_label, perm_type, opts.model_name)

    def has_user_permission(self, request, perm_name, obj=None):
        perm_name = self.get_permission_name(perm_name, obj)
        # print self, perm_name
        return request.user.has_perm(perm_name)

    def has_user_negative_permission(self, request, perm_name, obj=None):
        """
        Права доступа, которые отключают функциональность.
        """
        return not request.user.is_superuser and self.has_user_permission(
            request, perm_name, obj
        )


class AdminClassViewMixin(object):
    view_classes = {}
    template_name = None

    def get_template_name(self, view_name=None, view_class=None):
        return self.template_name

    def get_view_classes(self):
        return self.view_classes

    def _get_original_views(self):
        views = {
            "add": [r"^add/$", getattr(self, "add_view", None)],
            "change": [r"^(.+)/$", getattr(self, "change_view", None)],
            "changelist": [r"^$", getattr(self, "changelist_view", None)],
            "delete": [r"^(.+)/delete/$", getattr(self, "delete_view", None)],
            "history": [r"^(.+)/history/$", getattr(self, "history_view", None)],
        }
        return views

    def get_info(self):
        return (self.model._meta.app_label, self.model._meta.model_name)

    def build_url(self, pattern, view, name=None):
        if name:
            name %= self.get_info()

        return url(pattern, self.admin_site.admin_view(view), name=name)

    def get_extra_urls(self):
        return list()

    def get_urls(self):
        urlpatterns = self.get_extra_urls()
        original_views = self._get_original_views()
        view_classes = list(self.get_view_classes().items())
        view_classes += list(original_views.items())
        for name, view in view_classes:
            pattern = None
            if isinstance(view, (list, tuple)):
                pattern, view = view

            if view is None:
                continue

            if isclass(view) and issubclass(view, View):

                view_kw = {}
                if getattr(view, "template_name", None) is None:
                    view_kw["template_name"] = self.get_template_name(name)

                view = view.as_view(admin=self, view_type=name, **view_kw)

            if pattern is None:
                if name in original_views:
                    pattern = original_views[name][0]
                else:
                    pattern = r"^(.+)/%s/$" % name

            urlpatterns.append(self.build_url(pattern, view, name="%s_%s_" + name))

        return self.get_extra_urls() + urlpatterns

    def _get_urls(self):
        return self.get_urls()

    urls = property(_get_urls)


class CustomAdmin(
    six.with_metaclass(
        forms.MediaDefiningClass,
        AdminClassViewMixin,
        PermissionShortcutAdminMixin,
        ApiJsonContextMixin,
    )
):
    fields = fieldsets = exclude = ()
    date_hierarchy = ordering = None
    list_select_related = save_as = save_on_top = False

    app_label = None
    module_name = None

    verbose_name = ""
    verbose_name_plural = ""

    use_permission = True

    template_name = "admin/custom_view/custom_view.html"

    change_view = add_view = changelist_view = AdminTemplateView

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site

        assert self.app_label, "app_label required"
        assert self.module_name, "module_name required"

    def get_view_on_site_url(self, obj):
        return None

    @classmethod
    def _registration_args(cls):
        class Fake(object):
            pass

        model = Fake()
        model._meta = Fake()
        model._meta.app_label = cls.app_label

        model.__name__ = cls.module_name
        model._meta.module_name = cls.module_name

        model._meta.model_name = cls.module_name
        model._meta.object_name = cls.module_name.capitalize()

        model._meta.verbose_name = cls.verbose_name
        model._meta.verbose_name_plural = cls.verbose_name_plural
        model._meta.abstract = False
        model._meta.swapped = False
        model._deferred = False

        # For 1.10
        copy_map = {"app_label": "label", "verbose_name": "verbose_name"}

        model._meta.app_config = Fake()
        for f, to in copy_map.items():
            setattr(model._meta.app_config, to, getattr(model._meta, f))

        return (model,), cls

    @classmethod
    def register_at(cls, admin_site):
        return admin_site.register(*cls._registration_args())

    @classmethod
    def check(cls, model=None):
        return []

    def has_change_permission(self, request, obj=None):
        if self.use_permission:
            return self.has_user_permission(request, "change")
        return True

    def has_view_permission(self, request, obj=None):
        if self.use_permission:
            for perm_key in ["change", "view"]:
                if self.has_user_permission(request, perm_key):
                    return True
            return False
        return True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return request.user.has_module_perms(self.opts.app_label)

    def get_model_perms(self, request, obj=None):
        """
        Returns a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            "view": self.has_view_permission(request, obj),
            "change": self.has_change_permission(request, obj),
            "add": self.has_add_permission(request),
            "delete": self.has_delete_permission(request, obj),
        }

    def get_title(self, obj):
        return self.verbose_name

    def get_extra_context(self, request, *args, **kwargs):
        return dict(
            self.admin_site.each_context(request),
            app_label=self.app_label,
            verbose_name=self.verbose_name,
            opts=self.model._meta,
            json_context=self.get_json_context(request, *args),
            title=self.get_title(None),
            media=self.media,
        )

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        js = [
            "core.js",
            "jquery%s.js" % extra,
            "jquery.init.js",
            "admin/RelatedObjectLookups.js",
        ]
        if self.actions is not None:
            js.append("actions%s.js" % extra)
        if self.prepopulated_fields:
            js.extend(["urlify.js", "prepopulate%s.js" % extra])
        return forms.Media(js=[static("admin/js/%s" % url) for url in js])
