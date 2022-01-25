from datetime import datetime
from uuid import UUID

from impressive_strawberry.web.models import edit

__all__ = (
    "ApplicationRead",
    "GroupRead",
    "WebhookRead",
    "AchievementRead",
    "UnlockRead",
    "UserRead",
)


class ApplicationRead(edit.ApplicationEdit):
    """
    **Read** model for :class:`.database.tables.Application`.
    """

    id: UUID
    token: str

    class Config(edit.ApplicationEdit.Config):
        schema_extra = {
            "example": {
                **edit.ApplicationEdit.Config.schema_extra["example"],
                "id": "971851d4-b41f-46e1-a884-5b5e84a276f8",
                "token": "tLsk16aJojijZkuLQqJ-pVHnnBPVAl-G0HYavFkfmk4",
            },
        }


class GroupRead(edit.GroupEdit):
    """
    **Read** model for :class:`.database.tables.Group`.
    """

    id: UUID
    application_id: UUID

    class Config(edit.GroupEdit.Config):
        schema_extra = {
            "example": {
                **edit.GroupEdit.Config.schema_extra["example"],
                "id": "70fd1bf3-69dd-4cde-9d41-42368221849f",
                "application_id": "971851d4-b41f-46e1-a884-5b5e84a276f8",
            },
        }


class WebhookRead(edit.WebhookEdit):
    """
    **Read** model for :class:`.database.tables.Webhook`.
    """

    id: UUID
    group_id: UUID

    class Config(edit.GroupEdit.Config):
        schema_extra = {
            "example": {
                **edit.WebhookEdit.Config.schema_extra["example"],
                "id": "70fd1bf3-69dd-4cde-9d41-42368221849f",
                "group_id": "70fd1bf3-69dd-4cde-9d41-42368221849f",
            },
        }


class AchievementRead(edit.AchievementEdit):
    """
    **Read** model for :class:`.database.tables.Achievement`.
    """

    id: UUID
    group_id: UUID
    token: str

    class Config(edit.AchievementEdit.Config):
        schema_extra = {
            "example": {
                **edit.AchievementEdit.Config.schema_extra["example"],
                "id": "a0da6178-d1d3-48ef-984c-7bb8a75c6d3b",
                "group_id": "70fd1bf3-69dd-4cde-9d41-42368221849f",
                "token": "tLsk16aJojijZkuLQqJ-pVHnnBPVAl-G0HYavFkfmk4",
            },
        }


class UnlockRead(edit.UnlockEdit):
    """
    **Read** model for :class:`.database.tables.Unlock`.
    """

    id: UUID
    timestamp: datetime

    class Config(edit.UnlockEdit.Config):
        schema_extra = {
            "example": {
                **edit.UnlockEdit.Config.schema_extra["example"],
                "id": "15e5bdfb-1b5d-4de2-acc6-fc45b01a503e",
                "timestamp": 1636600556.251724,
            },
        }


class UserRead(edit.UserEdit):
    """
    **Read** model for :class:`.database.tables.User`.
    """

    id: UUID
    application_id: UUID

    class Config(edit.UserEdit.Config):
        schema_extra = {
            "example": {
                **edit.UserEdit.Config.schema_extra["example"],
                "application_id": "971851d4-b41f-46e1-a884-5b5e84a276f8",
                "id": "ee4855c6-5690-4a88-9999-950b3ae92473",
            },
        }
