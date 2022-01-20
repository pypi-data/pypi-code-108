# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from rer.sitesearch.restapi.utils import get_types_groups
from rer.sitesearch.restapi.utils import get_indexes_mapping


@implementer(IPublishTraverse)
class SearchFiltersGet(Service):
    def reply(self):
        params = {
            "groups": get_types_groups(),
            "indexes": get_indexes_mapping(),
        }

        return {"facets": params}
