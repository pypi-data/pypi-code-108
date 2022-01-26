class CreateDomainResult:
    def __init__(self, tenant_id, domain_id, alias):
        self._tenant_id = tenant_id
        self._domain_id = domain_id
        self._alias = alias

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def domain_id(self):
        return self._domain_id

    @property
    def alias(self):
        return self._alias

