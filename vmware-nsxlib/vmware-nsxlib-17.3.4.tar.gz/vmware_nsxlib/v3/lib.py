# Copyright 2016 OpenStack Foundation
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
from distutils import version

from oslo_log import log

from vmware_nsxlib._i18n import _
from vmware_nsxlib.v3 import client
from vmware_nsxlib.v3 import cluster
from vmware_nsxlib.v3 import exceptions
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3 import utils

LOG = log.getLogger(__name__)


class NsxLibBase(object, metaclass=abc.ABCMeta):
    def __init__(self, nsxlib_config):

        self.nsx_version = None
        self.nsx_api = None
        self.default_headers = None
        self.set_config(nsxlib_config)
        self.set_default_headers(nsxlib_config)

        # create the Cluster
        self.cluster = cluster.NSXClusteredAPI(self.nsxlib_config)

        # create the Client
        self.client = client.NSX3Client(
            self.cluster,
            nsx_api_managers=self.nsxlib_config.nsx_api_managers,
            max_attempts=self.nsxlib_config.max_attempts,
            url_path_base=self.client_url_prefix,
            rate_limit_retry=self.nsxlib_config.rate_limit_retry,
            default_headers=self.default_headers)

        self.general_apis = utils.NsxLibApiBase(
            self.client, self.nsxlib_config)

        self.init_api()

        super(NsxLibBase, self).__init__()

    def set_config(self, nsxlib_config):
        """Set config user provided and extend it according to application"""
        self.nsxlib_config = nsxlib_config
        self.nsxlib_config.extend(None, url_base=self.client_url_prefix)

    def set_default_headers(self, nsxlib_config):
        """Set the default headers with token information"""
        if nsxlib_config.token_provider:
            try:
                token_value = nsxlib_config.token_provider.get_token()
            except exceptions.BadJSONWebTokenProviderRequest as e:
                LOG.error("Error in retrieving JSON Web Token: %s", e)
                return
            bearer_token = "Bearer %s" % token_value
            self.default_headers = self.default_headers or {}
            self.default_headers["Authorization"] = bearer_token

    @abc.abstractproperty
    def client_url_prefix(self):
        pass

    @abc.abstractmethod
    def init_api(self):
        pass

    @abc.abstractmethod
    def feature_supported(self, feature):
        pass

    @abc.abstractmethod
    def get_version(self):
        pass

    def build_v3_api_version_tag(self):
        return self.general_apis.build_v3_api_version_tag()

    def is_internal_resource(self, nsx_resource):
        return self.general_apis.is_internal_resource(nsx_resource)

    def build_v3_api_version_project_tag(self, project_name, project_id=None):
        return self.general_apis.build_v3_api_version_project_tag(
            project_name, project_id=project_id)

    def build_v3_tags_payload(self, resource, resource_type, project_name):
        return self.general_apis.build_v3_tags_payload(
            resource, resource_type, project_name)

    def reinitialize_cluster(self, resource, event, trigger, payload=None):
        self.cluster._reinit_cluster()

    def subscribe(self, callback, event):
        self.cluster.subscribe(callback, event)

    def _add_pagination_parameters(self, url, cursor, page_size):
        if cursor:
            url += "&cursor=%d" % cursor
        if page_size:
            url += "&page_size=%d" % page_size
        return url

    def _get_search_url(self):
        if (version.LooseVersion(self.get_version()) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_3_0_0)):
            return "search/query?query=%s&sort_by=id"
        return "search?query=%s&sort_by=id"

    # TODO(abhiraut): Revisit this method to generate complex boolean
    #                 queries to search resources.
    def search_by_tags(self, tags, resource_type=None, cursor=None,
                       page_size=None, silent=False, **extra_attrs):
        """Return the list of resources searched based on tags.

        Currently the query only supports AND boolean operator.
        :param tags: List of dictionaries containing tags. Each
                     NSX tag dictionary is of the form:
                     {'scope': <scope_key>, 'tag': <tag_value>}
        :param resource_type: Optional string parameter to limit the
                              scope of the search to the given ResourceType.
        :param cursor: Opaque cursor to be used for getting next page of
                       records (supplied by current result page).
        :param page_size: Maximum number of results to return in this page.
        :param silent: Silence the logging if True.
        :param extra_attrs: Support querying by user specified attributes.
                            Multiple attributes will be ANDed.
        """
        if not tags:
            reason = _("Missing required argument 'tags'")
            raise exceptions.NsxSearchInvalidQuery(reason=reason)
        # Query will return nothing if the same scope is repeated.
        query_tags = self._build_query(tags)
        query = 'resource_type:%s' % resource_type if resource_type else None
        if query:
            query += " AND %s" % query_tags
        else:
            query = query_tags
        if extra_attrs:
            query += " AND %s" % " AND ".join(
                ['%s:%s' % (k, v) for (k, v) in extra_attrs.items()])
        url = self._add_pagination_parameters(self._get_search_url() % query,
                                              cursor, page_size)

        # Retry the search in case of error
        @utils.retry_upon_exception(exceptions.NsxSearchError,
                                    max_attempts=self.client.max_attempts)
        def do_search(url):
            return self.client.url_get(url, silent=silent)

        return do_search(url)

    def search_resource_by_attributes(self, resource_type, cursor=None,
                                      page_size=None, **attributes):
        """Search resources of a given type matching specific attributes.

        It is optional to specify attributes. If multiple attributes are
        specified they are ANDed together to form the search query.

        :param resource_type: String parameter specifying the desired
                              resource_type
        :param cursor: Opaque cursor to be used for getting next page of
                       records (supplied by current result page).
        :param page_size: Maximum number of results to return in this page.
        :param **attributes: an optional set of keyword arguments
                             specifying filters for the search query.
                             Wildcards will not be interpeted.

        :returns: a list of resources of the requested type matching
                  specified filters.
        """
        if not resource_type:
            raise exceptions.NsxSearchInvalidQuery(
                reason=_("Resource type was not specified"))
        attributes_query = " AND ".join(['%s:%s' % (k, v) for (k, v)
                                         in attributes.items()])
        query = 'resource_type:%s' % resource_type + (
            " AND %s" % attributes_query if attributes_query else "")
        url = self._add_pagination_parameters(self._get_search_url() % query,
                                              cursor, page_size)

        # Retry the search in case of error
        @utils.retry_upon_exception(exceptions.NsxSearchError,
                                    max_attempts=self.client.max_attempts)
        def do_search(url):
            return self.client.url_get(url)

        return do_search(url)

    def search_resource_by_attribute_values(self, resource_type, name, values,
                                            cursor=None, page_size=None):
        """Search resources of a given type matching values of an attribute.

        :param resource_type: String parameter specifying the desired
                              resource_type.
        :param name: Attribute name to match.
        :param values: List of attribute values to search for.
        :param cursor: Opaque cursor to be used for getting next page of
                       records (supplied by current result page).
        :param page_size: Maximum number of results to return in this page.

        :returns: a list of resources of the requested type matching
                  specified attribute values.
        """
        attribute_query = " OR ".join(values)
        query = 'resource_type:%s' % resource_type + (
            " AND %s:(%s)" % (name, attribute_query)
            if attribute_query else "")
        body = {"query_pipeline": [{"query": query}]}
        url = self._add_pagination_parameters(
            "search/querypipeline?sort_by=id", cursor, page_size)

        # Retry the search in case of error
        @utils.retry_upon_exception(exceptions.NsxSearchError,
                                    max_attempts=self.client.max_attempts)
        def do_search(url):
            return self.client.url_post(url, body)

        return do_search(url)

    def search_resource_by_filters(self, resource_type, filters,
                                   cursor=None, page_size=None, **extra_attrs):
        """Search resources of a given type matching specific filters.

        :param resource_type: String parameter specifying the desired
                              resource_type.
        :param filters: List of dictionaries containing filters. Each
                     filter dictionary is of the form:
                     {'field_names': <filter_key>, 'value': <filter_value>}
        :param cursor: Opaque cursor to be used for getting next page of
                       records (supplied by current result page).
        :param page_size: Maximum number of results to return in this page.
        :param extra_attrs: Support querying by user specified attributes.

        :returns: a list of resources of the requested type matching
                  specified filters.
        """
        body = {"primary": {"resource_type": resource_type,
                            "filters": filters}}
        related = extra_attrs.get("related")
        if related:
            body["related"] = related
        url = self._add_pagination_parameters(
            "search/aggregate?sort_by=id", cursor, page_size)

        # Retry the search in case of error
        @utils.retry_upon_exception(exceptions.NsxSearchError,
                                    max_attempts=self.client.max_attempts)
        def do_search(url):
            return self.client.url_post(url, body)

        return do_search(url)

    def _search_all(self, search_func, *args, **kwargs):
        results = []
        cursor = 0
        page_size = None
        while True:
            try:
                response = search_func(*args, cursor=cursor,
                                       page_size=page_size, **kwargs)
            except exceptions.NsxSearchPipelineError:
                if page_size is None:
                    page_size = 1000
                page_size -= 100
                if page_size < 0:
                    # Set page_size to the minimum value 1
                    page_size = 1
                continue
            if not response['results']:
                return results
            results.extend(response['results'])
            cursor = int(response['cursor'])
            result_count = int(response['result_count'])
            if cursor >= result_count:
                return results

    def search_all_by_tags(self, tags, resource_type=None, **extra_attrs):
        """Return all the results searched based on tags."""
        return self._search_all(self.search_by_tags,
                                resource_type=resource_type, tags=tags,
                                **extra_attrs)

    def search_all_resource_by_attributes(self, resource_type, **attributes):
        """Return all resources of a given type matching specific attributes.

        """
        return self._search_all(self.search_resource_by_attributes,
                                resource_type=resource_type, **attributes)

    def search_all_resource_by_attribute_values(self, resource_type, name,
                                                values):
        """Return all resources of a given type matching an attribute value.

        """
        return self._search_all(self.search_resource_by_attribute_values,
                                resource_type, name, values)

    def search_all_resource_by_filters(self, resource_type, filters,
                                       **extra_attrs):
        """Return all resources of a given type matching specific filters."""
        return self._search_all(self.search_resource_by_filters, resource_type,
                                filters, **extra_attrs)

    def get_id_by_resource_and_tag(self, resource_type, scope, tag,
                                   alert_not_found=False,
                                   alert_multiple=False):
        """Search a resource type by 1 scope&tag.

        Return the id of the result only if it is single.
        """
        query_tags = [{'scope': utils.escape_tag_data(scope),
                       'tag': utils.escape_tag_data(tag)}]
        query_result = self.search_by_tags(
            tags=query_tags, resource_type=resource_type)
        if not query_result['result_count']:
            if alert_not_found:
                msg = _("No %(type)s found for tag '%(scope)s:%(tag)s'") % {
                    'type': resource_type,
                    'scope': scope,
                    'tag': tag}
                LOG.warning(msg)
                raise exceptions.ResourceNotFound(
                    manager=self.nsxlib_config.nsx_api_managers,
                    operation=msg)
        elif query_result['result_count'] == 1:
            return query_result['results'][0]['id']
        else:
            # multiple results
            if alert_multiple:
                msg = _("Multiple %(type)s found for tag '%(scope)s:"
                        "%(tag)s'") % {
                    'type': resource_type,
                    'scope': scope,
                    'tag': tag}
                LOG.warning(msg)
                raise exceptions.ManagerError(
                    manager=self.nsxlib_config.nsx_api_managers,
                    operation=msg,
                    details='')

    def _build_tag_query(self, tag):
        # Validate that the correct keys are used
        if set(tag.keys()) - set(('scope', 'tag')):
            reason = _("Only 'scope' and 'tag' keys are supported")
            raise exceptions.NsxSearchInvalidQuery(reason=reason)
        _scope = tag.get('scope')
        _tag = tag.get('tag')
        if _scope and _tag:
            return 'tags.scope:%s AND tags.tag:%s' % (_scope, _tag)
        elif _scope:
            return 'tags.scope:%s' % _scope
        else:
            return 'tags.tag:%s' % _tag

    def _build_query(self, tags):
        return " AND ".join([self._build_tag_query(item) for item in tags])

    def get_tag_limits(self):
        try:
            result = self.client.url_get('spec/vmware/types/Tag')
            scope_length = result['properties']['scope'].get(
                'maxLength', utils.MAX_RESOURCE_TYPE_LEN)
            tag_length = result['properties']['tag'].get(
                'maxLength', utils.MAX_TAG_LEN)
        except Exception as e:
            LOG.error("Unable to read tag limits. Reason: %s", e)
            scope_length = utils.MAX_RESOURCE_TYPE_LEN
            tag_length = utils.MAX_TAG_LEN
        try:
            result = self.client.url_get('spec/vmware/types/ManagedResource')
            max_tags = result['properties']['tags']['maxItems']
        except Exception as e:
            LOG.error("Unable to read maximum tags. Reason: %s", e)
            max_tags = utils.MAX_TAGS
        return utils.TagLimits(scope_length, tag_length, max_tags)
