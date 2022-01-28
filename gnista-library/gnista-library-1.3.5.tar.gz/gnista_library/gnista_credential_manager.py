import jwt
from oauth2_client.credentials_manager import CredentialManager
from structlog import get_logger

log = get_logger()


class GnistaCredentialManager(CredentialManager):
    def __init__(self, service_information, proxies=None):
        super().__init__(service_information, proxies)
        self.id_token = None
        self.access_token = None
        self.tenant_name = None
        self.company_name = None
        self.refresh_token = None

    def _process_token_response(self, token_response, refresh_token_mandatory):
        log.info("Token has been received.")

        access_token = token_response.get("access_token")

        id_token = token_response.get("id_token")
        if id_token is not None:
            decoded = jwt.decode(
                id_token, options={"verify_signature": False, "verify_aud": False}, algorithms=["HS256", "RS256"]
            )
            self.id_token = id_token
            self.tenant_name = decoded["tenant_name"]
            self.company_name = decoded["company_name"]

        super()._process_token_response(token_response, refresh_token_mandatory)
        self.access_token = access_token
        self.refresh_token = token_response.get("refresh_token")
        log.info("Successfully logged in", company=self.company_name, tenant_name=self.tenant_name)
