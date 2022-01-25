"""Mixins module."""
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.decorators import method_decorator

from ecommerce_extensions.core.utils import has_console_access


class ConsoleAccessMixin:
    """Makes sure only staff users or users in ecomm_console_client group can access the view."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch method in order to check console access."""
        if not has_console_access(request.user):
            raise Http404

        return super().dispatch(request, *args, **kwargs)
