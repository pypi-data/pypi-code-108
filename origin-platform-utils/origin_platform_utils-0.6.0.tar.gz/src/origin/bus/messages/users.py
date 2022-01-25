from dataclasses import dataclass

from origin.bus import Message


@dataclass
class UserOnboarded(Message):
    """
    A new user has been onboarded to the system.
    """
    subject: str
