from pydantic import BaseModel, conint

DEFAULT_HTTP_TIMEOUT_SECONDS = 30
BASE_DELAY_DEFAULT = 1
MAX_DELAY_DEFAULT = 32


class HttpOptions(BaseModel):
    timeout: conint(strict=True, gt=0) = DEFAULT_HTTP_TIMEOUT_SECONDS
    retry_base_delay: conint(strict=True, gt=0) = BASE_DELAY_DEFAULT
    retry_max_delay: conint(strict=True, gt=0) = MAX_DELAY_DEFAULT
