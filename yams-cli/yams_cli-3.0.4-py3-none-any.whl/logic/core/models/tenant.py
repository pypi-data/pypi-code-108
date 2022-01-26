
class CreateTenantResult:
    def __init__(self, tenant_id):
        self._tenant_id = tenant_id

    @property
    def tenant_id(self):
        return self._tenant_id
