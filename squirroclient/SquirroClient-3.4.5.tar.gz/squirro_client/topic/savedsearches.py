import json

from ..exceptions import InputDataError


class SavedSearchesMixin(object):
    def new_savedsearch(
        self,
        scope_type,
        scope_id,
        query,
        name=None,
        actions=None,
        created_before=None,
        created_after=None,
        relative_start=None,
        relative_end=None,
        dashboard_id=None,
    ):
        """Create a new saved search.

        :param scope_type: Saved search scope type.
        :param scope_id: Project identifier.
        :param query: Saved search query.
        :param name: The name of the new saved search.
        :param actions: A list of actions to execute when the saved search
            matches.
        :param created_before: Only show items created before.
        :param created_after: Only show items created after.
        :param relative_start: Relative start date for displaying.
        :param relative_end: Relative end date for displaying.
        :param dashboard_id: Dashboard this query is associated with (query
            will be updated whenever the dashboard changes).
        :returns: A dictionary with created saved search.

        Example::

            >>> client.new_savedsearch(
                    scope_id='2sic33jZTi-ifflvQAVcfw',
                    scope_type='project',
                    query='hello world',
                )
            {u'actions': [{u'id': u'678b8102e5c55683130a469c12f6ce55a97ab8b5',
                           u'type': u'show'}],
             u'id': u'1ba32747c302d1c3cd4f2d43cfe937d7ae64489b',
             u'query': u'hello world'}
        """
        if actions is not None and not isinstance(actions, list):
            raise ValueError("`actions` must be a list")
        url = self._get_savedsearch_base_url(scope_type) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "scope_type": scope_type,
            "project_id": scope_id,
        }
        headers = {"Content-Type": "application/json"}
        data = {
            "query": query,
            "actions": actions,
            "name": name,
            "scope_type": scope_type,
            "created_before": created_before,
            "created_after": created_after,
            "relative_start": relative_start,
            "relative_end": relative_end,
            "dashboard_id": dashboard_id,
        }
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201, 200])

    def modify_savedsearch(
        self,
        savedsearch_id,
        scope_type,
        scope_id,
        query,
        name=None,
        actions=None,
        created_before=None,
        created_after=None,
        relative_start=None,
        relative_end=None,
    ):
        """Modify a saved search.

        :param savedsearch_id: Saved search identifier.
        :param scope_type: Saved search scope type.
        :param scope_id: Project identifier.
        :param query: Saved search query.
        :param name: The new name of the saved search.
        :param actions: A list of actions to execute when the saved search
            matches.
        :param created_before: Only show items created before.
        :param created_after: Only show items created after.
        :param relative_start: Relative start date for displaying.
        :param relative_end: Relative end date for displaying.
        :return: A dictionary with updated saved search data.

        Example::

            >>> client.modify_savedsearch(
                    savedsearch_id='77e2bbb206527a2e1ff2e5baf548656a8cb999cc',
                    scope_id='2sic33jZTi-ifflvQAVcfw',
                    scope_type='project',
                    query='test me'
                )
            {u'actions': [{u'id': u'4e23249793e9a3df2126321109c6619df66aaa51',
                           u'type': u'show'}],
             u'id': u'77e2bbb206527a2e1ff2e5baf548656a8cb999cc',
             u'query': u'test me'}
        """
        url = self._get_savedsearch_base_url(scope_type, savedsearch_id) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "scope_type": scope_type,
            "project_id": scope_id,
            "savedsearch_id": savedsearch_id,
        }
        data = {
            "query": query,
            "actions": actions,
            "name": name,
            "scope_type": scope_type,
            "created_before": created_before,
            "created_after": created_after,
            "relative_start": relative_start,
            "relative_end": relative_end,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def get_savedsearches(self, scope_type, scope_id):
        """Get saved searches for the provided scope.

        :param scope_type: Saved search scope type.
        :param scope_id: Project identifier.
        :returns: A dictionary with data for the saved searches.

        Example::

            >>> client.get_savedsearches(
            ...     scope_type='project', scope_id='2sic33jZTi-ifflvQAVcfw')
            {u'savedsearches': [
                {u'actions': [
                 {u'id': u'ff18180f74ebdf4b964ac8b5dde66531e0acba83',
                  u'type': u'show'}],
                 u'id': u'9c2d1a9002a8a152395d74880528fbe4acadc5a1',
                 u'query': u'hello world',
                 u'relative_start': '24h',
                 u'relative_end': None,
                 u'created_before': None,
                 u'created_after': None}]}
        """
        url = self._get_savedsearch_base_url(scope_type) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "scope_type": scope_type,
            "project_id": scope_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_savedsearch(self, scope_type, scope_id, savedsearch_id):
        """Get saved search details.

        :param scope_type: Saved search scope type.
        :param scope_id: Project identifier.
        :param savedsearch_id: Saved search identifier.
        :returns: A dictionary with saved search data.

        Example::

            >>> client.get_savedsearch(
            ...     scope_type='project', scope_id='2sic33jZTi-ifflvQAVcfw',
            ...     savedsearch_id='77e2bbb206527a2e1ff2e5baf548656a8cb999cc')
            {u'actions': [{u'id': u'4e23249793e9a3df2126321109c6619df66aaa51',
                           u'type': u'show'}],
             u'id': u'77e2bbb206527a2e1ff2e5baf548656a8cb999cc',
             u'query': u'test me',
             u'relative_start': '24h',
             u'relative_end': None,
             u'created_before': None,
             u'created_after': None}
        """

        url = self._get_savedsearch_base_url(scope_type, savedsearch_id) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "scope_type": scope_type,
            "project_id": scope_id,
            "savedsearch_id": savedsearch_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def delete_savedsearch(self, scope_type, scope_id, savedsearch_id):
        """Delete a savedsearch.

        :param scope_type: Saved search scope type.
        :param scope_id: Project identifier.
        :param savedsearch_id: Saved search identifier.

        Example::

            >>> client.delete_savedsearch(
            ...     scope_type='project',
            ...     scope_id='2sic33jZTi-ifflvQAVcfw',
            ...     savedsearch_id='9c2d1a9002a8a152395d74880528fbe4acadc5a1')
        """
        url = self._get_savedsearch_base_url(scope_type, savedsearch_id) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "scope_type": scope_type,
            "project_id": scope_id,
            "savedsearch_id": savedsearch_id,
        }
        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    def _get_savedsearch_base_url(self, scope_type, savedsearch_id=None):
        """Returns the URL template for the saved searches of this scope
        type."""
        parts = ["%(ep)s/v0/%(tenant)s"]

        if scope_type not in ["project", "user"]:
            raise InputDataError(400, "Invalid scope type %r" % scope_type)

        parts.append("/projects/%(project_id)s/savedsearches")

        if savedsearch_id:
            parts.append("/%(savedsearch_id)s")

        parts.append("?scope_type=%(scope_type)s")

        return "".join(parts)
