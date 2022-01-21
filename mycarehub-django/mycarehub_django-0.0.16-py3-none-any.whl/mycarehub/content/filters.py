from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from mycarehub.content.models import ContentItem


class TagFilter(BaseFilterBackend):
    """
    Implements the ?tag filter which returns only pages that match a tag.

    This filter accepts a single tag.
    """

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        tag = query_params.get("tag", "")

        if tag and queryset.model is ContentItem:
            queryset = queryset.filter(Q(tags__name=tag) | Q(tags__slug=tag))

        return queryset


class CategoryFilter(BaseFilterBackend):
    """
    Implements the ?category filter which returns only pages that match a
    category ID.

    This filter accepts a single category ID.
    When no filter is passed, the category ID 1
    which is reserved for `welcome` content type is excluded.
    """

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        category_id = query_params.get("category", "")

        if category_id and queryset.model is ContentItem:
            queryset = queryset.filter(Q(categories__id=category_id))
        if not category_id and queryset.model is ContentItem:
            queryset = queryset.filter(~Q(categories__id=1))

        return queryset
