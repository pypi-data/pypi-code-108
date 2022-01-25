import typing as t

from impressive_strawberry.web.models import read

__all__ = (
    "ApplicationFull",
    "GroupFull",
    "AchievementFull",
    "UnlockFull",
    "UserFull",
)


class ApplicationFull(read.ApplicationRead):
    """
    **Full** model (with expanded relationships) for :class:`.database.tables.Application`.
    """

    groups: t.List[read.GroupRead]
    users: t.List[read.UserRead]

    class Config(read.ApplicationRead.Config):
        schema_extra = {
            "example": {
                **read.ApplicationRead.Config.schema_extra["example"],
                "groups": [
                    read.GroupRead.Config.schema_extra["example"],
                ],
                "users": [
                    read.UserRead.Config.schema_extra["example"],
                ],
            },
        }


class GroupFull(read.GroupRead):
    """
    **Full** model (with expanded relationships) for :class:`.database.tables.Group`.
    """

    application: read.ApplicationRead
    achievements: t.List[read.AchievementRead]

    class Config(read.GroupRead.Config):
        schema_extra = {
            "example": {
                **read.GroupRead.Config.schema_extra["example"],
                "application": read.ApplicationRead.Config.schema_extra["example"],
                "achievements": [
                    read.AchievementRead.Config.schema_extra["example"],
                ],
            },
        }


class WebhookFull(read.WebhookRead):
    """
    **Full** model (with expanded relationships) for :class:`.database.tables.Webhook`.
    """

    group: read.GroupRead

    class Config(read.AchievementRead.Config):
        schema_extra = {
            "example": {
                **read.WebhookRead.Config.schema_extra["example"],
                "group": read.GroupRead.Config.schema_extra["example"],
            },
        }


class AchievementFull(read.AchievementRead):
    """
    **Full** model (with expanded relationships) for :class:`.database.tables.Achievement`.
    """

    group: read.GroupRead
    unlocks: t.List[read.UnlockRead]

    class Config(read.AchievementRead.Config):
        schema_extra = {
            "example": {
                **read.AchievementRead.Config.schema_extra["example"],
                "group": read.GroupRead.Config.schema_extra["example"],
                "unlocks": [
                    read.UnlockRead.Config.schema_extra["example"],
                ],
            },
        }


class UnlockFull(read.UnlockRead):
    """
    **Full** model (with expanded relationships) for :class:`.database.tables.Unlock`.
    """

    achievement: read.AchievementRead
    user: read.UserRead

    class Config(read.UnlockRead.Config):
        schema_extra = {
            "example": {
                **read.UnlockRead.Config.schema_extra["example"],
                "achievement": read.AchievementRead.Config.schema_extra["example"],
                "user": read.UserRead.Config.schema_extra["example"],
            },
        }


class UserFull(read.UserRead):
    """
    **Full** model (with expanded relationships) for :class:`.database.tables.User`.
    """

    application: read.ApplicationRead
    unlocks: t.List[read.UnlockRead]

    class Config(read.UserRead.Config):
        schema_extra = {
            "example": {
                **read.UserRead.Config.schema_extra["example"],
                "application": read.ApplicationRead.Config.schema_extra["example"],
                "unlocks": [
                    read.UnlockRead.Config.schema_extra["example"],
                ],
            },
        }
