import json
import logging

log = logging.getLogger(__name__)


class CommunityTypesMixin(object):
    def get_community_types(self, project_id):
        """Returns all community types for a particular project.

        :param project_id: Project Identifier

        Example::

            >>> client.get_community_types('Xh9CeyQtTYe2cv5F11e6nQ')
            [
                {
                "id": "9WArQ7hhRUeEkg3_CLdfLA",
                "created_at": "2020-09-09T15:19:38",
                "modified_at": "2020-09-09T15:19:38",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_2",
                "facet": "Country"
                },
                {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Company"
                }
            ]
        """

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/community_types" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_community_type(
        self,
        project_id,
        community_type_id,
        include_communities=False,
        start=None,
        count=-1,
        community_partial_name=None,
        include_count_of_items=False,
    ):
        """Returns a community types for a project
        given the community_type_id

        :param project_id: Project Identifier
        :param community_type_id: Community type Identifier
        :param include_communities: Boolean argument to include all the communities
            belonging to the community type with id `community_type_id`. Defaults
            to False.
        :param start: Integer. Used for pagination of objects. If set, the
            objects starting with offset `start` are returned. Defaults to None.
        :param count: Integer. Used for pagination of objects. If set, `count`
            number of communities are returned. To return all communities, set
            to -1. Defaults to -1.
        :param community_partial_name: Argument to filter communities by name.
        :param include_count_of_items: Boolean argument to include the count of
            items belonging to the communities of community type `community_type_id`.
            Defaults to False.

        Example::

            >>> client.get_community_type(
                'Xh9CeyQtTYe2cv5F11e6nQ',
                'LB5Q-GmBSbaNvJhUxXfUaA'
            )
            {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Company"
            }
        """

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "community_types/%(community_type_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "community_type_id": community_type_id,
        }
        params = {
            "include_communities": include_communities,
            "start": start,
            "count": count,
            "community_partial_name": community_partial_name,
            "include_count_of_items": include_count_of_items,
        }
        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_community_type(self, project_id, name, facet=None):
        """Creates a new community type

        :param project_id: Project Identifier
        :param name: community type name
        :param facet: facet name associated with the community

        Example::

            >>> client.new_community_type(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    'Community_type_1',
                    facet='Company'
                    )
            {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Company"
            }
        """

        url = ("%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "community_types") % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        data = {"name": name}
        if facet:
            data["facet"] = facet

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_community_type(self, project_id, community_type_id, name, facet=None):

        """Modifies a community type

        :param project_id: Project Identifier
        :param community_type_id: Community type Identifier
        :param name: community type name
        :param facet: facet name associated with the community

        Example::

            >>> client.modify_community_type(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    'LB5Q-GmBSbaNvJhUxXfUaA',
                    'Community_type_1',
                    facet='Country',
                )
            {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Country"
            }
        """

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "community_types/%(community_type_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "community_type_id": community_type_id,
        }
        data = {"name": name}
        if facet:
            data["facet"] = facet

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def delete_community_type(self, project_id, community_type_id):
        """Deletes a community type

        :param project_id: Project Identifier
        :param community_type_id: Community type Identifier

        Example::

            >>> client.delete_community_type(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    'LB5Q-GmBSbaNvJhUxXfUaA')
            {}
        """

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "community_types/%(community_type_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "community_type_id": community_type_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
