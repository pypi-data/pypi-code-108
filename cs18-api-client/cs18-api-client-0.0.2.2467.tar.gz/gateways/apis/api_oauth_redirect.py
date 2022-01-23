from gateways.apis.api_base_class import ApiBase


class ApiOauthRedirect(ApiBase):
    def oauth_redirect(self, account: str):
        return self.build_route("OauthRedirect/{account}".format(**locals()))
