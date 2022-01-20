# coding: utf-8
from __future__ import unicode_literals

from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, FormView

from .view_mixins import AdminViewMixin


class AdminObjectView(AdminViewMixin):
    def get_queryset(self):
        return self.admin.get_queryset(self.request)

    def get_object(self, queryset=None):
        obj = self.admin.get_object(self.request, self.kwargs[self.pk_url_kwarg])
        if obj is None:
            raise ObjectDoesNotExist("Not found")
        return obj


class AdminTemplateView(AdminViewMixin, TemplateView):
    template_name = None


class AdminFormView(AdminViewMixin, FormView):
    pass


class AdminDetailView(AdminObjectView, DetailView):
    def get_context_data(self, **kwargs):
        context = AdminObjectView.get_context_data(self, **kwargs)
        context.update(DetailView.get_context_data(self, **kwargs))
        return context

    def dispatch(
        self, request, object_id=None, form_url="", extra_context=None, **kwargs
    ):
        self.kwargs = {
            "pk": object_id,
            "form_url": form_url,
            "extra_context": extra_context,
        }
        self.kwargs.update(kwargs)
        return super(AdminDetailView, self).dispatch(request, **self.kwargs)


class AdminUpdateView(AdminObjectView, UpdateView):
    success_url = ""

    def get_admin_context(self, **extra_context):
        context = super(AdminUpdateView, self).get_admin_context(**extra_context)
        context.update(self.admin.get_extra_context(self.request, object_id=None))
        return context

    def get_context_data(self, **kwargs):
        context = UpdateView.get_context_data(self, **kwargs)
        context.update(self.get_admin_context())
        return context

    def form_invalid(self, form):
        return super(AdminUpdateView, self).form_invalid(form)

    def form_valid_response(self, form):
        if self.is_add():
            return self.admin.response_add(self.request, self.object)
        return self.admin.response_change(self.request, self.object)

    def form_valid(self, form):
        self.object = form.save()
        if hasattr(form, "save_m2m"):
            form.save_m2m()
        return self.form_valid_response(form)

    def dispatch(
        self, request, object_id=None, form_url="", extra_context=None, **kwargs
    ):
        self.kwargs = {
            "pk": object_id,
            "form_url": form_url,
            "extra_context": extra_context,
        }
        self.kwargs.update(**kwargs)
        return super(AdminUpdateView, self).dispatch(request, **self.kwargs)


class AdminAddFormView(AdminUpdateView):
    def get_object(self, queryset=None):
        return None


class AdminChangeFormView(AdminUpdateView):
    is_allow_add = True

    def get_admin_context(self, **extra_context):
        context = AdminObjectView.get_admin_context(self, **extra_context)
        context.update(
            self.admin.get_extra_context(
                self.request, object_id=self.object and self.object.id
            )
        )
        return context

    def get_object(self, queryset=None):
        try:
            return super(AdminChangeFormView, self).get_object(queryset)
        except ObjectDoesNotExist:
            if not self.is_allow_add:
                raise Http404("Not found")


def admin_view_class(view_class, view_type="change", template_name=None):
    def decorator(func):
        @wraps(func)
        def wrap(self, request, *args, **kwargs):
            view = getattr(func, "_view", None)
            if not view:
                view_kw = {}
                if template_name:
                    view_kw["template_name"] = template_name
                view = view_class.as_view(admin=self, view_type=view_type, **view_kw)
                setattr(func, "_view", None)
            return view(request, *args, **kwargs)

        return wrap

    return decorator
