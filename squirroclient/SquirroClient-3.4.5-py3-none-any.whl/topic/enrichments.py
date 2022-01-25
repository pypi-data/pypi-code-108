import json
import urllib.error
import urllib.parse
import urllib.request


class EnrichmentsMixin(object):
    def create_enrichment(self, project_id, type, name, config, before=None):
        """Create a new enrichment on the project.

        :param project_id: Project identifier. Enrichment will be created in
            this project.
        :param type: Enrichment type. Possible values: `pipelet`, `keyword`.
        :param name: The new name of the enrichment.
        :param config: The configuration of the new enrichment. This is an
            dictionary and the contents depends on the type.
        :param before: The stage before which to run this enrichment (only
            valid for pipelet enrichments).
        :returns: The new enrichment.

        Example::

            >>> client.create_enrichment('Sz7LLLbyTzy_SddblwIxaA', 'pipelet',
            ...                          'TextRazor', {
            ...     'pipelet': 'tenant-example/textrazor',
            ...     'api_key': 'TextRazor-API-Key'})
            {
                u'type': u'pipelet',
                u'config': {u'api_key': u'TextRazor-API-Key',
                            u'pipelet': u'tenant-example/textrazor'},
                u'name': u'TextRazor',
                u'id': u'pipelet-rTBoGNl6S4aG4TDkBoN6xQ'
            }
        """
        data = {"type": type, "name": name, "config": config}
        if before:
            data["before"] = before
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/enrichments" % {
            "ep": self.topic_api_url,
            "project_id": project_id,
            "tenant": self.tenant,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def get_enrichments(self, project_id, type=None):
        """Return enrichments configured on this project.

        :param project_id: Project identifier. Enrichments are retrieved from
            this project.
        :param type: Type of enlistments to list or None for all types

        Example::

            >>> client.get_enrichments('Sz7LLLbyTzy_SddblwIxaA', 'pipelet')
            [{
                u'type': u'pipelet',
                u'config': {u'api_key': u'TextRazor-API-Key',
                            u'pipelet': u'tenant-example/textrazor'},
                u'name': u'TextRazor',
                u'id': u'pipelet-rTBoGNl6S4aG4TDkBoN6xQ'
            }]
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/enrichments" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        # build params
        params = {}
        if type is not None:
            params["type"] = type

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def get_enrichment(self, project_id, enrichment_id):
        """Returns a single enrichment configured on this project.

        :param project_id: Project identifier. Enrichment must exist in this
            project.
        :param enrichment_id: Enrichment identifier.

        Example::

            >>> client.get_enrichment('Sz7LLLbyTzy_SddblwIxaA',
            ...                       'pipelet-rTBoGNl6S4aG4TDkBoN6xQ',
            ...                       'pipelet'})
            {
                u'type': u'pipelet',
                u'config': {u'api_key': u'TextRazor-API-Key',
                            u'pipelet': u'tenant-example/textrazor'},
                u'name': u'TextRazor',
                u'id': u'pipelet-rTBoGNl6S4aG4TDkBoN6xQ'
            }
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "enrichments/%(enrichment_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "enrichment_id": urllib.parse.quote_plus(enrichment_id),
        }

        res = self._perform_request("get", url)
        return self._process_response(res)

    def delete_enrichment(self, project_id, enrichment_id):
        """Delete a single enrichment configured on this project.

        :param project_id: Project identifier. Enrichment must exist in this
            project.
        :param enrichment_id: Enrichment identifier.

        Example::

            >>> client.delete_enrichment('Sz7LLLbyTzy_SddblwIxaA',
            ...                          'pipelet-rTBoGNl6S4aG4TDkBoN6xQ')
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "enrichments/%(enrichment_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "enrichment_id": urllib.parse.quote_plus(enrichment_id),
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def update_enrichment(self, project_id, enrichment_id, name, config):
        """Update a single enrichment configured on this project.

        :param project_id: Project identifier. Enrichment must exist in this
            project.
        :param enrichment_id: Enrichment identifier.
        :param name: The new name of the enrichment.
        :param config: The new configuration of the enrichment. This is an
            dictionary and the contents depends on the type.
        :returns: The modified enrichment.

        Example::

            >>> client.update_enrichment('Sz7LLLbyTzy_SddblwIxaA',
             'pipelet-rTBoGNl6S4aG4TDkBoN6xQ',
             'TextRazor', {'pipelet': 'tenant-example/textrazor',
             'api_key': 'New-Key'})
            {
                u'type': u'pipelet',
                u'config': {
                    u'api_key': u'New-Key',
                    u'pipelet': u'tenant-example/textrazor'
                },
                u'name': u'TextRazor',
                u'id': u'pipelet-rTBoGNl6S4aG4TDkBoN6xQ'
            }
        """
        data = {"name": name, "config": config}
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "enrichments/%(enrichment_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "enrichment_id": urllib.parse.quote_plus(enrichment_id),
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)
