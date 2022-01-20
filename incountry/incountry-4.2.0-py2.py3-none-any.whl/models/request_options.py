from typing import Dict

from pydantic import BaseModel, Extra, constr, validator

NonEmptyStr = constr(strict=True, min_length=1)

SERVICE_HEADERS = ["authorization", "x-env-id", "user-agent", "content-type"]


class RequestOptionsModel(BaseModel):
    http_headers: Dict[NonEmptyStr, NonEmptyStr] = {}

    class Config:
        extra = Extra.forbid

    @validator("http_headers")
    def forbid_service_headers_override(cls, value):
        for custom_header in value.keys():
            if custom_header[0] == " " or custom_header[-1] == " ":
                raise ValueError(f"http header may not have leading or traling whitespace: got '{custom_header}'")
            if value[custom_header][0] == " " or value[custom_header][-1] == " ":
                raise ValueError(
                    f"http header value may not have leading or traling whitespace: got '{value[custom_header]}'"
                )
            if custom_header.lower() in SERVICE_HEADERS:
                raise ValueError(f"must not override service http header: got '{custom_header}'")
        return value


class RequestOptions(BaseModel):
    request_options: RequestOptionsModel = {}
