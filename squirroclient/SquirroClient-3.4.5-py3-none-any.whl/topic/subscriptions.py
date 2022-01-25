# TODO: remove this file completely


from ..util import deprecation


class SubscriptionsMixin(object):
    def get_object_subscriptions(
        self, project_id, object_id, user_id=None, filter_deleted=None
    ):
        """
        DEPRECATED: subscriptions no longer exist.

        Get all subscriptions for the provided object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param user_id: User identifier.
        :param filter_deleted: If `True` returns only non-deleted
            subscriptions.
        :returns: A list which contains subscriptions.

        Example::

            >>> client.get_object_subscriptions('2sic33jZTi-ifflvQAVcfw',
            ...                                 '2TBYtWgRRIa23h1rEveI3g')
            [
                {
                    u'config': {
                        u'query': u'squirro',
                        u'vertical': u'News',
                    },
                    u'deleted': False,
                    u'id': u'hw8j7LUBRM28-jAellgQdA',
                    u'link': u'http://bing.com/news/search?q=squirro',
                    u'modified_at': u'2012-10-09T07:54:12',
                    u'provider': u'bing',
                    u'seeder': None,
                    u'source_id': u'2VkLodDHTmiMO3rlWi2MVQ',
                    u'title': u'News Alerts for "squirro" in Switzerland',
                    u'workflow': {
                        u'name': u'Default Workflow',
                        u'project_default': True,
                        u'id': u'kAvdogQOQvGHijqcIPi_WA',
                        u'project_id': u'FzbcEMMNTBeQcG2wnwnxLQ'
                    }
                }
            ]
        """
        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `get_sources` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def get_subscription(self, project_id, object_id, subscription_id):
        """
        DEPRECATED: subscriptions no longer exist.

        Get subscription details.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.
        :returns: A dictionary which contains the subscription.

        Example::

            >>> client.get_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw', '2TBYtWgRRIa23h1rEveI3g',
            ...     'hw8j7LUBRM28-jAellgQdA')
            {
                u'config': {
                    u'query': u'squirro',
                    u'vertical': u'News',
                },
                u'deleted': False,
                u'id': u'hw8j7LUBRM28-jAellgQdA',
                u'link': u'http://bing.com/news/search?q=squirro',
                u'modified_at': u'2012-10-09T07:54:12',
                u'provider': u'bing',
                u'seeder': None,
                u'source_id': u'2VkLodDHTmiMO3rlWi2MVQ',
                u'title': u'News Alerts for "squirro" in Switzerland',
                u'processed': True,
                u'paused': False,
                u'workflow': {
                    u'name': u'Default Workflow',
                    u'project_default': True,
                    u'id': u'kAvdogQOQvGHijqcIPi_WA',
                    u'project_id': u'FzbcEMMNTBeQcG2wnwnxLQ'
                }
            }
        """

        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `get_source` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def new_subscription(
        self,
        project_id,
        object_id,
        provider,
        config,
        user_id=None,
        seeder=None,
        private=None,
        workflow_id=None,
        subscription_id=None,
    ):
        """
        DEPRECATED: subscriptions no longer exist.

        Create a new subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param provider: Provider name.
        :param config: Provider configuration dictionary.
        :param workflow_id: Optional id of the pipeline workflow to apply to
            the data of this subscription. If not specified, then the default
            workflow of the project with `project_id` will be applied.
        :param user_id: User identifier.
        :param seeder: Seeder which manages the subscription.
        :param private: Hints that the contents for this subscriptions should
            be treated as private.
        :param subscription_id: Optional string parameter to create the
            subscription with the provided id. The length of the parameter must
            be 22 characters. Useful when exporting and importing projects
            across multiple Squirro servers.
        :returns: A dictionary which contains the new subscription.

        Example::

            >>> client.new_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw', '2TBYtWgRRIa23h1rEveI3g',
            ...     'feed', {'url': 'http://blog.squirro.com/rss'})
            {u'config': {u'url': u'http://blog.squirro.com/rss'},
             u'deleted': False,
             u'id': u'oTvI6rlaRmKvmYCfCvLwpw',
             u'link': u'http://blog.squirro.com/rss',
             u'modified_at': u'2012-10-12T09:32:09',
             u'provider': u'feed',
             u'seeder': u'team',
             u'source_id': u'D3Q8AiPoTg69bIkqFhe3Bw',
             u'title': u'Squirro',
             u'processed': False,
             u'paused': False,
             u'workflow': {
                u'name': u'Default Workflow',
                u'project_default': True,
                u'id': u'kAvdogQOQvGHijqcIPi_WA',
                u'project_id': u'FzbcEMMNTBeQcG2wnwnxLQ'}
            }
        """

        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `new_sources` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def modify_subscription(
        self, project_id, object_id, subscription_id, workflow_id=None, config=None
    ):
        """
        DEPRECATED: subscriptions no longer exist.

        Modify an existing subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.
        :param workflow_id: Optional workflow id to change subscription to.
        :param config: Changed config of the subscription.

        :returns: A dictionary which contains the subscription.

        Example::

            >>> client.modify_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw',
            ...     '2TBYtWgRRIa23h1rEveI3g',
            ...     'oTvI6rlaRmKvmYCfCvLwpw',
            ...     config={'url': 'http://blog.squirro.com/atom'})
        """

        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `modify_sources` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def delete_subscription(self, project_id, object_id, subscription_id, seeder=None):
        """
        DEPRECATED: subscriptions no longer exist.

        Delete an existing subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.
        :param seeder: Seeder that deletes the subscription.

        Example::

            >>> client.delete_subscription('2sic33jZTi-ifflvQAVcfw',
            ...                            '2TBYtWgRRIa23h1rEveI3g',
            ...                            'oTvI6rlaRmKvmYCfCvLwpw')

        """

        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `delete_sources` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def pause_subscription(self, project_id, object_id, subscription_id):
        """
        DEPRECATED: subscriptions no longer exist.

        Pause a subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.

        Example::

            >>> client.pause_subscription('2sic33jZTi-ifflvQAVcfw',
            ...                           '2TBYtWgRRIa23h1rEveI3g',
            ...                           'hw8j7LUBRM28-jAellgQdA')
        """

        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `pause_sources` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def resume_subscription(self, project_id, object_id, subscription_id):
        """
        DEPRECATED: subscriptions no longer exist.

        Resume a paused subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.

        Example::

            >>> client.resume_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw', '2TBYtWgRRIa23h1rEveI3g',
            ...     'hw8j7LUBRM28-jAellgQdA')
        """

        msg = (
            "Subscriptions are deprecated and replaced with sources. "
            "Please use `resume_sources` instead."
        )
        deprecation(msg)
        raise NotImplementedError(msg)
