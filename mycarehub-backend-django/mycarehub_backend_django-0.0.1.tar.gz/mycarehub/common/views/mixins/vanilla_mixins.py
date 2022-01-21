from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views.generic import View
from django.views.generic.edit import ModelFormMixin

User = get_user_model()


class ApprovedMixin(UserPassesTestMixin, PermissionRequiredMixin, View):
    permission_denied_message = "Permission Denied"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_approved


class BaseFormMixin(ModelFormMixin, View):
    def form_valid(self, form):
        user = self.request.user
        instance = form.instance
        instance.updated_by = user.pk
        instance.updated = timezone.now()

        if instance.created_by is None:  # pragma: nobranch
            instance.created_by = user.pk

        if (
            getattr(instance, "organisation", None) is None
            and isinstance(user, User)
            and getattr(user, "organisation", None) is not None
        ):
            instance.organisation = user.organisation  # pragma: nocover
        return super().form_valid(form)
