# -*- coding: utf-8 -*-
from copy import deepcopy
from plone import api
from plone.indexer.interfaces import IIndexableObject
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.catalog import (
    LazyCatalogResultSerializer as BaseSerializer,
)
from Products.ZCatalog.Lazy import Lazy
from rer.sitesearch import _
from rer.sitesearch.interfaces import IRERSiteSearchLayer
from rer.sitesearch.restapi.utils import get_indexes_mapping
from rer.sitesearch.restapi.utils import get_types_groups
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implementer


import Missing


@implementer(ISerializeToJson)
@adapter(Lazy, IRERSiteSearchLayer)
class LazyCatalogResultSerializer(BaseSerializer):
    def __call__(self, fullobjects=False):
        data = super(LazyCatalogResultSerializer, self).__call__(
            fullobjects=fullobjects
        )
        # add facets informations
        data.update({"facets": self.extract_facets(brains=self.lazy_resultset)})
        return data

    def extract_facets(self, brains):
        pc = api.portal.get_tool(name="portal_catalog")
        facets = {
            "groups": self.get_groups_facets(brains=brains),
            "indexes": get_indexes_mapping(),
        }
        for brain in brains:
            for index_id, index_settings in facets["indexes"].get("values", {}).items():
                try:
                    value = getattr(brain, index_id)
                except AttributeError:
                    # index is not a brain's metadata. Load item object
                    # (could be painful)
                    item = brain.getObject()
                    adapter = queryMultiAdapter((item, pc), IIndexableObject)
                    value = getattr(adapter, index_id, None)
                if not value or value == Missing.Value:
                    continue
                else:
                    if isinstance(value, list) or isinstance(value, tuple):
                        for single_value in value:
                            if single_value not in index_settings["values"]:
                                index_settings["values"][single_value] = 1
                            else:
                                index_settings["values"][single_value] += 1
                    else:
                        if value not in index_settings["values"]:
                            index_settings["values"][value] = 1
                        else:
                            index_settings["values"][value] += 1
        return facets

    def get_groups_facets(self, brains):
        """
        We need to have the right count for groups facets because these are
        not proper facets, and the number of results should be the same also
        if we select a different group (groups only needs to show grouped
        informations, not to filter).
        If we are filtering by type, this means that we need to do an another
        catalog search for get the proper counters for each group.
        """
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        groups = get_types_groups()
        all_label = translate(
            _("all_types_label", default=u"All content types"),
            context=self.request,
        )
        new_query = deepcopy(query)
        if "portal_type" in new_query:
            del new_query["portal_type"]
        portal_types = set([])
        for group_id, group_data in groups.get("values", {}).items():
            if group_data.get("types", []):
                portal_types.update(group_data["types"])
        if portal_types:
            new_query["portal_type"] = list(portal_types)
        brains_to_iterate = api.content.find(**new_query)
        for brain in brains_to_iterate:
            for group in groups.get("values", {}).values():
                if brain.portal_type in group.get("types", []):
                    group["count"] += 1

        groups["values"][all_label]["count"] = getattr(
            brains_to_iterate, "actual_result_count", len(brains_to_iterate)
        )
        return groups
