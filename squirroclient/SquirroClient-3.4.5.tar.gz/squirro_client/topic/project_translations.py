import json
import logging

log = logging.getLogger(__name__)


class ProjectTranslationsMixin(object):
    def get_project_translations(self, project_id, language=None):
        """ Get language translations for the provided project.

        :param project_id: Identifier of the project
        :param language: (Optional) language to select the translations by
        :returns: A list of translations.

        Example::

            >>> client.get_project_translations("project_uuid1")
            [
                {
                    "key":":cancel",
                    "en": "Cancel",
                    "de": "Abbrechen",
                },
                {
                    "key": ":yes",
                    "en": "Yes",
                    "de": "Ja",
                },
            ]

        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/project_translations"
            % {
                "ep": self.topic_api_url,
                "version": self.version,
                "tenant": self.tenant,
                "project_id": project_id,
            }
        )

        if language:
            params = {"language": language}
        else:
            params = {}
        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_project_translations(self, project_id, translations):
        """ Create new language translation set. Note: the existing translation set
        gets overwritten.

        :param project_id: Identifier of the project
        :param translations: List of language translations
        :return:

        Example::

            >>> client.new_project_translations("project_uuid1",
                    [{"key":":yes","en":"Yes","de": "Ja"}]
                )
            [
                {
                    "key": ":yes",
                    "en": "Yes",
                    "de": "Ja",
                },
            ]
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/project_translations"
            % {
                "ep": self.topic_api_url,
                "version": self.version,
                "tenant": self.tenant,
                "project_id": project_id,
            }
        )

        data = json.dumps(translations)

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("post", url, data=data, headers=headers)
        return self._process_response(res, [200])

    def modify_project_translations(self, project_id, translations):
        """ Update language translation set.

        :param project_id: Identifier of the project
        :param translations: List of language translations
        :return:

        Example::

            >>> client.modify_project_translations("project_uuid1",
                    [{"key":"cancel","en":"Cancel","de": "Abbrechen"}]
                )
            [
                {
                    "key":":cancel",
                    "en": "Cancel",
                    "de": "Abbrechen",
                },
                {
                    "key": ":yes",
                    "en": "Yes",
                    "de": "Ja",
                },
            ]
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/project_translations"
            % {
                "ep": self.topic_api_url,
                "version": self.version,
                "tenant": self.tenant,
                "project_id": project_id,
            }
        )

        data = json.dumps(translations)

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("put", url, data=data, headers=headers)
        return self._process_response(res, [200])
