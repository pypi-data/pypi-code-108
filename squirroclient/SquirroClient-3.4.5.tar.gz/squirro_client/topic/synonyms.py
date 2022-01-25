import json


class SynonymsMixin(object):
    def new_synonym_list(self, project_id, title, synonyms):
        """Creates a new synonym list

        :param project_id: Project Identifier
        :param title: Synonyms title, use to recognize your synonyms,
            e.g. 'english name synonyms'
        :param synonyms: list of synonym definitions. Each definition is a
            comma separated group of synonyms. Example:
            ['humorous,comical,hilarious', 'attractive,stunning']

        Example::

            >>> client.new_synonym_list('Sz7LLLbyTzy_SddblwIxaA',
             'general english synonyms',
              ['humorous,comical,hilarious,hysterical',
               'attractive,pretty,lovely,stunning'])
            {u'project_id': u'Sz7LLLbyTzy_SddblwIxaA',
             u'synonyms_id': u'H2DKVGU8Sv-GpMlQ7PDnqw',
             u'title': u'general english synonyms',
             u'location': u'/v0/squirro/projects/Sz7LLLbyTzy_SddblwIxaA
             /synonyms/H2DKVGU8Sv-GpMlQ7PDnqw'}

        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/synonyms" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        data = {"title": title, "synonyms": synonyms}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_synonym_list(self, project_id, synonyms_id, title=None, synonyms=None):
        """Modifies an existing synonym list

        :param project_id: Project Identifier
        :param synonyms_id: Synonyms Identifier
        :param title: Synonyms title, use to recognize your synonyms,
            e.g. 'english name synonyms'
        :param synonyms: List of Synonyms definitions. Each definition is a
            comma separated group of synonyms. Example:
            ['humorous,comical,hilarious', 'attractive,stunning']


        Example::

            >>> client.modify_synonym_list('Sz7LLLbyTzy_SddblwIxaA',
             'H2DKVGU8Sv-GpMlQ7PDnqw',
             'english names',
             ['humorous,comical,hilarious,hysterical',
              'attractive,pretty,lovely,stunning'])

        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "synonyms/%(syn_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "syn_id": synonyms_id,
        }
        data = {}
        if title is not None:
            data["title"] = title
        if synonyms is not None:
            data["synonyms"] = synonyms

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [204])

    def get_synonym_lists(self, project_id):
        """Returns all synonym lists for a particular project.

        :param project_id: Project Identifier

        Example::

            >>> client.get_synonym_lists('Sz7LLLbyTzy_SddblwIxaA')
            [
                {
                    "id": "QAxn9i3tShWqrPmIIeVt4w",
                    "created_at": "2020-06-08T12:07:34",
                    "modifield_at": "2020-06-08T12:10:57",
                    "project_id": "Tq416ObCTLKZEHY-RCUSBQ",
                    "title": "Synonyms for Title, Body & Abstract",
                    "synonyms": [
                        "apple, water melon => fruit"
                    ]
                }
            ]
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/synonyms" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_synonym_list(self, project_id, synonyms_id):
        """Returns a synonym list.

        :param project_id: Project Identifier
        :param synonyms_id: Synonyms Identifier

        Example::

            >>> client.get_synonym_list('Sz7LLLbyTzy_SddblwIxaA',
             'H2DKVGU8Sv-GpMlQ7PDnqw')
            {u'project_id': u'Sz7LLLbyTzy_SddblwIxaA',
             u'synonyms_id': u'H2DKVGU8Sv-GpMlQ7PDnqw',
             u'title': u'english names',
             u'synonyms': [
              u'humorous,comical,hilarious,hysterical',
              u'attractive,pretty,lovely,stunning'
             ]}
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "synonyms/%(syn_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "syn_id": synonyms_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def delete_synonym_list(self, project_id, synonyms_id):
        """Deletes a synonym list

        :param project_id: Project Identifier
        :param synonyms_id: Synonyms Identifier

        Example::

            >>> client.delete_synonym_list('Sz7LLLbyTzy_SddblwIxaA',
             'H2DKVGU8Sv-GpMlQ7PDnqw')
            {}
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "synonyms/%(syn_id)s"
        ) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "syn_id": synonyms_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
