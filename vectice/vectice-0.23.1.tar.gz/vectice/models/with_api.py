import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar


class WithAPITrait(ABC):
    T = TypeVar("T", bound="WithAPITrait")

    @abstractmethod
    def with_create(self: T) -> T:
        """

        :param key:
        :param value:
        :return: iself
        """
        pass


@dataclass
class WithAPI(WithAPITrait):

    T = TypeVar("T", bound="WithAPI")

    def with_create(self: T) -> T:
        from vectice.api import Client  # import here to avoid circular import
        import time

        payload = self.__dict__
        payload["name"] = payload.pop("parentName")
        dataset_id = Client(os.environ["PROJECT_TOKEN"]).create_dataset(payload)
        time.sleep(1)

        Client(os.environ["PROJECT_TOKEN"]).create_dataset_version(dataset_id["id"], self)  # type: ignore
        return self


class WithDelegatedAPI(WithAPITrait, ABC):
    T = TypeVar("T", bound="WithDelegatedAPI")

    @abstractmethod
    def _get_delegate(self) -> WithAPITrait:
        pass

    def with_create(self: T) -> T:
        self._get_delegate().with_create()
        return self
