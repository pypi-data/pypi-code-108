"""Module for user exposed env settings"""


from pydantic import BaseSettings


class Settings(BaseSettings):
    TAKTILE_GIT_SHA: str = "unknown"
    TAKTILE_GIT_REF: str = "unknown"
