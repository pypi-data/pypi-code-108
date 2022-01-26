from typing import Optional


class CoiledException(Exception):
    """Custom exception to be used as a base exception.

    This exception needs to include a `code` argument which is
    a constant variable that will give us more information as to
    where the exception happened.

    """

    code = "COILED_EXCEPTION"

    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message = message
        self.extras = kwargs

    def __repr__(self) -> str:
        return f"CoiledException({self.code}: {self.message})"

    def as_json(self) -> dict:
        return {"code": self.code, "message": self.message, **self.extras}


class UnsupportedBackendError(CoiledException):
    code = "UNSUPPORTED_BACKEND"


class ParameterMissingError(CoiledException):
    code = "PARAMETER_MISSING_ERROR"


class GCPCredentialsParameterError(ParameterMissingError):
    code = "GCP_PARAMETER_MISSING_ERROR"


class GCPCredentialsError(CoiledException):
    code = "CREDENTIALS_ERROR"


class AWSCredentialsParameterError(ParameterMissingError):
    code = "AWS_PARAMETER_MISSING_ERROR"


class RegistryParameterError(ParameterMissingError):
    code = "REGISTRY_PARAMETER_ERROR"


class AccountConflictError(CoiledException):
    code = "ACCOUNT_CONFLICT_ERROR"

    def __init__(
        self,
        unparsed_name: str,
        account_from_name: str,
        account: str,
        message: Optional[str] = None,
        **kwargs,
    ):
        self.unparsed_name = unparsed_name
        self.account_from_name = account_from_name
        self.account = account
        if not message:
            message = (
                "Two accounts were specified where only "
                f'one is valid. The value "{unparsed_name}" '
                f'contains the account prefix "{account_from_name}," '
                f'and the account "{account}" was also passed.'
            )
        super().__init__(message, **kwargs)


class InstanceTypeError(CoiledException):
    code = "INSTANCE_TYPE_ERROR"


class GPUTypeError(CoiledException):
    code = "GPU_TYPE_ERROR"


class ArgumentCombinationError(CoiledException):
    code = "ARGUMENT_COMBINATION_ERROR"


class CidrInvalidError(CoiledException):
    code = "CIDR_INVALID_ERROR"


class PortValidationError(CoiledException):
    code = "PORT_VALIDATION_ERROR"


class AccountFormatError(CoiledException):
    code = "ACCOUNT_FORMAT_ERROR"


class ApiResponseStatusError(CoiledException):
    code = "API_RESPONSE_STATUS_ERROR"
