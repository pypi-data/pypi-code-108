from typing import List, Optional

from django.db.models import Q, QuerySet

from simple_graphql.django.types import ModelInstance


def order_qs(
    qs: QuerySet[ModelInstance], ordering: Optional[str]
) -> QuerySet[ModelInstance]:
    if ordering:
        return qs.order_by(ordering)
    return qs


def search_qs(
    qs: QuerySet[ModelInstance],
    search_fields: Optional[List[str]],
    search_query: Optional[str],
) -> QuerySet[ModelInstance]:
    if not search_fields or not search_query:
        return qs

    search_parts = [x for x in search_query.strip().split(" ") if x]
    match_query = Q()

    for part in search_parts:
        part_query = Q()
        for field in search_fields:
            part_query |= Q(**{f"{field}__icontains": part})
        match_query &= part_query

    return qs.exclude(~match_query)
