class CreatePolicyResult:
    def __init__(self, tenant_id, policy_id):
        self._tenant_id = tenant_id
        self._policy_id = policy_id

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def policy_id(self):
        return self._policy_id
