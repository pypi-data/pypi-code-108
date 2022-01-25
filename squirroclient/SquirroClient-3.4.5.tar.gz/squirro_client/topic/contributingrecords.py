import json


class ContributingRecordsMixin(object):
    def delete_contributing_content_record(
        self, type, type_id, name, record_id, created_at=None
    ):
        """Deletes a contributing content record and recalculates the
        fingerprint for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param record_id: Contributing record identifier.
        :param created_at: Contributing record creation timestamp.

        Example::

            >>> client.delete_contributing_content_record(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default',
            ...     'M2uyX6aUQVG2J2zcblSFHg')
            {}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s/fingerprint"
            "/%(type)s/%(type_id)s/%(name)s/content/%(record_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
            "record_id": record_id,
        }

        params = {}
        if created_at is not None:
            params["created_at"] = created_at

        res = self._perform_request("delete", url, params=params)
        return self._process_response(res, [204])

    def update_contributing_content_record(
        self, type, type_id, name, record_id, content, created_at=None
    ):
        """Updates a contributing content record and recalculates the
        fingerprint for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param record_id: Contributing record identifier.
        :param content: Content data which is a dictionary which contains the
            `lang` and `text` keys.
        :param created_at: Contributing record creation timestamp.

        Example::

            >>> data = {'lang': 'en', 'text': 'updated english content'}
            >>> client.update_fingerprint_from_content(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default',
            ...     'M2uyX6aUQVG2J2zcblSFHg', data,
            ...     created_at='2013-07-01T14:08:23')
            {}
         """
        url = (
            "%(ep)s/%(version)s/%(tenant)s/fingerprint/"
            "%(type)s/%(type_id)s/%(name)s/content/%(record_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
            "record_id": record_id,
        }

        headers = {"Content-Type": "application/json"}

        params = {}
        if created_at is not None:
            params["created_at"] = created_at

        res = self._perform_request(
            "put", url, params=params, data=json.dumps(content), headers=headers
        )
        return self._process_response(res, [204])

    def delete_contributing_items_record(
        self, type, type_id, name, record_id, created_at=None
    ):
        """Deletes a contributing items record and recalculates the
        fingerprint for the provided parameters.

        :param type: Fingerprint type.
        :param type_id: Fingerprint type identifier.
        :param name: Fingerprint name.
        :param record_id: Contributing record identifier.
        :param created_at: Contributing record creation timestamp.

        Example::

            >>> client.delete_contributing_items_record(
            ...     'user', 'bgFtu5rkR1STpx1xR2u1UQ', 'default',
            ...     '0L5jwLdfTJWRcTFMtBzhGg')
            {}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/fingerprint/%(type)s/%(type_id)s/%(name)s/"
            "items/%(record_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "type": type,
            "type_id": type_id,
            "name": name,
            "record_id": record_id,
        }

        params = {}
        if created_at is not None:
            params["created_at"] = created_at

        res = self._perform_request("delete", url, params=params)
        return self._process_response(res, [204])
