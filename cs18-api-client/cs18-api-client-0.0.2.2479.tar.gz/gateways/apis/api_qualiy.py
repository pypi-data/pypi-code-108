from gateways.apis.api_base_class import ApiBase


class ApiQualiY(ApiBase):
    def __init__(self, api_address: str, space_name: str, version: str = None):
        super().__init__(api_address, version)
        self._space = space_name

    def connect(self, sandbox_id: str, instance_id: str, protocol: str):
        return self.build_route("spaces/{SPACE}/connect/{PROTOCOL}?iid={IID}&sandboxId={SANDBOX_ID}".format(
            SPACE=self._space,
            PROTOCOL=protocol,
            IID=instance_id,
            SANDBOX_ID=sandbox_id))
