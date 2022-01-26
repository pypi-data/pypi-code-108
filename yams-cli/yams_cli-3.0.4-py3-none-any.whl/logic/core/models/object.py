class GetObjectResult:
    def __init__(self, content, metadata):
        self._content = content
        self._metadata = metadata

    @property
    def content(self):
        return self._content

    @property
    def metadata(self):
        return self._metadata


class ObjectMetadata:
    def __init__(self, md5, content_type, content_length, etag, last_modified):
        self._md5 = md5
        self._content_type = content_type
        self._content_length = content_length
        self._etag = etag
        self._last_modified = last_modified

    @property
    def md5(self):
        return self._md5

    @property
    def content_type(self):
        return self._content_type

    @property
    def content_length(self):
        return self._content_length

    def last_modified(self):
        return self._last_modified

    def etag(self):
        return self._etag

    def __str__(self):
        return "Md5: {}\nContent-Type: {}\nSize: {}\nETag: {}\nlast-Modified: {}\n".format(self._md5,
                                                                                           self._content_type,
                                                                                           self._content_length,
                                                                                           self._etag,
                                                                                           self._last_modified)

    def __repr__(self):
        return self.__str__()


class PutObjectResult:
    def __init__(self, tenant_id, domain_id, bucket_id, object_id):
        self._tenant_id = tenant_id
        self._domain_id = domain_id
        self._bucket_id = bucket_id
        self._object_id = object_id

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def domain_id(self):
        return self._domain_id

    @property
    def bucket_id(self):
        return self._bucket_id

    @property
    def object_id(self):
        return self._object_id
