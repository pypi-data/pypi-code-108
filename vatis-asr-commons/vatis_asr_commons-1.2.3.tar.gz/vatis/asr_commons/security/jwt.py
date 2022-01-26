from enum import Enum


class Claim(Enum):
    LANGUAGE: str = 'language'
    MODEL: str = 'model_uid'
    SERVICE: str = 'service'
