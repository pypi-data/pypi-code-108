import six
from django.contrib.admin import FieldListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from jnt_django_toolbox.models.fields.bit.types import Bit


class BitFieldListFilter(FieldListFilter):
    """List filter for bitfields."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        """Initializing."""
        self.lookup_kwarg = field_path
        self.lookup_val = int(request.GET.get(self.lookup_kwarg, 0))
        self.flags = field.flags
        self.labels = field.labels
        super().__init__(
            field,
            request,
            params,
            model,
            model_admin,
            field_path,
        )

    def queryset(self, request, queryset):
        """Provides queryset."""
        filter = {
            param: models.F(param).bitor(value)
            for param, value in six.iteritems(self.used_parameters)
        }
        try:
            return queryset.filter(**filter)
        except ValidationError as e:
            raise IncorrectLookupParameters(e)

    def expected_parameters(self):
        """Get expected parameters."""
        return [self.lookup_kwarg]

    def choices(self, cl):
        """Get choices."""
        yield {
            "selected": self.lookup_val == 0,
            "query_string": cl.get_query_string({}, [self.lookup_kwarg]),
            "display": _("All"),
        }
        for number, _flag in enumerate(self.flags):
            bit_mask = Bit(number).mask
            yield {
                "selected": self.lookup_val == bit_mask,
                "query_string": cl.get_query_string(
                    {self.lookup_kwarg: bit_mask},
                ),
                "display": self.labels[number],
            }
