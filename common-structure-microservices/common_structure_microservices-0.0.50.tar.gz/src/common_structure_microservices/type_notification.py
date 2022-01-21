from enum import Enum


class TypeNotification(Enum):
    COMMUNITY = "community"
    REQUEST_COMMUNITY = "request-community"
    INVITATION_COMMUNITY = "invitation"
    PUBLICATION = "publication"
    FULL_TEXT = "full_text"
    USER = "user"
    CHAT = "chat"
