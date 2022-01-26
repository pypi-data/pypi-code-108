class CreateWatermarkResult:
    def __init__(self, tenant_id, domain_id, watermark_id, alias):
        self._tenant_id = tenant_id
        self._domain_id = domain_id
        self._watermark_id = watermark_id
        self._alias = alias

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def domain_id(self):
        return self._domain_id

    @property
    def watermark_id(self):
        return self._watermark_id

    @property
    def alias(self):
        return self._alias


class GetWatermarkResult:
    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

