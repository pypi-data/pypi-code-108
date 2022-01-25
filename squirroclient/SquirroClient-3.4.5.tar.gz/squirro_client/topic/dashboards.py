import json
import logging

from squirro_client.util import deprecation

log = logging.getLogger(__name__)


class DashboardsMixin(object):
    def get_dashboards(self, project_id):
        """Return all dashboard for the given project.

        :param project_id: Project identifier

        :returns: A list of dashboard dictionaries.

        Example::

            >>> client.get_dashboards('2aEVClLRRA-vCCIvnuEAvQ')
            [{u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
              u'search': {u'query': u'Test'},
              u'title': u'Test',
              u'type': u'dashboard',
              u'widgets': [{u'col': 1,
                            u'id': 1,
                            u'row': 1,
                            u'size_x': 1,
                            u'size_y': 1,
                            u'title': u'Search Results',
                            u'type': u'Search'}]}]
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/dashboards" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_dashboard(self, project_id, dashboard_id):
        """Return a specific dashboard from the given project.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :returns: A dictionary of the given dashboard.

        Example::

            >>> client.get_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                      'G0Tm2SQcTqu2d4GvfyrsMg')
            {u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'search': {u'query': u'Test'},
             u'title': u'Test',
             u'type': u'dashboard',
             u'theme_id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'widgets': [{u'col': 1,
                           u'id': 1,
                           u'row': 1,
                           u'size_x': 1,
                           u'size_y': 1,
                           u'title': u'Search Results',
                           u'type': u'Search'}]}
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def new_dashboard(
        self,
        project_id,
        title,
        search=None,
        type=None,
        column_count=None,
        row_height=None,
        theme_id=None,
        hide_title=None,
        reset_placement=None,
        sections=None,
        panels=None,
        sidepanel=None,
        mobileSections=None,
        loaders=None,
        desyncFromDesktop=None,
        dashboard_id=None,
        restricted=None,
        default_store=None,
        transparent=None,
        layout=None,
    ):
        """Create a new dashboard.

        :param project_id: Project identifier
        :param title: Dashboard title
        :param search: Search parameters for the dashboard
        :param type: Dashboard type (`dashboard` or `result`). The latter is
            used for the chart view in the UI and not displayed as a dashboard
            tab.
        :param column_count: Number of columns on this dashboard. Used by
            the frontend to render the widgets in the correct size.
        :param row_height: Height in pixels of each row on this dashboard. Used
            by the frontend to render the widgets in the correct size.
        :param theme_id: Dashboard theme identifier
        :param hide_title: Boolean, whether to hide the dashboard title when
            shared
        :param reset_placement: Position of the filter reset flyout, either
            `left` or `right` is supported
        :param sections: Deprecated please use panels instead
        :param panels: List of dashboard panels
        :param sidepanel: Boolean, whether to show the sidepanel or not
        :param mobileSections: Deprecated please use panels instead
        :param desyncFromDesktop: Boolean, whether to prevent syncing the
            mobile content to desktop version or not
        :param dashboard_id: Optional string parameter to create the
            dashboard with the provided id. The length of the parameter must
            be 22 characters. Useful when exporting and importing projects
            across multiple Squirro servers.
        :param restricted: Boolean, whether the dashboard has permissions set
        :param default_store: Dict, dashboard default store state to be saved
            with the dashboard
        :param transparent: Boolean, whether the dashboard uses a transparent
            background or not
        :param layout: Dict, Dashboard layout configuration

        :returns: A list of dashboard dictionaries.

        Example::

            >>> client.new_dashboard('2aEVClLRRA-vCCIvnuEAvQ', title='Sample')
                {u'column_count': 16,
                 u'hide_title': False,
                 u'id': u'8N38s1XsTAKE39TFC4kTkg',
                 u'reset_placement': u'right',
                 u'row_height': 55,
                 u'search': None,
                 u'panels': [],
                 u'default_store': {},
                 u'desyncFromDesktop': False,
                 u'sidepanel': False,
                 u'transparent': False,
                 u'theme': {
                     u'definition': {
                         u'activeColor': u'#e55100',
                         u'background': u'#ffffff',
                         u'borderColor': u'#BDBDBD',
                         u'borderRadius': 2,
                         u'headerHeight': 30,
                         u'marginBottom': 70,
                         u'marginLeft': 10,
                         u'marginRight': 10,
                         u'marginTop': 10,
                         u'titleColor': u'#616161',
                         u'titleFontSize': 17,
                         u'titleFontWeight': u'normal',
                         u'titleTextAlignment': u'left',
                         u'widgetGap': 5,
                         u'widgets': {
                             u'Chord': {
                                 u'activeBackground': u'#f5f5f5',
                                 u'activeColor': u'#e55100',
                                 u'background': u'#ffffff',
                                 u'chartColorScheme': [
                                     u'#4b8ecc',
                                     u'#348f5f',
                                     u'#ec6a2b',
                                     u'#807dba',
                                     u'#fec44f',
                                     u'#009994',
                                     u'#d43131',
                                     u'#0d7074'
                                 ],
                                 u'headerAlignment': u'left',
                                 u'headerBackground': u'#F5F5F5',
                                 u'headerColor': u'#b6b6b6',
                                 u'headerFontSize': 17,
                                 u'headerFontWeight': u'normal',
                                 u'linkBackground': u'#f5f5f5',
                                 u'linkColor': u'#2196F3',
                                 u'paddingBottom': 10,
                                 u'paddingLeft': 10,
                                 u'paddingRight': 10,
                                 u'paddingTop': 5,
                                 u'primaryButtonGradient1': u'#1484f9',
                                 u'primaryButtonGradient2': u'#156fcc',
                                 u'textColor': u'#212121'
                                 },
                             u'Connection': {
                                 u'color': u'#212121',
                                 u'fontAlign': u'center',
                                 u'fontSize': u'13',
                                 u'fontWeight': u'normal',
                                 u'hoverColor': u'#E3F2FD',
                                 u'labelColor': u'#212121',
                                 u'primaryButtonGradient1': u'#FFECB3',
                                 u'primaryButtonGradient2': u'#EF5350'
                             },
                             u'Facets': {u'labelColor': u'#212121'},
                             u'FacetsHistogram': {
                                 u'labelColor': u'#212121',
                                 u'legendColor': u'#212121'
                             },
                             u'FacetsList': {
                                 u'activeColor': u'#e55100',
                                 u'barColor': u'#1484f9',
                                 u'facetValueColor': u'#bdbdbd'
                             },
                             u'FacetsTable': {
                                 u'activeBackground': u'#F5F5F5',
                                 u'activeColor': u'#e55100',
                                 u'headerColor': u'#616161'
                             },
                             u'Frequency': {u'labelColor': u'#212121'},
                             u'HorizontalResultList': {
                                 u'linkColor': u'#2196F3',
                                 u'subtitleColor': u'#616161'
                             },
                             u'IFrame': {},
                             u'Keywords': {
                                 u'barColor': u'#1484f9',
                                 u'headerColor': u'#616161',
                                 u'linkColor': u'#2196F3'
                             },
                             u'PredQuery': {
                                 u'activeBackground': u'#F5F5F5',
                                 u'activeColor': u'#e55100'
                             },
                             u'Search': {
                                 u'activeColor': u'#e55100',
                                 u'titleColor': u'#616161',
                                 u'titleColorRead': u'#212121',
                                 u'titleFontSize': 15,
                                 u'titleFontSizeRead': 15,
                                 u'titleFontWeight': u'bolder',
                                 u'titleFontWeightRead': u'bolder',
                                 u'titleTextAlignment': u'left',
                                 u'titleTextAlignmentRead': u'left'
                             },
                             u'SearchQuery': {
                                 u'backgroundColor': u'#428bca',
                                 u'borderColor': u'#1e88e5',
                                 u'textColor': u'#ffffff'
                             },
                             u'SignificantTerms': {},
                             u'TagCloud': {},
                             u'default': {
                                 u'activeBackground': u'#f5f5f5',
                                 u'activeColor': u'#e55100',
                                 u'background': u'#ffffff',
                                 u'chartColorScheme': [
                                     u'#64b5f6',
                                     u'#E57373',
                                     u'#FFD54F',
                                     u'#81C784',
                                     u'#7986CB',
                                     u'#4DD0E1',
                                     u'#F06292',
                                     u'#AED581',
                                     u'#A1887F',
                                     u'#FFB74D',
                                     u'#4FC3F7',
                                     u'#FF8A65',
                                     u'#DCE775',
                                     u'#BA68C8'
                                 ],
                                 u'headerAlignment': u'left',
                                 u'headerBackground': u'#F5F5F5',
                                 u'headerColor': u'#616161',
                                 u'headerFontSize': 17,
                                 u'headerFontWeight': u'normal',
                                 u'linkBackground': u'#f5f5f5',
                                 u'linkColor': u'#2196F3',
                                 u'paddingBottom': 10,
                                 u'paddingLeft': 10,
                                 u'paddingRight': 10,
                                 u'paddingTop': 5,
                                 u'textColor': u'#212121'
                             }
                         }
                     },
                     u'id': u'ofVfiQ-uRWSZeGFZspH9nQ',
                     u'scope': u'default',
                     u'title': u'Squirro Default'},
                    u'theme_id': u'ofVfiQ-uRWSZeGFZspH9nQ',
                    u'title': u'foo',
                    u'type': u'dashboard',
                    u'layout': {}
                }
        """
        if mobileSections:
            msg = "MobileSections are deprecated please use panels instead"
            deprecation(msg)
        if sections:
            msg = "Sections are deprecated please use panels instead"
            deprecation(msg)

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/dashboards" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        data = {
            "title": title,
            "search": search,
            "type": type,
            "panels": panels,
            "desyncFromDesktop": desyncFromDesktop,
            "sidepanel": sidepanel,
            "loaders": loaders,
            "transparent": transparent,
            "layout": layout,
        }
        if dashboard_id:
            data["dashboard_id"] = dashboard_id

        if column_count:
            data["column_count"] = column_count
        if row_height:
            data["row_height"] = row_height
        if theme_id:
            data["theme_id"] = theme_id
        if hide_title:
            data["hide_title"] = hide_title
        if reset_placement:
            data["reset_placement"] = reset_placement
        if restricted:
            data["restricted"] = restricted
        if default_store:
            data["default_store"] = default_store

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_dashboard(
        self,
        project_id,
        dashboard_id,
        title=None,
        search=None,
        type=None,
        column_count=None,
        row_height=None,
        theme_id=None,
        hide_title=None,
        reset_placement=None,
        sections=None,
        panels=None,
        sidepanel=None,
        loaders=None,
        widgets=None,
        mobileSections=None,
        desyncFromDesktop=None,
        restricted=None,
        default_store=None,
        master=None,
        role=None,
        transparent=None,
        layout=None,
    ):
        """Update a dashboard.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier
        :param title: Dashboard title
        :param search: Search parameters for the dashboard
        :param type: Dashboard type
        :param column_count: Number of columns on this dashboard. Used by
            the frontend to render the widgets in the correct size.
        :param row_height: Height in pixels of each row on this dashboard. Used
            by the frontend to render the widgets in the correct size.
        :param theme_id: Associated theme id
        :param hide_title: Boolean, whether to hide the dashboard title when
            shared
        :param reset_placement: Position of the filter reset flyout, either
            `left` or `right` is supported
        :param sections: Deprecated please use panels instead
        :param panels: List of dashboard panels
        :param widgets: Deprecated please use panels instead
        :param sidepanel: Boolean, whether to show the sidepanel or not
        :param mobileSections: Deprecated please use panels instead
        :param desyncFromDesktop: Boolean, whether to sync the mobile content
            to desktop version or not
        :param restricted: Boolean, whether the dashboard has permissions set
        :param default_store: Dict, dashboard default store state to be saved
            with the dashboard
        :param master: Deprecated, use `role` instead
        :param role: str, Defines the role of a dashboard.
            Valid values are "search" & "normal"
        :param transparent: Boolean, whether the dashboard uses a transparent
            background or not
        :param layout: Dict, Dashboard layout configuration

        :returns: A dictionary of the updated dashboard.

        Example::

            >>> client.modify_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                         'YagQNSecR_ONHxwBmOkkeQ',
            ...                         search={'query': 'Demo'})
        """
        if mobileSections:
            msg = "MobileSections are deprecated please use panels instead"
            deprecation(msg)
        if sections:
            msg = "Sections are deprecated please use panels instead"
            deprecation(msg)
        if widgets:
            msg = "Widgets are deprecated please use panels instead"
            deprecation(msg)
        if master is not None:
            msg = "`master` parameter is deprecated, please use `role` instead"
            deprecation(msg)

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        data = {
            "title": title,
            "search": search,
            "type": type,
            "column_count": column_count,
            "row_height": row_height,
            "theme_id": theme_id,
            "hide_title": hide_title,
            "reset_placement": reset_placement,
            "panels": panels,
            "desyncFromDesktop": desyncFromDesktop,
            "sidepanel": sidepanel,
            "loaders": loaders,
            "restricted": restricted,
            "default_store": default_store,
            "transparent": transparent,
            "layout": layout,
        }

        if master is not None:
            data["master"] = master
        if role is not None:
            data["role"] = role

        post_data = {}
        for key, value in data.items():
            if value is not None:
                post_data[key] = value
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=json.dumps(post_data), headers=headers
        )
        return self._process_response(res)

    def move_dashboard(self, project_id, dashboard_id, after):
        """Move a dashboard.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier
        :param after: The dashboard identifier after which the dashboard should
            be moved. Can be `None` to move the dashboard to the beginning
            of the list.

        :returns: No return value.

        Example::

            >>> client.move_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                       'Ue1OceLkQlyz21wpPqml9Q',
            ...                       'nJXpKUSERmSgQRjxX7LrZw')
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s/move"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=json.dumps({"after": after}), headers=headers
        )
        return self._process_response(res, [204])

    def delete_dashboard(self, project_id, dashboard_id):
        """Delete a specific dashboard from the given project.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :returns: No return value.

        Example::

            >>> client.delete_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                         'Ue1OceLkQlyz21wpPqml9Q')
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_dashboard_permissions(self, project_id, dashboard_id):
        """Return the dashboard permissions for a specific dashboard from
         the given project.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :returns: A dictionary containing:

            * `permissions`: A list of the dashboard permission dictionaries.
            * `is_default`: a boolean flag indicating whether these are the
              default permissions on the dashboard (based on project
              membership) or not (i.e. based on explicitly saved dashboard
              permissions)

        Example::

            >>> client.get_dashboard_permisssions('2aEVClLRRA-vCCIvnuEAvQ',
            ...                      'G0Tm2SQcTqu2d4GvfyrsMg')
            {
                'permissions':
                [
                    {
                        'id': 'dashboard_permission_id',
                        'user_id': 'some_user_id',
                        'user': 'username',
                        'project_role': 'member',
                        'permission': 'view_and_edit',
                        'dashboard_id': 'some_id'
                    },
                    {
                        'id': 'dashboard_permission_id',
                        'group_id': 'some_user_id',
                        'group': 'group_name',
                        'project_role': 'admin',
                        'permission': 'view_and_edit',
                        'dashboard_id': 'some_id'
                    }
                ],
                'is_default': True
            }
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s/permissions"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def create_dashboard_permissions(self, project_id, dashboard_id, permissions_list):
        """(re)Create dashboard permissions for a specific project.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier
        :param permissions_list: A list of all the permissions to create.
            The permissions_list must be superset of the default permissions
            for a dashboard, since it is impossible to remove the admin from a
            permission list

        :returns: A list of the users/groups with permissions for the dashboard

        Example::

            permissions_list = [
                {
                    'user_id': 'some_user_id',
                    'permission': 'view_and_edit',
                    'dashboard_id': 'dashboard_id'
                }
            ]

            >>> client.create_dashboard_permissions('2aEVClLRRA-vCCIvnuEAvQ',
            ...                 'G0Tm2SQcTqu2d4GvfyrsMg', permissions_list)
            {
                'permissions':
                [
                    {
                        'user_id': 'some_user_id',
                        'permission': 'view_and_edit',
                        'dashboard_id': 'dashboard_id'
                    }
                ]
            }
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s/permissions"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=json.dumps(permissions_list), headers=headers
        )
        return self._process_response(res)

    def set_default_dashboard_permissions(self, project_id, dashboard_id):
        """
        This is a helper method to create default (admin-only) dashboard
        permissions with one call. It is equivalent to get_dashboard_permissions
        followed by set_dashboard_permissions (with an appropriate response
        handling from the get call)

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :return: 201 if successful, or 400 if the dashboard already had custom
            permissions in place.
        """
        res_get = self.get_dashboard_permissions(project_id, dashboard_id)
        is_default = res_get.get("is_default")
        if not is_default:
            msg = "Dashboard already has permissions"
            log.warning(msg)
            return {"error": msg}

        permissions = res_get.get("permissions")
        res_post = self.create_dashboard_permissions(
            project_id, dashboard_id, permissions
        )
        # Return whatever we got from the create POST
        return res_post

    def delete_dashboard_permissions(self, project_id, dashboard_id):
        """Delete all permissions from the dashboard, so that the permissions
        fall back to default (project default, i.e. Admins and Members can
        read and edit, Readers can view only)

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :returns: A 204 status code if successful

        Example::
            >>> client.delete_dashboard_permissions('2aEVClLRRA-vCCIvnuEAvQ',
            ...                 'G0Tm2SQcTqu2d4GvfyrsMg')
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "dashboards/%(dashboard_id)s/permissions"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "dashboard_id": dashboard_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
