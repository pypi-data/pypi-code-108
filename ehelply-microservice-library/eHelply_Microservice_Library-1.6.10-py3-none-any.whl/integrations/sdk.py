from ehelply_bootstrapper.utils.state import State
from ehelply_bootstrapper.utils.cryptography import Encryption
from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.drivers.fast_api_utils.responses import *

from ehelply_python_sdk.sdk import SDKConfiguration, eHelplySDK, ErrorResponse, is_response_error
from ehelply_python_sdk.services.service_schemas import GenericHTTPResponse


class SDK(Integration):
    instance: eHelplySDK

    def __init__(self, service_gatekeeper_key: str) -> None:
        super().__init__("sdk")

        self.enc: Encryption = Encryption([service_gatekeeper_key.encode(Encryption.STRING_ENCODING)])

    def init(self):
        try:
            secret_token: str = State.config.m2m.auth.secret_key
            access_token: str = State.config.m2m.auth.access_key

            if len(secret_token) == 0 or len(access_token) == 0:
                State.logger.warning("SDK (M2M) credentials are not set. Check the m2m.yaml config")

            secret_token = self.enc.decrypt_str(secret_token.encode(Encryption.STRING_ENCODING))
            access_token = self.enc.decrypt_str(access_token.encode(Encryption.STRING_ENCODING))

            # Setup SDK
            SDK.instance = SDK.make_sdk(access_token, secret_token)

        except:
            SDK.instance = SDK.make_sdk("", "")
            State.logger.severe(
                "SDK (M2M) credentials are invalid. Ensure they are encrypted. Check the m2m.yaml config")

    @staticmethod
    def make_sdk(access_token: str, secret_token: str) -> eHelplySDK:
        ehelply_sdk: eHelplySDK = eHelplySDK(
            sdk_configuration=SDKConfiguration(
                access_token=access_token,
                secret_token=secret_token,
                project_identifier="ehelply-resources",
                partition_identifier="ehelply-cloud"
            )
        )
        return ehelply_sdk

    @staticmethod
    def make_json_response(response: GenericHTTPResponse) -> JSONResponse:
        if is_response_error(response):
            response: ErrorResponse
            return JSONResponse(status_code=response.status_code, content={"message": response.message})
        content = response.dict()
        content.pop('status_code')
        return JSONResponse(status_code=response.status_code, content=content)
