import json


def make_smartfilter_aliases(cls):
    for funcname in dir(cls):
        if funcname.startswith("_"):
            continue
        new_name = funcname.replace("smartfilter", "fingerprint")
        setattr(cls, new_name, getattr(cls, funcname))
    return cls


@make_smartfilter_aliases
class SmartfiltersMixin(object):
    def get_project_smartfilters(self, project_id, tags=None, include_config=False):
        """Get all smartfilters which are applicable on a project.

        :param project_id: Project identifier.
        :param tags: List of tags which can be used to
            filtering the returned smartfilters.
        :param include_config: Boolean flag whether to include each
            Smart Filter config.
        :returns: A list of smartfilters.

        Example::

            >>> client.get_project_smartfilters('zgxIdCxSRWSwJzL1fwNX1Q')
            []
        """

        url = "%(ep)s/%(version)s/%(tenant)s/projects/" "%(project_id)s/smartfilters"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        params = {}
        if tags is not None:
            params["tags"] = json.dumps(tags)
        if include_config:
            params["include_config"] = True

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def get_smartfilter(self, type, type_id, name):
        """Get a single smartfilter for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :returns: Fingerprint information in a dictionary.

        Example::

            >>> client.get_smartfilter('project', 'zgxIdCxSRWSwJzL1fwNX1Q',
            ...                        'default')
            {}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/smartfilter/%(type)s/%(type_id)s/%(name)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        res = self._perform_request("get", url)
        return self._process_response(res, [200])

    def get_project_smartfilter_scores(self, project_id, tags, fields=None):
        """Get the smartfilter scores for all items contained in the specified
        project. One ore more smartfilters are selected by specifying tags.

        :param project_id: Project identifier.
        :param tags: List of tags.
        :param fields: String of comma-separated item fields to include in the
            result.
        :returns: A list of smartfilter score entries.

        Example::

            >>> client.get_project_smartfilter_scores(
            ...     'Sz7LLLbyTzy_SddblwIxaA', ['poc', 'testing'])
            [{u'fingerprint': {u'filter_min_score': None,
                               u'name': u'ma',
                               u'title': u'',
                               u'type': u'tenant',
                               u'type_id': u'squirro'},
              u'scores': [{u'fields': {u'external_id': u'a38515'},
                           u'noise_level': 0.0},
                          {u'fields': {u'external_id': u'a37402'},
                           u'noise_level': 0.0},
                          {u'fields': {u'external_id': u'a38116'},
                           u'noise_level': 0.1}]},
             {u'fingerprint': {u'filter_min_score': 1.2950184,
                               u'name': u'something',
                               u'title': u'Something',
                               u'type': u'tenant',
                               u'type_id': u'squirro'},
              u'scores': [{u'fields': {u'external_id': u'a38515'},
                           u'noise_level': 0.0},
                          {u'fields': {u'external_id': u'a37402'},
                           u'noise_level': 0.1},
                          {u'fields': {u'external_id': u'a38116'},
                           u'noise_level': 0.1}]}]
        """
        url = "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/scores"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        params = {"tags": json.dumps(tags)}

        if fields is not None:
            params["fields"] = fields

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def validate_smartfilter_attributes(self, data):
        """Validates the attributes syntax of a smartfilter.

        :param data: Fingerprint attributes.

        Valid example::

            >>> data = {'config': {
                'manual_features': 'term1, 1.5, de, Term1\\nterm2, 2.4',
                'default_manual_features_lang': 'de'}}
            >>> client.validate_smartfilter_attributes(data)
            {}

        Invalid example::

            >>> data = {'config': {
                'manual_features': 'invalid, 1.5, de, Term1'}}
            >>> try:
            >>>     client.validate_smartfilter_attributes(data)
            >>> except squirro_client.exceptions.ClientError as e:
            >>>     print e.error
            u'[{"line": 0, "error": "required default language is missing"}]'
        """
        url = "%(ep)s/%(version)s/%(tenant)s/smartfilter/validate"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
        }

        headers = {"Content-Type": "application/json"}

        if data is None:
            data = {}

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [200])

    def new_smartfilter(self, type, type_id, name=None, data=None):
        """Create a new smartfilter for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param data: Fingerprint attributes.

        Example::

            >>> data = {'title': 'Earnings Call'}
            >>> client.new_smartfilter(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default', data)
            {}
        """
        if name:
            url = (
                "%(ep)s/%(version)s/%(tenant)s"
                "/smartfilter/%(type)s/%(type_id)s/%(name)s"
            )
        else:
            url = "%(ep)s/%(version)s/%(tenant)s" "/smartfilter/%(type)s/%(type_id)s"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        headers = {"Content-Type": "application/json"}

        if data is None:
            data = {}

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def copy_smartfilter(self, type, type_id, name):
        """Copies the smartfilter for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.

        Example::

            >>> client.copy_smartfilter('tenant', 'squirro', 'ma')
            {}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/smartfilter/%(type)s/%(type_id)s/%(name)s/copy"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        res = self._perform_request("post", url)
        return self._process_response(res, [201])

    def update_smartfilter_from_content(self, type, type_id, name, content):
        """Updates the smartfilter for the provided parameters from content
        data.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param content: Content data which is a list of dictionaries which
            contain the `lang` and `text` keys.

        Example::

            >>> data = [{'lang': 'en', 'text': 'english content'}]
            >>> client.update_smartfilter_from_content(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default', data)
            {}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/smartfilter/%(type)s/%(type_id)s/%(name)s/content"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        headers = {"Content-Type": "application/json"}

        res = self._perform_request(
            "post", url, data=json.dumps(content), headers=headers
        )
        return self._process_response(res, [204])

    def update_smartfilter_from_items(self, type, type_id, name, items, negative=False):
        """Updates the smartfilter for the provided parameters from items
        data.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param items: List of item identifiers
        :param negative: Boolean, whether to add the items as 'negative' or
            'positive' training definitions. Defaults to False

        Example::

            >>> data = ['tfoOHGEZRAqFURaEE2cPWA']
            >>> client.update_smartfilter_from_items(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default', data)
            {}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/smartfilter/%(type)s/%(type_id)s/%(name)s/items"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        headers = {"Content-Type": "application/json"}

        data = {"item_ids": items, "negative": negative}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [204])

    def update_smartfilter_attributes(self, type, type_id, name, data):
        """Updates the smartfilter key-value attributes for the provided
        parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param data: Fingerprint attributes.

        Example::

            >>> data = {'title': 'Earnings Call'}
            >>> client.update_smartfilter_attributes(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default', data)
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/smartfilter/%(type)s/%(type_id)s/%(name)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [200])

    def delete_smartfilter(self, type, type_id, name):
        """Deletes the smartfilter for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.

        Example::

            >>> client.delete_smartfilter('user', 'bgFtu5rkR1STpx1xR2u1UQ',
            ...                           'default')
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/smartfilter/%(type)s/%(type_id)s/%(name)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    def move_smartfilter(self, type, type_id, name, target_name):
        """Moves the smartfilter for the provided parameters.

        This saves the smartfilter and removes the `temporary` flag. The old
        smartfilter is not removed.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param target_name: Name of move target smartfilter.

        Example::

            >>> client.move_smartfilter('user', 'bgFtu5rkR1STpx1xR2u1UQ',
            ...                         'default')
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/smartfilter/%(type)s/%(type_id)s/%(name)s/move"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        data = {"target_name": target_name}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def protect_smartfilter(self, type, type_id, name, locked):
        """Sets the locked state of a smartfilter.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param locked: Boolean flag to either lock or unlock the smartfilter.

        Example::

            >>> client.protect_smartfilter(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default', True)
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s/smartfilter"
            "/%(type)s/%(type_id)s/%(name)s/protection"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
        }

        data = {"locked": bool(locked)}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [200])

    def get_smartfilter_matches_for_query(
        self, type, type_id, name, language, noise_level=0.1, **kwargs
    ):
        """Returns the match counts for each feature of smartfilter with
        `type`, `type_id` and `name` and the query provide in kwargs.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type id.
        :param name: Fingerprint name.
        :param language: Language for which the matches are being returned.
        :param noise_level: Fingerprint noise_level.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the [[Items#List Items|List Items]]
            resource for all possible parameters.
        :returns: A dictionary which contains the matching feature and counts
            for the query.
        """
        project_id = kwargs.get("project_id")
        assert project_id
        del kwargs["project_id"]

        kwargs["count"] = 0
        fingerprint_matches = {
            "fingerprint_type": type,
            "fingerprint_type_id": type_id,
            "fingerprint_name": name,
            "fingerprint_language": language,
            "noise_level": noise_level,
        }
        kwargs.setdefault("options", {}).update(
            {"fingerprint_matches": fingerprint_matches}
        )

        res = self.query(project_id, **kwargs)
        matches = res.get("fingerprint_matches", {})
        return {"fingerprint_matches": matches}
