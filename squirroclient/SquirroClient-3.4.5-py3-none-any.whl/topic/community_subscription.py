import json
import logging

log = logging.getLogger(__name__)


class CommunitySubscriptionsMixin(object):
    def get_community_subscriptions(self, project_id, include_count_of_items=False):
        """Returns all community subscriptions for a project and a user.

        :param project_id: Project Identifier
        :param include_count_of_items: Boolean argument to include the count of
            items belonging to the subscribed communities of the user.
            Defaults to False.

        Example::

            >>> client.get_community_subscriptions('Xh9CeyQtTYe2cv5F11e6nQ')
            [
                {
                "id": "D0nEBlUmTLqxq6lwZj4rTw",
                "user_id": "-XNqd1bARxuA0L1jh3OeeQ",
                "community_id": "OSACPQKbRz2dadBM4nSseA",
                "created_at": "2020-09-14T09:12:21"
                },
                {
                "id": "QmykmwR3Tb6ZEHI6DJQzUg",
                "user_id": "-XNqd1bARxuA0L1jh3OeeQ",
                "community_id": "mNDkc6q9QvuL8EVMWA3cgg",
                "created_at": "2020-09-14T09:17:15"
                }

            ]

        TODO: allow for specifying user id
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/community_subscriptions" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        params = {
            "include_count_of_items": include_count_of_items,
        }
        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_community_subscriptions(
        self, project_id, community_ids, remove_existing_subscriptions=False
    ):
        """Creates a new community subscription for a project
        given the community_id

        :param project_id: Project Identifier
        :param name: community type name

        Example::

            >>> client.new_community_subscription(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    ['mNDkc6q9QvuL8EVMWA3cgg','otCTwaF9Qs-66MFGLCtyKQ']
                    remove_existing_subscriptions = True
                )
            {
                "id": "QmykmwR3Tb6ZEHI6DJQzUg",
                "user_id": "-XNqd1bARxuA0L1jh3OeeQ",
                "community_id": "mNDkc6q9QvuL8EVMWA3cgg",
                "created_at": "2020-09-14T09:17:15"
            }
        """

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/community_subscriptions"
        ) % {"ep": self.topic_api_url, "tenant": self.tenant, "project_id": project_id}
        data = {
            "community_ids": community_ids,
            "remove_existing_subscriptions": remove_existing_subscriptions,
        }

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def delete_community_subscription(self, project_id, subscription_id):

        """Deletes a community subscription

        :param project_id: Project Identifier
        :param subscription_id: Community subscription Identifier

        Example::

            >>> client.delete_community_subscription(
                'Xh9CeyQtTYe2cv5F11e6nQ',
                'mNDkc6q9QvuL8EVMWA3cgg')
            {}
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "community_subscriptions/%(subscription_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "subscription_id": subscription_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
