from gateways.apis.api_base_class import ApiBase


class ApiToken(ApiBase):
    def refresh(self, refresh_token: str):
        return self.build_route("token/refresh".format(**locals()))

    def long_token(self):
        return self.build_route("token/longtoken")

    def revoke(self):
        return self.build_route("token/revoke")

    def revoke_long_token(self):
        return self.build_route("token/revokelongtoken")
