from impressive_strawberry.web.models import base

__all__ = (
    "StrawberryErrorModel",
)


class StrawberryErrorModel(base.StrawberryModel):
    """
    Model for errors returned by the API.
    """

    error_code: str
    reason: str

    class Config(base.StrawberryModel.Config):
        schema_extra = {
            "example": {
                "error_code": "NOT_FOUND",
                "reason": "The requested object was not found.",
            },
        }
