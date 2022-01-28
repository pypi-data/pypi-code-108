import logging
from abc import ABC, abstractmethod
from typing import List

from dataclasses import dataclass, field

log = logging.getLogger(__name__)


class LoginError(Exception):
    pass


class Credentials(ABC):
    """
    Abstract class for credential managers
    """

    @abstractmethod
    def get_credentials(self, resource_id, resource_type="dataset", mode="r"):
        pass


@dataclass
class CredentialsChain(Credentials):
    """
    Credentials chain grouping a number of credentials into one trying all of them in order
    """
    chain: List[Credentials] = field(default_factory=list)

    def get_credentials(self, resource_id, resource_type="dataset", mode="r"):
        if not self.chain:
            raise LoginError("Credentials chain empty")

        exceptions = []
        for credentials in self.chain:
            try:
                return credentials.get_credentials(resource_id, resource_type, mode)
            except LoginError as ex:
                exceptions.append(ex)
        raise LoginError(f"Error logging in with credentials chain", exceptions)
