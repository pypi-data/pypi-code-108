#!/usr/bin/env python3
import datetime
from typing import Any, Iterator, Union, List, Dict
from urllib.parse import quote_plus

from hiro_graph_client.clientlib import AuthenticatedAPIHandler, AbstractTokenApiHandler


class HiroGraph(AuthenticatedAPIHandler):
    """
    Python implementation for accessing the HIRO HIRO REST API.
    See https://core.arago.co/help/specs/?url=definitions/graph.yaml
    """

    def __init__(self, api_handler: AbstractTokenApiHandler):
        """
        Constructor

        :param api_handler: External API handler.
        """
        super().__init__(api_name='graph',
                         api_handler=api_handler)

    ###############################################################################################################
    # REST API operations
    ###############################################################################################################

    def query(self,
              query: str,
              fields: str = None,
              limit=-1,
              offset=0,
              order: str = None,
              meta: bool = None,
              count: bool = None) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Search/post_query_vertices

        :param query: The actual query. e.g. ogit\\\\/_type: ogit\\\\/Question for vertices.
        :param fields: the comma separated list of fields to return
        :param limit: limit of entries to return
        :param offset: offset where to start returning entries
        :param order: order by a field asc|desc, e.g. ogit/name desc
        :param meta: List detailed metainformations in result payload
        :param count: Just return the number of found items. Result payload is like
               {"items":[&lt;number of items found as int&gt;]}.
        :return: Result payload
        """
        url = self.endpoint + '/query/vertices'

        data = {"query": str(query)}
        if fields:
            data['fields'] = quote_plus(fields.replace(" ", ""), safe="/,")
        if limit is not None:
            data['limit'] = limit
        if offset:
            data['offset'] = offset
        if order:
            data['order'] = order
        if meta is not None:
            data['listMeta'] = meta
        if count is not None:
            data['count'] = count
        return self.post(url, data)

    def query_gremlin(self,
                      query: str,
                      root: str,
                      fields: str = None,
                      include_deleted: bool = None,
                      meta: bool = None) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Search/post_query_gremlin

        :param query: The actual query. e.g. outE().inV() for gremlin.
        :param root: ogit/_id of the root node where the gremlin query starts.
        :param fields: the comma separated list of fields to return
        :param include_deleted: Include deleted values.
        :param meta: List detailed metainformations in result payload
        :return: Result payload
        """
        url = self.endpoint + '/query/gremlin'

        data = {"query": str(query),
                "root": root}
        if fields:
            data['fields'] = quote_plus(fields.replace(" ", ""), safe="/,")
        if include_deleted is not None:
            data['include_deleted'] = include_deleted
        if meta is not None:
            data['listMeta'] = meta
        return self.post(url, data)

    def create_node(self, data: dict, obj_type: str, return_id=False) -> Union[dict, str]:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Graph]_Entity/post_new__type_

        :param data: Payload for the new node/vertex
        :param obj_type: ogit/_type of the new node/vertex
        :param return_id: Return only the ogit/_id as string. Default is False to return everything as dict.
        :return: The result payload
        """
        url = self.endpoint + '/new/' + quote_plus(obj_type)
        res = self.post(url, data)
        return res['ogit/_id'] if return_id and 'error' not in res else res

    def update_node(self, node_id: str, data: dict) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Graph]_Entity/post__id_

        :param data: Payload for the node/vertex
        :param node_id: ogit/_id of the node/vertex
        :return: The result payload
        """
        url = self.endpoint + '/' + quote_plus(node_id)
        return self.post(url, data)

    def delete_node(self, node_id: str) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Graph]_Entity/delete__id_

        :param node_id: ogit/_id of the node/vertex
        :return: The result payload
        """
        url = self.endpoint + '/' + quote_plus(node_id)
        return self.delete(url)

    def connect_nodes(self, from_node_id: str, verb: str, to_node_id: str) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Graph]_Verb/post_connect__type_

        :param from_node_id: ogit/_id of the source node/vertex
        :param verb: verb for the connection
        :param to_node_id: ogit/_id of the target node/vertex
        :return: The result payload
        """
        url = self.endpoint + '/connect/' + quote_plus(verb)
        data = {"out": from_node_id, "in": to_node_id}
        return self.post(url, data)

    def disconnect_nodes(self, from_node_id: str, verb: str, to_node_id: str) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Graph]_Verb/delete__id_

        :param from_node_id: ogit/_id of the source node/vertex
        :param verb: verb for the connection
        :param to_node_id: ogit/_id of the target node/vertex
        :return: The result payload
        """
        url = self.endpoint + '/' + quote_plus(
            from_node_id
        ) + "$$" + quote_plus(
            verb
        ) + "$$" + quote_plus(
            to_node_id
        )
        return self.delete(url)

    def get_node(self,
                 node_id: str,
                 fields: str = None,
                 meta: bool = None,
                 include_deleted: bool = None,
                 vid: str = None) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Graph]_Entity/get__id_

        :param node_id: ogit/_id of the node/vertex or edge
        :param fields: Filter for fields
        :param include_deleted: allow to get if ogit/_is-deleted=true
        :param vid: get specific version of Entity matching ogit/_v-id
        :param meta: List detailed metainformations in result payload
        :return: The result payload
        """
        query = {
            "fields": fields.replace(" ", "") if fields else None,
            "listMeta": meta,
            "includeDeleted": include_deleted,
            "vid": vid
        }

        url = self.endpoint + '/' + quote_plus(node_id) + self._get_query_part(query)
        return self.get(url)

    def get_nodes(self,
                  node_ids: list,
                  fields: str = None,
                  meta: bool = None,
                  include_deleted: bool = None,
                  ) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Search/get_query_ids

        :param node_ids: list of ogit/_ids of the node/vertexes or edges
        :param fields: Filter for fields
        :param meta: List detailed metainformations in result payload
        :param include_deleted: allow to get if ogit/_is-deleted=true
        :return: The result payload
        """
        query = {
            "query": ",".join(node_ids),
            "fields": fields.replace(" ", "") if fields else None,
            "includeDeleted": include_deleted,
            "listMeta": meta
        }

        url = self.endpoint + '/query/ids' + self._get_query_part(query)
        return self.get(url)

    def get_node_by_xid(self,
                        node_id: str,
                        fields: str = None,
                        meta: bool = None,
                        include_deleted: bool = None) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Search/get_xid__id_

        :param node_id: ogit/_xid of the node/vertex or edge
        :param fields: Filter for fields
        :param meta: List detailed metainformations in result payload
        :param include_deleted: allow to get if ogit/_is-deleted=true
        :return: The result payload
        """
        query = {
            "fields": fields.replace(" ", "") if fields else None,
            "includeDeleted": include_deleted,
            "listMeta": meta
        }

        url = self.endpoint + '/xid/' + quote_plus(node_id) + self._get_query_part(query)
        return self.get(url)

    def get_timeseries(self,
                       node_id: str,
                       starttime: str = None,
                       endtime: str = None,
                       include_deleted: bool = None,
                       limit: int = None,
                       with_ids: str = None,
                       order: str = "asc",
                       aggregate: str = None) -> Union[List, Dict]:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Timeseries/get__id__values

        :param node_id: ogit/_id of the node containing timeseries
        :param starttime: ms since epoch.
        :param endtime: ms since epoch.
        :param aggregate: aggregate numeric values for multiple timeseries ids with same timestamp: avg|min|max|sum|none
        :param order: order by a timestamp asc|desc|none. Default is "asc" here.
        :param with_ids: list of ids to aggregate in result
        :param limit: limit of entries to return
        :param include_deleted: allow to get if ogit/_is-deleted=true
        :return: The result payload. Either a list of dict or a dict with an error message.
        """
        query = {
            "from": starttime,
            "to": endtime,
            "include_deleted": include_deleted,
            "limit": limit,
            "with": with_ids,
            "order": order,
            "aggregate": aggregate
        }

        url = self.endpoint + '/' + quote_plus(node_id) + '/values' + self._get_query_part(query)
        res = self.get(url)
        if 'error' in res:
            return res
        timeseries: list = res['items']
        return timeseries

    def get_timeseries_history(self,
                               node_id: str,
                               timestamp: str = None,
                               include_deleted: bool = None) -> Union[List, Dict]:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Timeseries/get__id__values_history

        :param node_id: ogit/_id of the node containing timeseries
        :param timestamp: timestamp in ms
        :param include_deleted: allow to get if ogit/_is-deleted=true
        :return: The result payload. Either a list of dict or a dict with an error message.
        """
        query = {
            "include_deleted": include_deleted,
            "timestamp": timestamp
        }

        url = self.endpoint + '/' + quote_plus(node_id) + '/values/history' + self._get_query_part(query)
        res = self.get(url)
        if 'error' in res:
            return res
        timeseries: list = res['items']
        return timeseries

    def query_timeseries(self,
                         starttime: str = None,
                         endtime: str = None,
                         limit: int = None,
                         order: str = "asc",
                         aggregate: str = None) -> Union[List, Dict]:
        """
        Run a query against the graph and return agragated timeseries values for timeseries vertices matching
        query result. query: Entities with matching ogit/_type:ogit/Timeseries

        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Search/get_query_values

        :param starttime: ms since epoch.
        :param endtime: ms since epoch.
        :param aggregate: aggregate numeric values for multiple timeseries ids with same timestamp: avg|min|max|sum|none
        :param order: order by a timestamp asc|desc|none. Default is "asc" here.
        :param limit: limit of entries to return
        :return: The result payload. Either a list of dict or a dict with an error message.
        """
        query = {
            "from": starttime,
            "to": endtime,
            "limit": limit,
            "order": order,
            "aggregate": aggregate
        }

        url = self.endpoint + '/query/values' + self._get_query_part(query)
        res = self.get(url)
        if 'error' in res:
            return res
        timeseries: list = res['items']
        return timeseries

    def post_timeseries(self,
                        node_id: str,
                        items: list,
                        synchronous: bool = True,
                        ttl: int = None) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Storage]_Timeseries/post__id__values

        :param synchronous: whether the operation should return synchronously. Default is True here.
        :param ttl: time to live for values to be stored in seconds (overrides /ttl in vertex).
        :param node_id: ogit/_id of the node containing timeseries
        :param items: list of timeseries values [{timestamp: (ms since epoch), value: ...},...]
        :return: The result payload
        """

        query = {
            "synchronous": synchronous,
            "ttl": ttl
        }

        url = self.endpoint + '/' + quote_plus(node_id) + '/values' + self._get_query_part(query)
        data = {"items": items}
        return self.post(url, data)

    def get_attachment(self,
                       node_id: str,
                       content_id: str = None,
                       include_deleted: bool = None) -> Iterator[bytes]:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_Blob/get__id__content

        :param node_id: Id of the attachment node
        :param content_id: Id of the content within the attachment node. Default is None.
        :param include_deleted: Whether to be able to access deleted content: Default is False
        :return: Returns generator over byte chunks from the response body payload.
        """
        query = {
            "contentId": content_id,
            "includeDeleted": include_deleted
        }

        url = self.endpoint + '/' + quote_plus(node_id) + '/content' + self._get_query_part(query)
        yield from self.get_binary(url)

    def post_attachment(self,
                        node_id: str,
                        data: Any,
                        content_type: str = None) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Storage]_Blob/post__id__content

        :param node_id: Id of the attachment node
        :param data: Data to upload in binary form. Can also be an IO object for streaming.
        :param content_type: Content-Type for *data*. Defaults to 'application/octet-stream' if left unset.
        :return: The result payload
        """
        url = self.endpoint + '/' + quote_plus(node_id) + '/content'
        return self.post_binary(url, data, content_type=content_type)

    def get_history(self,
                    node_id: str,
                    ts_from: int = 0,
                    ts_to: int = datetime.datetime.now(),
                    history_type: str = 'element',
                    version: str = None,
                    vid: str = None,
                    limit=-1,
                    offset=0,
                    include_deleted: bool = None,
                    meta: bool = None
                    ) -> dict:
        """
        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Query]_History/get__id__history

        :param node_id: Id of the node
        :param ts_from: timestamp in ms where to start returning entries (default: 0)
        :param ts_to: timestamp in ms where to end returning entries (default: now)
        :param history_type: Response format:
                             full - full event,
                             element - only event body,
                             diff - diff to previous event.
                             (default: 'element')
        :param version: get entry with specific ogit/_v value
        :param vid: get specific version of Entity matching ogit/_v-id
        :param limit: limit of entries to return (default: -1).
        :param offset: offset where to start returning entries (default: 0)
        :param include_deleted: allow to get if ogit/_is-deleted=true (default: false)
        :param meta: return list type attributes with metadata (default: false)
        :return: The result payload
        """

        query = {
            "from": ts_from,
            "to": ts_to,
            "type": history_type,
            "version": version,
            "vid": vid,
            "limit": limit,
            "offset": offset,
            "includeDeleted": include_deleted,
            "listMeta": meta
        }

        url = self.endpoint + '/' + quote_plus(node_id) + '/history' + self._get_query_part(query)
        return self.get(url)

    def get_events(self,
                   ts_from: int = 0,
                   ts_to: int = datetime.datetime.now(),
                   ogit_type: str = None,
                   jfilter: str = None) -> dict:
        """
        Replays events from history

        https://core.arago.co/help/specs/?url=definitions/graph.yaml#/[Events]_History/get_events_

        :param ts_from: timestamp in ms where to start returning entries (default: 0)
        :param ts_to: timestamp in ms where to end returning entries (default: now)
        :param jfilter: jfilter string to limit matching results
        :param ogit_type: Entity or Verb ogit/_type for filtering result based on this type
        :return: The result payload
        """

        query = {
            "from": ts_from,
            "to": ts_to,
            "type": ogit_type,
            "filter": jfilter
        }

        url = self.endpoint + '/events' + self._get_query_part(query)
        return self.get(url)
