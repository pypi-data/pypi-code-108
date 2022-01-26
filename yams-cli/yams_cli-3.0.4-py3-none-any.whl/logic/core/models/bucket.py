
class CreateBucketResult:
    def __init__(self, tenant_id, domain_id, bucket_id, alias):
        self._tenant_id = tenant_id
        self._domain_id = domain_id
        self._bucket_id = bucket_id
        self._alias = alias

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
    def alias(self):
        return self._alias

    def __str__(self):
        return "tenant_id: {}, domain_id: {}, bucket_id: {}, alias: {}".format(self.tenant_id, self.domain_id, self.bucket_id, self.alias)

    def __repr__(self):
        return self.__str__()
