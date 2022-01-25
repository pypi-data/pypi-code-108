import json


class FacetsMixin(object):
    def get_facet(self, project_id, facet_id_or_name):
        """Retrieves a facet of project `project_id`.

        :param project_id: Project identifier
        :param facet_id_or_name: Facet identifier or name"""
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/facets/%(id_or_name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "id_or_name": facet_id_or_name,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_facets(self, project_id):
        """Retrieves all facets of project `project_id`.

        :param project_id: Project identifier"""
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/facets" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        res = self._perform_request("get", url)
        retval = self._process_response(res)
        if retval:
            retval = retval.get("facets")
        return retval

    def new_facet(
        self,
        project_id,
        name,
        data_type=None,
        display_name=None,
        group_name=None,
        visible=None,
        format_instr=None,
        searchable=None,
        typeahead=None,
        analyzed=None,
        synonyms_id=None,
    ):
        """Creates a new facet on project `project_id`.

        :param project_id: Project identifier
        :param name: Name of the facet in queries and on incoming items
        :param data_type: One of ('string', 'int', 'float', 'datetime',
                                  'weighted')
        :param analyzed: Valid only for `data_type` 'string'. For other
            data-types, this parameter is set to `False` and can not be
            modified for the time being.
            If True, this string facet will be analyzed for extra features
            like facet-value typeahead, searchability, and alphabetical sorting
            support on this facet. If False, this string facet will not
            support facet-value typeahead, searching, and alphabetical sorting
            at all.
            Although, it can still be used for query filtering, lexical sorting
            and facet-name typeahead.
            This is an immutable property and can not be modified after
            the facet has been created.
            Defaults to 'True' if not specified for string type facets.
            Setting this parameter to False will improve the data loading time.
        :param display_name: Name to show to the user in the frontend
        :param group_name: Label to group this facet under.
        :param visible: If `False` this facet will be hidden in the front-end
        :param format_instr: Formatting instruction for the facet value
            display.
        :param searchable: Flag for enabling and disabling the searchability of
            a facet given that the `analyzed` property of this facet has been
            set to 'True'. If 'True', values for this facet will be searchable.
            Defaults to 'False' if not specified.
        :param typeahead: Boolean Flag for toggling the typeahead given that the
            `analyzed` property of this facet has been set to `True` while creation.
            If `True`, the value as well as the name of this facet will be
            typeaheadable. If `False`, neither the name, nor the value is
            typeaheadable.
            Defaults to `False` if not specified.
        :param synonyms_id: Synonym reference id. If set, the corresponding
            synonyms list will be applied when searching on this field.
            Requires the facet to by analyzed and only has an effect if the
            facet is searchable.

        """
        data = {
            "name": name,
            "data_type": data_type,
            "display_name": display_name,
            "visible": visible,
            "group_name": group_name,
            "format_instr": format_instr,
            "searchable": searchable,
            "typeahead": typeahead,
            "analyzed": analyzed,
            "synonyms_id": synonyms_id,
        }
        data = dict([(k, v) for k, v in data.items() if v is not None])

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/facets" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_facet(
        self,
        project_id,
        id,
        display_name=None,
        group_name=None,
        visible=None,
        format_instr=None,
        searchable=None,
        typeahead=None,
        synonyms_id=None,
        **kwargs
    ):
        """Modifies a facet on project `project_id`.

        :param project_id: Project identifier
        :param id: Facet identifier
        :param display_name: Name to show to the user in the frontend
        :param group_name: Label to group this facet under.
        :param visible: If `False` this facet will be hidden in the front-end
        :param format_instr: Formatting instruction for the facet value
            display.
        :param searchable: Boolean property to enable/disable the
            searchability for this facet. For a 'string' data_type facet, this
            property can only be modified if the 'analyzed' (immutable)
            property of the facet has been set to 'True' while creating the
            facet.
            If False, this facet can still be used as a filter.
        :param typeahead: Boolean property to enable/disable the typeahead for
            this facet.
        :param synonyms_id: Synonym reference id. If set, the corresponding
            synonyms list will be applied when searching on this field.
            Requires the facet to by analyzed and only has an effect if the
            facet is searchable. If value is None then old synonyms is removed
            from facet.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the [[Facets#Update Facet|Update Facet]]
            resource for all possible parameters.
        """
        data = {
            "display_name": display_name,
            "visible": visible,
            "group_name": group_name,
            "format_instr": format_instr,
            "searchable": searchable,
            "typeahead": typeahead,
            "synonyms_id": synonyms_id,
        }
        data.update(**kwargs)
        ACCEPTED_NONE = ["synonyms_id"]
        data = dict(
            [
                (k, v)
                for k, v in data.items()
                if (v is not None) or (v is None and k in ACCEPTED_NONE)
            ]
        )

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/facets/%(id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "id": id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def get_facet_stats(self, project_id, id):
        """Returns stats for a facet on project `project_id`.

        :param project_id: Project identifier
        :param id: Facet identifier

        Example::

            >>> client.get_facet_stats('Sz7LLLbyTzy_SddblwIxaA',
             'da1d234f7e85c4edf37c3286ad7d4ea2c0c64ee8899a5219be21077214719d77'})
            {
                u'all_single_values': True
            }
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "facets/%(id)s/stats"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "id": id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)
