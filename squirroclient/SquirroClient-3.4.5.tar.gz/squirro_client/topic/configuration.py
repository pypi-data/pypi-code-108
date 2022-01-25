import json
from typing import Any, Optional, Union


class ConfigurationMixin:
    def get_server_configuration(self):
        """Return all configuration service values from the server namespace.

        :return: Returns a dictionary with the returned data and configuration.
                 The relevant keys in the returned dictionary are:

                 - `cache_ttl`: the number of seconds this response can be
                   cached. This can be changed by modifying the value of the
                   `config.cache-ttl` key.
                 - `namespace`: always set to `server`.
                 - `scope`: always empty (`None`)
                 - `config`: a dictionary mapping the configuration keys to
                   their data. The keys in this sub-dictionary are:

                   - `value`: the current value of the setting.
                   - `default_value`: the original default value of the setting.
                     This is `None` for all user-defined settings.
                   - `type`: The type. Can be `boolean`, `string`, `numeric`,
                     or `dictionary`.
                   - `delete`: what will happen when the deletion is called on
                     this method.

                     - `reset`: the server default value will be restored.
                     - `noop`: nothing will happen, as the value is equivalent
                       to the server default.
                     - `delete`: the setting will be removed, meaning it was a
                       user-defined setting.

                   - `help`: The help text displayed to the user on config
                     editing.

        Example::

            >>> client.get_server_configuration()
            {
                'cache_ttl': 60,
                'namespace': 'server',
                'scope': None,
                'config': {
                    'user.create': {
                        'value': False,
                        'default_value': True,
                        'type': 'boolean',
                        'delete': 'reset',
                        'help': 'Whether new users can be created on this sytemn.'
                    },
                },
                # …
            }
        """
        # Build URL
        url = "{ep}/v0/{tenant}/configuration".format(
            ep=self.topic_api_url, tenant=self.tenant,
        )
        res = self._perform_request("get", url)
        return self._process_response(res)

    def set_server_configuration(self, key, value, type=None):
        """Sets the given configuration key to the provided value in the server
        namespace.

        :param key: The key of the setting to overwrite or define. If the key
                    exists, the existing value is changed. Otherwise a new one
                    is created.
        :param value: The value of the value. Can be a string, number (int),
                    boolean, or dictionary.
        :param type: The type of the value. If this is not provided, the type
                    is automatically inferred from the value. If provided, the
                    type must be the same as the value type, and for built-in
                    settings but be the same as the default type.

                    Valid types are: `boolean`, `string`, `numeric`,
                    `dictionary`.
        :return: Returns a dictionary with the new data of the setting. The keys are:

            - `namespace`: always set to `server`.
            - `scope`: always empty (`None`)
            - `value`: the current value of the setting.
            - `default_value`: the original default value of the setting.
              This is `None` for all user-defined settings.
            - `type`: The type. Can be `boolean`, `string`, `numeric`, or
              `dictionary`.
            - `delete`: what will happen when the deletion is called on
              this method.

              - `reset`: the server default value will be restored.
              - `noop`: nothing will happen, as the value is equivalent to
                the server default.
              - `delete`: the setting will be removed, meaning it was a
                user-defined setting.

            - `help`: The help text displayed to the user on config
              editing.

        Example::

            >>> c.set_server_configuration(key='user.create', value=False)
            {
                'namespace': 'server',
                'scope': None,
                'key': 'user.create',
                'value': False,
                'default_value': True,
                'type': 'boolean',
                'help': 'Whether new users can be created on this system.',
                'delete': 'reset'
            }
        """
        # Build URL
        url = "{ep}/v0/{tenant}/configuration/{key}".format(
            ep=self.topic_api_url, tenant=self.tenant, key=key,
        )
        headers = {"Content-Type": "application/json"}
        post_data = {"value": value, "type": type}
        res = self._perform_request(
            "put", url, data=json.dumps(post_data), headers=headers
        )
        return self._process_response(res, [200])

    def delete_server_configuration(self, key):
        """Deletes the given configuration key from the server namespace.

        For built-in values, the value will be reset to the default. In that
        case the newly valid configuration dictionary is returned.

        For custom values, the value will be deleted irrevocably. `None` is
        returned for this.

        :param key: The key of the setting to delete.
        :return: `None` for custom values, new entry with default values for
            built-in values.

        Example::

            >>> c.delete_server_configuration('topic.custom-locator')
            {
                'key': 'topic.custom-locator',
                'value': False,
                'default_value': False,
                'type': 'boolean',
                'help': 'Whether custom index locators can be defined on Squirro projects.',
                'delete': 'noop',
            }

            >>> c.set_server_configuration(key='user.create', value=False)
            {
                'namespace': 'server',
                'scope': None,
                'key': 'user.create',
                'value': False,
                'default_value': True,
                'type': 'boolean',
                'help': 'Whether new users can be created on this system.',
                'delete': 'reset'
            }
        """

        # Build URL
        url = "{ep}/v0/{tenant}/configuration/{key}".format(
            ep=self.topic_api_url, tenant=self.tenant, key=key,
        )
        res = self._perform_request("delete", url)
        return self._process_response(res, [200, 204])

    def get_project_configuration(self, project_id: str):
        """
        Return all configuration service values from the project namespace.

        :param project_id: Project ID.

        :return: Returns a dictionary with the returned data and configuration.
                The relevant keys in the returned dictionary are:

                - `cache_ttl`: The number of seconds this response can be
                  cached. This can be changed by modifying the value of the
                  `config.cache-ttl` key.
                - `namespace`: Always set to `project`.
                - `scope`: Project ID
                - `config`: A dictionary mapping the configuration keys to
                  their data. The keys in this sub-dictionary are:

                  - `value`: The current value of the setting.
                  - `default_value`: The original default value of the setting.
                    This is `None` for all user-defined settings.
                  - `type`: The type. Can be `boolean`, `string`, `numeric`,
                    or `dictionary`.
                  - `delete`: What will happen when the deletion is called on
                    this method.

                    - `reset`: The project default value will be restored.
                    - `noop`: Nothing will happen, as the value is equivalent
                      to the project default.
                    - `delete`: The setting will be removed, meaning it was a
                      user-defined setting.

                  - `help`: The help text displayed to the user on config
                    editing.

        Example::

            >>> client.get_project_configuration(project_id='d_GZJjMiVgKHHf6-pFWzNQ')
            {
                'cache_ttl': 60,
                'namespace': 'project',
                'scope': 'd_GZJjMiVgKHHf6-pFWzNQ',
                'config': {
                    'topic.typeahead.popular.scope': {
                        'value': 'user',
                        'default_value': 'user',
                        'type': 'string',
                        'delete': 'reset',
                        'help': 'A scope for popular queries (user/project).'
                    },
                },
                # …
            }
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/configuration"
        )
        res = self._perform_request("get", url)
        return self._process_response(res)

    def set_project_configuration(
        self,
        project_id: str,
        key: str,
        value: Union[str, int, bool, dict],
        type: Optional[str] = None,
    ):
        """
        Set the given configuration key to the provided value in the project namespace.

        :param project_id: Project ID.
        :param key: The key of the setting to overwrite or define. If the key
                    exists, the existing value is changed. Otherwise a new one
                    is created.
        :param value: The value of the setting. Can be a string, number (int),
                    boolean, or dictionary.
        :param type: The type of the value. If this is not provided, the type
                    is automatically inferred from the value. If provided, the
                    type must be the same as the value type, and for built-in
                    settings must be the same as the default type.
                    Valid types are: `boolean`, `string`, `numeric`, `dictionary`.

        :return: Returns a dictionary with the new data of the setting. The keys are:

            - `namespace`: Always set to `project`.
            - `scope`: Project ID
            - `value`: The current value of the setting.
            - `default_value`: The original default value of the setting.
              This is `None` for all user-defined settings.
            - `type`: The type. Can be `boolean`, `string`, `numeric`, or `dictionary`.
            - `delete`: What will happen when the deletion is called on this method.

              - `reset`: The project default value will be restored.
              - `noop`: Nothing will happen, as the value is equivalent to
                the project default.
              - `delete`: The setting will be removed, meaning it was a
                user-defined setting.

            - `help`: The help text displayed to the user on config
              editing.

        Example::

            >>> c.set_project_configuration(project_id='d_GZJjMiVgKHHf6-pFWzNQ', key='topic.typeahead.popular.scope', value='project')
            {
                'namespace': 'project',
                'scope': 'd_GZJjMiVgKHHf6-pFWzNQ',
                'key': 'topic.typeahead.popular.scope',
                'value': 'project',
                'default_value': 'user',
                'type': 'string',
                'help': 'A scope for popular queries (user/project).',
                'delete': 'reset'
            }
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/configuration/{key}"
        headers = {"Content-Type": "application/json"}
        post_data = {"value": value, "type": type}
        res = self._perform_request(
            "put", url, data=json.dumps(post_data), headers=headers
        )
        return self._process_response(res, [200])

    def delete_project_configuration(self, project_id: str, key: str):
        """
        Delete the given configuration key from the project namespace.

        For built-in values, the value will be reset to the default. In that
        case the newly valid configuration dictionary is returned.

        For custom values, the value will be deleted irrevocably. Empty dictionary is
        returned for this.

        :param project_id: Project ID.
        :param key: The key of the setting to delete.

        :return: Empty dictionary for custom values, new entry with default values for
            built-in values.

        Example::

            >>> c.delete_project_configuration(project_id='d_GZJjMiVgKHHf6-pFWzNQ', key='topic.typeahead.popular.scope')
            {
                'key': 'topic.typeahead.popular.scope',
                'value': 'user',
                'default_value': 'user,
                'type': 'string',
                'help': 'A scope for popular queries (user/project).',
                'delete': 'noop',
            }
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/configuration/{key}"
        res = self._perform_request("delete", url)
        return self._process_response(res, [200, 204])

    def interpolate_project_configuration(self, project_id: str, value: Any):
        """
        Return project configuration values for the given config references.

        :param project_id: Project ID.
        :param value: Value to interpolate.

        :return: Returns a dictionary contains an interpolated value.

        Example::

            >>> client.interpolate_project_configuration(
                  project_id='d_GZJjMiVgKHHf6-pFWzNQ',
                  value='${topic.snow-url}'
                )
            {
                'value': 'https://mysnow.com',
            }
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/configuration/interpolate"
        headers = {"Content-Type": "application/json"}
        post_data = {"value": value}
        res = self._perform_request(
            "post", url, data=json.dumps(post_data), headers=headers
        )
        return self._process_response(res)
