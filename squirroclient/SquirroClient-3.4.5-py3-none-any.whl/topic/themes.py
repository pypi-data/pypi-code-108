import json


class ThemesMixin(object):
    def get_dashboard_themes(self, project_id):
        """Return all dashboard themes for the given project.

        :param project_id: Project identifier

        :returns: A list of dashboard theme dictionaries.

        Example::

            >>> client.get_dashboard_themes('2aEVClLRRA-vCCIvnuEAvQ')
            [{u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
              u'title': u'Test',
              u'scope': u'custom',
              u'definition': [{u'background': u'#ffffff',
                               u'titleColor': u'#525252',
                               .....}]}]
        """
        url = ("%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "dashboard_themes") % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_dashboard_theme(self, project_id, theme_id):
        """Return a specific dashboard theme from the given project.

        :param project_id: Project identifier
        :param theme_id: Dashboard identifier

        :returns: A dictionary of the given dashboard theme.

        Example::

            >>> client.get_dashboard_theme('2aEVClLRRA-vCCIvnuEAvQ',
            ...                            'G0Tm2SQcTqu2d4GvfyrsMg')
            {u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'title': u'Test',
             u'scope': u'custom',
             u'definition': [{u'background': u'#ffffff',
                             u'titleColor': u'#525252',
                             .....}]}]
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboard_themes/%(theme_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "theme_id": theme_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def new_dashboard_theme(self, project_id, title, definition=None):
        """Create a new dashboard theme.

        :param project_id: Project identifier
        :param title: Theme title
        :param definition: Theme definition

        :returns: Location of new theme.

        Example::

            >>> client.new_dashboard_theme('2aEVClLRRA-vCCIvnuEAvQ',
            ...                            title='Sample')
            {u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'title': u'Test',
             u'scope': u'custom',
             u'definition': [{u'background': u'#ffffff',
                             u'titleColor': u'#525252',
                             .....}]}]
        """
        url = ("%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "dashboard_themes") % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        data = {"title": title, "definition": definition}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_dashboard_theme(self, project_id, theme_id, title=None, definition=None):
        """Update a dashboard theme.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier
        :param title: Dashboard title
        :param definition: Theme definition
        :param widgets: Widgets shown on the dashboard

        :returns: A dictionary of the updated dashboard.

        Example::

            >>> client.modify_dashboard_theme('2aEVClLRRA-vCCIvnuEAvQ',
            ...     'YagQNSecR_ONHxwBmOkkeQ', title='New Title')
            {
                u'id': u'YagQNSecR_ONHxwBmOkkeQ',
                u'title': u'New Title',
                u'definition': [{u'background': u'#ffffff',
                                 u'titleColor': u'#525252',
                                 .....}]}]
            }
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboard_themes/%(theme_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "theme_id": theme_id,
        }
        data = {"title": title, "definition": definition}
        post_data = {}
        for key, value in data.items():
            if value is not None:
                post_data[key] = value
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=json.dumps(post_data), headers=headers
        )
        return self._process_response(res)

    def delete_dashboard_theme(self, project_id, theme_id):
        """Delete a specific dashboard theme from the given project.

        :param project_id: Project identifier
        :param theme_id: Theme identifier

        :returns: No return value.

        Example::

            >>> client.delete_dashboard_theme('2aEVClLRRA-vCCIvnuEAvQ',
            ...                               'Ue1OceLkQlyz21wpPqml9Q')
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboard_themes/%(theme_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "theme_id": theme_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
