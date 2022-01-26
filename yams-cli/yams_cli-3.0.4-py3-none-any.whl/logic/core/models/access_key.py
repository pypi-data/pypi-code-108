class CreateAccessKeyResult:
    def __init__(self, tenant_id, access_key_id, private_key):
        self._tenant_id = tenant_id
        self._access_key_id = access_key_id
        self._private_key = private_key

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def access_key_id(self):
        return self._access_key_id

    @property
    def private_key(self):
        return self._private_key
