from enum import Enum


class InvalidatedReasonInput(str, Enum):
    BAD_CONTENT = "bad-content"
    DUPLICATE = "duplicate"
    INCORRECTLY_CREATED = "incorrectly-created"
