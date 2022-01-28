from django.contrib.auth import get_user_model
from django.db.models import TextField
from django.db.models.functions import Cast
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType

from elasticsearch_dsl import Q

from pyston.contrib.elasticsearch.filters import ElasticsearchFilter
from pyston.filters.filters import OPERATORS
from pyston.filters.exceptions import FilterValueError

from is_core.contrib.elasticsearch.filters import CoreElasticsearchFilterManagerFilterManager

from security.backends.elasticsearch.models import get_key_from_content_type_and_id


class UsernameUserFilter(ElasticsearchFilter):

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
        return Q('terms', **{'user_id': value})


class EnumElasticsearchFilter(ElasticsearchFilter):

    allowed_operators = (OPERATORS.EQ,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum = self.field._enum
        self.choices = [(None, '')] + [
            (choice.name, choice.label) for choice in self._enum
        ]

    def clean_value(self, value, operator_slug, request):
        try:
            return self._enum[value]
        except KeyError:
            raise FilterValueError(
                ugettext('Invalid value. Please use one of the following values: {}.').format(
                    ', '.join([a.name for a in self._enum])
                )
            )

    def get_filter_term(self, value, operator_slug, request):
        return Q('term', **{self.get_full_filter_key(): value.name})


class SecurityElasticsearchFilterManager(CoreElasticsearchFilterManagerFilterManager):

    filter_by_field_name = {
        'enum': EnumElasticsearchFilter,
        **CoreElasticsearchFilterManagerFilterManager.filter_by_field_name,
    }


class RelatedObjectsFilter(ElasticsearchFilter):

    allowed_operators = (OPERATORS.IN,)

    def clean_value(self, value, operator_slug, request):
        cleaned_values = []
        for v in value:
            try:
                content_type_id, object_id = v.split('|')
                cleaned_values.append(
                    get_key_from_content_type_and_id(ContentType.objects.get(pk=content_type_id), object_id)
                )
            except (ValueError, ContentType.DoesNotExist):
                raise FilterValueError(ugettext('Invalid value.'))
        return cleaned_values

    def get_filter_term(self, value, operator_slug, request):
        return Q('terms', related_objects=value)
