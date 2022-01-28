import functools
import operator

from django.contrib.auth import get_user_model
from django.db.models import TextField, Q
from django.db.models.functions import Cast
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType

from pyston.filters.django_filters import SimpleMethodFilter
from pyston.filters.filters import OPERATORS
from pyston.filters.exceptions import FilterValueError


class UsernameUserFilter(SimpleMethodFilter):

    allowed_operators = (OPERATORS.CONTAINS,)

    def clean_value(self, value, operator_slug, request):
        user_model = get_user_model()
        return list(
            user_model.objects.filter(
                **{'{}__contains'.format(user_model.USERNAME_FIELD): value}
            ).annotate(
                str_id=Cast('id', output_field=TextField())
            ).values_list('str_id', flat=True)
        )

    def get_filter_term(self, value, operator_slug, request):
        return {'user_id__in': value}


class RelatedObjectsFilter(SimpleMethodFilter):

    allowed_operators = (OPERATORS.IN,)

    def clean_value(self, value, operator_slug, request):
        cleaned_values = []
        for v in value:
            try:
                content_type_id, object_id = v.split('|')
                cleaned_values.append((int(content_type_id), object_id))
            except (ValueError, ContentType.DoesNotExist):
                raise FilterValueError(ugettext('Invalid value.'))
        return cleaned_values

    def get_filter_term(self, value, operator_slug, request):
        return functools.reduce(operator.or_, (
            Q(
                related_objects__object_id=object_id,
                related_objects__object_ct_id=object_ct_id
            ) for object_ct_id, object_id in value
        ))
