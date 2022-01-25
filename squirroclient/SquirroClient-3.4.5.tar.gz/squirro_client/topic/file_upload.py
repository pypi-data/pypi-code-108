import os

from squirro_client.exceptions import NotFoundError, UnknownError


class FileUploadMixin(object):
    def new_storage_file_from_name(self, bucket, filename):
        """Stores the `file` identified by filename to the container

        :param filename: filename to be stored
        :param bucket: bucket name
        """

        if not os.path.exists(filename):
            raise ValueError("Can not find file {}".format(filename))

        data = open(filename, "rb").read()
        return self.new_storage_file(bucket=bucket, data=data)

    def new_storage_file(self, bucket, data, filename=None):
        """Stores the `file` to the container

        :param data: data to be stored
        """

        url = "%(ep)s/v0/%(tenant)s/%(bucket)s/file_upload" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "bucket": bucket,
        }
        headers = {}
        res = self._perform_request(
            "post",
            url,
            files={"bucket": bucket, "file": data},
            params={"filename": filename},
            headers=headers,
        )
        return self._process_response(res, [201])

    def get_storage_file(self, storage_url):
        """Returns the content file with the url `storage_url`
        from the container.

        :param storage_url: File name
        """

        url = "%(ep)s/v0/%(tenant)s/file" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
        }
        res = self._perform_request("get", url, params={"storage_url": storage_url})
        if res.status_code == 404:
            raise NotFoundError(res.status_code, "Not found")
        elif res.status_code != 200:
            raise UnknownError(res.status_code, "")
        else:
            return res.content

    def delete_storage_file(self, storage_url):
        """Deletes the file with the url `storage_url`
        from the container.

        :param storage_url: File name
        """

        url = "%(ep)s/v0/%(tenant)s/file" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
        }
        res = self._perform_request("delete", url, params={"storage_url": storage_url})
        return self._process_response(res, [204])
