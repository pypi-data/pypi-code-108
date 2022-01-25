"""
This module contains the database tables of :mod:`impressive_strawberry`.
"""

import datetime
import enum
import secrets
import uuid

import sqlalchemy.orm
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, Enum, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

__all__ = (
    "Base",
    "Alloy",
    "WebhookKind",
    "Application",
    "Group",
    "Webhook",
    "Achievement",
    "Unlock",
    "User",
)

Base = sqlalchemy.orm.declarative_base()


class Alloy(str, enum.Enum):
    """
    An alloy represents the rarity of an :class:`.Achievement`.
    """

    BRONZE = "BRONZE"
    "A common :class:`.Achievement`."

    SILVER = "SILVER"
    "An uncommon :class:`.Achievement`."

    GOLD = "GOLD"
    "A rare :class:`.Achievement`."


class WebhookKind(str, enum.Enum):
    """
    The type of the output format of webhooks.
    """

    STRAWBERRY = "STRAWBERRY"
    "Strawberry will output data using its own JSON model."

    DISCORD = "DISCORD"
    "Strawberry will output data which can be fed directly into a Discord webhook."


class Application(Base):
    """
    An :class:`.Application` represents an entity interacting with :mod:`impressive_strawberry`, such as a website or a bot.
    """

    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="")
    token = Column(String, nullable=False, default=secrets.token_urlsafe)

    groups = relationship("Group", back_populates="application", cascade="all, delete-orphan")
    users = relationship("User", back_populates="application", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Application id={self.id}>"


class Group(Base):
    """
    A :class:`.Group` represents a grouping of :class:`.Achievement`\\ s in an :class:`.Application`.

    If, for example, the application is a Discord Bot, the :class:`.Group` represents the Discord Guild / Server.
    """

    __tablename__ = "groups"
    __table_args__ = (
        # To avoid an application having the same server over and over, uniqueness between the crystal and the application_id is needed
        UniqueConstraint('application_id', 'crystal'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)

    crystal = Column(String, nullable=False)
    """
    :class:`Application`\\ s can identify :class:`.Group`\\ s through a custom identifier, the :attr:`.crystal`, which is specified on creation.
    """

    application = relationship("Application", back_populates="groups")
    achievements = relationship("Achievement", back_populates="group", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group id={self.id} crystal={self.crystal}>"


class Webhook(Base):
    """
    A :class:`.Webhook` represents an URL to which updates relative to a certain :class:`.Group` should be sent, using the format specified by the :class:`.WebhookType`.
    """

    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    url = Column(String, nullable=False)
    kind = Column(Enum(WebhookKind), nullable=False)

    group = relationship("Group", back_populates="webhooks")


class Achievement(Base):
    """
    An :class:`.Achievement` represents an award that can be bestowed by an :class:`.Application` to an :class:`.User`.

    All :class:`.Achievement`\\ s belong to a :class:`.Group`.
    """

    __tablename__ = "achievements"
    __table_args__ = (
        # To avoid an application having the same server over and over, uniqueness between the crystal and the application_id is needed
        UniqueConstraint('group_id', 'crystal'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, default="")
    alloy = Column(Enum(Alloy), nullable=False)
    secret = Column(Boolean, nullable=False, default=False)
    icon = Column(String)
    repeatable = Column(Boolean, nullable=False, default=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)

    crystal = Column(String, nullable=False)
    """
    :class:`Group`\\ s can identify :class:`.Achievements`\\ s through a custom identifier, the :attr:`.crystal`, which is specified on creation.
    """

    token = Column(String, nullable=False, default=secrets.token_urlsafe)
    """
    Token used to unlock an achievement for an user without knowing the application token.
    """

    group = relationship("Group", back_populates="achievements")
    unlocks = relationship("Unlock", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement id={self.id} crystal={self.crystal}>"


class Unlock(Base):
    """
    An :class:`.Unlock` represents the bestowing of an :class:`.Achievement` to an :class:`.User`.

    If the achievement is :attr:`~.Achievement.repeatable`, multiple :class:`.Unlock`\\ s for it can exist.
    """

    __tablename__ = "unlocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.now)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    achievement = relationship("Achievement", back_populates="unlocks")
    user = relationship("User", back_populates="unlocks")

    def __repr__(self):
        return f"<Unlock id={self.id}>"


class User(Base):
    """
    An :class:`.User` is the representation of a person in an :class:`.Application`.

    If, for example, the application is a Discord Bot, the :class:`.User` represents the corresponding Discord User.
    """

    __tablename__ = "users"
    __table_args__ = (
        # To avoid an user registered to the same server over and over, uniqueness between the crystal
        # and the application_id is needed
        UniqueConstraint('application_id', 'crystal'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)

    crystal = Column(String, nullable=False)
    """
    :class:`Application`\\ s can identify :class:`.Group`\\ s through a custom identifier, the :attr:`.crystal`, which is specified on creation.
    """

    application = relationship("Application", back_populates="users")
    unlocks = relationship("Unlock", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id}>"
