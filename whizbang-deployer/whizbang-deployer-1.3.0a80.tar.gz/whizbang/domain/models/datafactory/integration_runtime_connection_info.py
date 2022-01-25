from pydantic import SecretStr

from whizbang.domain.models.pydantic_model_base import PydanticModelBase


class IntegrationRuntimeConnectionInfo(PydanticModelBase):
    host_service_uri: str
    identity_cert_thumbprint: str
    is_grpc_used: bool
    is_identity_cert_exprired: bool # This field is misspelled by Azure in the return dictionary
    public_key: str
    service_token: SecretStr
    version: str
