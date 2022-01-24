#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Triggers module notification entities module
"""

# Python base dependencies
import uuid
from abc import abstractmethod
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_metadata.triggers_module import NotificationType
from sqlalchemy import BINARY, BOOLEAN, VARCHAR, Column, ForeignKey
from sqlalchemy.orm import relationship

# Library libs
import fastybird_triggers_module.entities  # pylint: disable=unused-import
from fastybird_triggers_module.entities.base import (
    Base,
    EntityCreatedMixin,
    EntityUpdatedMixin,
)
from fastybird_triggers_module.exceptions import InvalidStateException


class NotificationEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Notification entity

    @package        FastyBird:TriggersModule!
    @module         entities/notification

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_notifications"

    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_collate": "utf8mb4_general_ci",
        "mysql_charset": "utf8mb4",
        "mysql_comment": "Trigger notifications",
    }

    _type: str = Column(VARCHAR(40), name="notification_type", nullable=False)  # type: ignore[assignment]

    __notification_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="notification_id", default=uuid.uuid4
    )
    __enabled: bool = Column(  # type: ignore[assignment]
        BOOLEAN, name="notification_enabled", nullable=False, default=True
    )

    trigger_id: Optional[bytes] = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16),
        ForeignKey("fb_triggers.trigger_id", ondelete="CASCADE"),
        name="trigger_id",
        nullable=False,
    )

    trigger: "entities.trigger.TriggerEntity" = relationship(  # type: ignore[name-defined]
        "entities.trigger.TriggerEntity",
        back_populates="notifications",
    )

    _email: Optional[str] = Column(VARCHAR(255), name="notification_email", nullable=True)  # type: ignore[assignment]
    _phone: Optional[str] = Column(VARCHAR(150), name="notification_phone", nullable=True)  # type: ignore[assignment]

    __mapper_args__ = {
        "polymorphic_identity": "notification",
        "polymorphic_on": _type,
    }

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        trigger: "entities.trigger.TriggerEntity",  # type: ignore[name-defined]
        notification_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__()

        self.__notification_id = notification_id.bytes if notification_id is not None else uuid.uuid4().bytes

        self.trigger = trigger

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> NotificationType:
        """Trigger notification type"""

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Notification unique identifier"""
        return uuid.UUID(bytes=self.__notification_id)

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Notification enabled status"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Notification enabled setter"""
        self.__enabled = enabled

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "type": self.type.value,
                "enabled": self.enabled,
                "trigger": self.trigger.id.__str__(),
                "owner": self.trigger.owner,
            },
        }


class EmailNotificationEntity(NotificationEntity):
    """
    Email notification entity

    @package        FastyBird:TriggersModule!
    @module         entities/notification

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "email"}

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        email: str,
        trigger: "entities.trigger.TriggerEntity",  # type: ignore[name-defined]
        notification_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(trigger, notification_id)

        self._email = email

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> NotificationType:
        """Notification type"""
        return NotificationType.EMAIL

    # -----------------------------------------------------------------------------

    @property
    def email(self) -> str:
        """Notification email"""
        if self._email is None:
            raise InvalidStateException("Email is missing on notification instance")

        return self._email

    # -----------------------------------------------------------------------------

    @email.setter
    def email(self, email: str) -> None:
        """Notification email setter"""
        self._email = email

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "email": self.email,
            },
        }


class SmsNotificationEntity(NotificationEntity):
    """
    SMS notification entity

    @package        FastyBird:TriggersModule!
    @module         entities/notification

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "sms"}

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        phone: str,
        trigger: "entities.trigger.TriggerEntity",  # type: ignore[name-defined]
        notification_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(trigger, notification_id)

        self._phone = phone

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> NotificationType:
        """Notification type"""
        return NotificationType.SMS

    # -----------------------------------------------------------------------------

    @property
    def phone(self) -> str:
        """Notification phone"""
        if self._phone is None:
            raise InvalidStateException("Phone is missing on notification instance")

        return self._phone

    # -----------------------------------------------------------------------------

    @phone.setter
    def phone(self, phone: str) -> None:
        """Notification phone setter"""
        self._phone = phone

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "phone": self.phone,
            },
        }
