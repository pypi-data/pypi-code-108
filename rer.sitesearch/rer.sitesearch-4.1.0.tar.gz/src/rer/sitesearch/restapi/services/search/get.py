# -*- coding: utf-8 -*-
from copy import deepcopy
from plone import api
from plone.api.exc import InvalidParameterError
from plone.registry.interfaces import IRegistry
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from rer.sitesearch import _
from rer.sitesearch.restapi.utils import get_indexes_mapping
from rer.sitesearch.restapi.utils import get_types_groups
from zope.component import getUtility
from zope.i18n import translate
from plone.memoize.view import memoize

try:
    from rer.solrpush.interfaces.settings import IRerSolrpushSettings
    from rer.solrpush.restapi.services.solr_search.solr_search_handler import (
        SolrSearchHandler,
    )
    from rer.solrpush.utils.solr_indexer import get_site_title

    HAS_SOLR = True
except ImportError:
    HAS_SOLR = False

try:
    # rer.agidtheme overrides site tile field
    from rer.agidtheme.base.interfaces import IRERSiteSchema as ISiteSchema
    from rer.agidtheme.base.utility.interfaces import ICustomFields

    RER_THEME = True
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import ISiteSchema

    RER_THEME = False


import six


class SearchGet(Service):
    @property
    def solr_search_enabled(self):
        if not HAS_SOLR:
            return False
        try:
            return api.portal.get_registry_record(
                "active", interface=IRerSolrpushSettings
            )
        except (KeyError, InvalidParameterError):
            return False

    @property
    @memoize
    def searchable_portal_types(self):
        groups = get_types_groups()
        types = set([])
        for group_id, group_data in groups.get("values", {}).items():
            if group_data.get("types", []):
                types.update(group_data["types"])
        return sorted(list(types))

    def reply(self):
        query = deepcopy(self.request.form)
        query = unflatten_dotted_dict(query)
        path_infos = self.get_path_infos(query=query)

        groups = get_types_groups()
        if "group" in query:
            for group_id, group_data in groups.get("values", {}).items():
                if query["group"] == group_id and group_data["types"]:
                    query["portal_type"] = group_data["types"]

            del query["group"]
        if self.solr_search_enabled:
            data = self.do_solr_search(query=query)
        else:
            data = SearchHandler(self.context, self.request).search(query)
        if path_infos:
            data["path_infos"] = path_infos
        return data

    def do_solr_search(self, query):
        query["facets"] = True
        query["facet_fields"] = ["portal_type", "site_name"]

        if not query.get("site_name", []):
            query["site_name"] = get_site_title()
        elif "all" in query.get("site_name", []):
            del query["site_name"]

        indexes = get_indexes_mapping()

        if indexes:
            query["facet_fields"].extend(indexes["order"])
        if "metadata_fields" not in query:
            query["metadata_fields"] = ["Description"]
        else:
            if "Description" not in query["metadata_fields"]:
                query["metadata_fields"].append("Description")
        data = SolrSearchHandler(self.context, self.request).search(query)
        data["facets"] = self.remap_solr_facets(data=data, query=query)
        data["current_site"] = get_site_title()
        return data

    def remap_solr_facets(self, data, query):
        new_facets = {
            "groups": get_types_groups(),
            "indexes": get_indexes_mapping(),
            "sites": {"order": [], "values": {}},
        }
        for index_id, index_values in data["facets"].items():
            if index_id == "site_name":
                entry = new_facets["sites"]["values"]
                self.handle_sites_facet(
                    sites=entry,
                    index_values=index_values,
                    query=query,
                )
                new_facets["sites"]["order"] = sorted(entry.keys())
            elif index_id == "portal_type":
                # groups
                self.handle_groups_facet(
                    groups=new_facets["groups"]["values"],
                    index_values=index_values,
                    query=query,
                )
            else:
                entry = new_facets["indexes"]["values"][index_id]
                for index_mapping in index_values:
                    for key, count in index_mapping.items():
                        if count:
                            entry["values"][key] = count
        return new_facets

    def handle_groups_facet(self, groups, index_values, query):
        # we need to do a second query in solr, to get the results
        # unfiltered by types
        portal_types = query.get("portal_type", "")
        if portal_types:
            new_query = deepcopy(query)
            del new_query["portal_type"]
            # simplify returned result data
            new_query["facet_fields"] = ["portal_type"]
            new_query["metadata_fields"] = ["UID"]
            new_data = SolrSearchHandler(self.context, self.request).search(new_query)
            indexes = new_data["facets"]["portal_type"]
        else:
            indexes = index_values
        all_label = translate(
            _("all_types_label", default=u"All content types"),
            context=self.request,
        )
        for type_mapping in indexes:
            for ptype, count in type_mapping.items():
                for group in groups.values():
                    if ptype in group["types"]:
                        group["count"] += count
                groups[all_label]["count"] += count

    def handle_sites_facet(self, sites, index_values, query):
        site = query.get("site_name", "")
        if site:
            # we need to do an additional query in solr, to get the results
            # unfiltered by site_name
            new_query = deepcopy(query)
            del new_query["site_name"]
            # simplify returned result data
            new_query["facet_fields"] = ["site_name"]
            new_query["metadata_fields"] = ["UID"]
            new_data = SolrSearchHandler(self.context, self.request).search(new_query)
            indexes = new_data["facets"]["site_name"]
        else:
            indexes = index_values
        for site_mapping in indexes:
            for name, count in site_mapping.items():
                if count:
                    sites[name] = count

    def get_path_infos(self, query):
        if "path" not in query:
            return {}
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        site_title = getattr(site_settings, "site_title") or ""
        if RER_THEME:
            fields_value = getUtility(ICustomFields)
            site_title = fields_value.titleLang(site_title)
        if six.PY2:
            site_title = site_title.decode("utf-8")

        path = query["path"]
        if isinstance(path, dict):
            path = path.get("query", "")
        root_path = "/".join(api.portal.get().getPhysicalPath())

        data = {
            "site_name": site_title,
            "root": "/".join(api.portal.get().getPhysicalPath()),
        }
        if path != root_path:
            folder = api.content.get(path)
            if folder:
                data["path_title"] = folder.title
        return data


class SearchLocalGet(SearchGet):
    @property
    def solr_search_enabled(self):
        return False
