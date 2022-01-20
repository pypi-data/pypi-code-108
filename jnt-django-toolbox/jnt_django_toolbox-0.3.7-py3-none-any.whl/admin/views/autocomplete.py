from django.apps import apps
from django.contrib.admin.sites import site
from django.contrib.admin.views.autocomplete import (
    AutocompleteJsonView as BaseAutocompleteJsonView,
)
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404, JsonResponse


class AutocompleteFieldsError(Exception):
    """Autocomplete fields error."""


class AutocompleteJsonView(BaseAutocompleteJsonView):
    def get(self, request, *args, **kwargs):
        """Override from base."""
        (  # noqa: WPS414
            self.term,
            self.model_admin,
            self.source_field,
            to_field_name,
        ) = self.process_request(request)

        if not self.has_perm(request):
            raise PermissionDenied()

        self._check_inherit_model_admin()

        self.object_list = self.get_queryset()
        context = self.get_context_data()

        return JsonResponse(
            {
                "results": [
                    self.model_admin.autocomplete_item_data(instance, request)
                    for instance in context["object_list"]
                ],
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )

    def get_queryset(self):
        """Additional filter for queryset in autocomplete."""
        queryset = super().get_queryset()

        return self.model_admin.autocomplete_queryset(self.request, queryset)

    def process_request(self, request):  # noqa: WPS238
        """Process request."""
        self._apply_pagination(request)
        try:
            app_label = request.GET["app_label"]
            model_name = request.GET["model_name"]
            field_name = request.GET.get("field_name")
        except KeyError as err:
            raise PermissionDenied from err

        if field_name:
            return super().process_request(request)

        try:
            source_model = apps.get_model(app_label, model_name)
        except LookupError as err:
            raise PermissionDenied from err

        try:
            model_admin = self.admin_site._registry[source_model]
        except KeyError as err:
            raise PermissionDenied from err

        if not model_admin.get_search_fields(request):
            raise Http404(
                "{0} must have search_fields for the autocomplete_view.".format(
                    type(model_admin).__qualname__,
                )
            )

        to_field_name = "id"
        source_field = models.ForeignKey(
            source_model,
            on_delete=models.CASCADE,
        )

        return (
            request.GET.get("term", ""),
            model_admin,
            source_field,
            to_field_name,
        )

    def _apply_pagination(self, request) -> None:
        page_size = request.GET.get("page_size")
        if page_size:
            self.paginate_by = int(page_size)

    def _check_inherit_model_admin(self) -> None:
        """Check inherit model_admin."""
        from jnt_django_toolbox.admin.mixins import (
            AutocompleteFieldsAdminMixin,
        )

        if not isinstance(self.model_admin, AutocompleteFieldsAdminMixin):
            raise AutocompleteFieldsError(
                "{0} is necessary to inherit the class from the AutocompleteAdminMixin".format(
                    self.model_admin,
                ),
            )


def autocomplete_view(request):
    return AutocompleteJsonView.as_view(admin_site=site)(request)
