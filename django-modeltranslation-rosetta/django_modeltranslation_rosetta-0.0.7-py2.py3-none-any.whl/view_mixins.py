# coding: utf-8
from __future__ import unicode_literals

from django.contrib.admin.options import IS_POPUP_VAR, get_content_type_for_model


class AdminViewMixin(object):
    admin = None
    view_type = None
    object = None
    form_url = None
    pk_url_kwarg = "pk"

    add_perm = None
    change_perm = None
    delete_perm = None
    readonly_perm = None

    show_delete = show_save = show_save_and_continue = True
    show_only_save = False

    def _get_admin_attr(self, name):
        app_label = getattr(self.admin, name, None)
        if not app_label:
            app_label = getattr(self.admin.model._meta, name)
        return app_label

    def is_add(self):
        return not self.kwargs.get(self.pk_url_kwarg)

    def has_add_permission(self, request):
        perm = self.add_perm
        if perm is None:
            perm = self.admin.has_add_permission(request)
        return perm

    def has_change_permission(self, request, obj):
        perm = self.change_perm
        if perm is None:
            perm = self.admin.has_change_permission(request, obj)
        return perm

    def has_readonly_permission(self, request, obj=None):
        perm = self.readonly_perm
        if perm is None and hasattr(self.admin, "has_readonly_permission"):
            perm = self.admin.has_readonly_permission(request, obj)
        return perm

    def has_delete_permission(self, request, obj):
        perm = self.delete_perm
        if perm is None:
            perm = (self.admin.has_delete_permission(request, obj),)
        return perm

    def get_admin_context(self, **extra_context):
        admin = self.admin
        obj = self.object

        self.request.current_app = admin.admin_site.name

        view_on_site_url = admin.get_view_on_site_url(obj)
        context = dict(
            admin.admin_site.each_context(self.request),
            change=not self.is_add(),
            add=self.is_add(),
            object=obj,
            object_id=obj and obj.id,
            opts=admin.model._meta,
            app_label=self._get_admin_attr("app_label"),
            verbose_name=self._get_admin_attr("verbose_name"),
            save_as=False,
            save_on_top=False,
            is_popup=(
                IS_POPUP_VAR in self.request.POST or IS_POPUP_VAR in self.request.GET
            ),
            is_popup_var=IS_POPUP_VAR,
            content_type_id=get_content_type_for_model(admin.model).pk,
            has_absolute_url=view_on_site_url is not None,
            absolute_url=view_on_site_url,
            form_url=self.kwargs.get("form_url") or "",
            has_add_permission=self.has_add_permission(self.request),
            has_change_permission=self.has_change_permission(self.request, self.object),
            has_delete_permission=self.has_delete_permission(self.request, self.object),
            has_readonly_permission=self.has_readonly_permission(
                self.request, self.object
            ),
            has_file_field=True,
            show_delete=self.show_delete,
            show_save=self.show_save,
            show_save_and_continue=self.show_save_and_continue,
            show_only_save=self.show_save,
        )
        return context

    def get_context_data(self, **kwargs):
        context = super(AdminViewMixin, self).get_context_data(**kwargs)
        context.update(self.get_admin_context())
        if hasattr(self.admin, "get_extra_context"):
            context.update(
                self.admin.get_extra_context(
                    self.request, object_id=context.get("object_id")
                )
            )
        return context
