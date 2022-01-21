from wagtail.api.v2.filters import (
    AncestorOfFilter,
    ChildOfFilter,
    DescendantOfFilter,
    FieldsFilter,
    LocaleFilter,
    OrderingFilter,
    SearchFilter,
    TranslationOfFilter,
)
from wagtail.api.v2.views import PagesAPIViewSet

from .filters import CategoryFilter, TagFilter


class CustomPageAPIViewset(PagesAPIViewSet):
    # the order is important...wagtail filters come last
    filter_backends = [
        TagFilter,
        CategoryFilter,
        FieldsFilter,
        ChildOfFilter,
        AncestorOfFilter,
        DescendantOfFilter,
        OrderingFilter,
        TranslationOfFilter,
        LocaleFilter,
        SearchFilter,  # must be last
    ]
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(["tag", "category"])
