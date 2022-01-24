from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List, Any, BinaryIO, TypeVar
from abc import ABC, abstractmethod


class WithAttachmentsTrait(ABC):
    T = TypeVar("T", bound="WithAttachmentsTrait")

    @abstractmethod
    def with_attachments(self, files: List[str]):
        """Accepts a list of file paths and then attaches the files to the modelversion that is created.
        e.g ["filepath/image.png", r"User/path/metrics.json"]

        :param files: The list of files
        :return: ModelVersionArtifact
        """
        pass


@dataclass
class WithAttachments(WithAttachmentsTrait):
    artifact_type: Optional[str] = None
    """"""
    files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    """"""

    def with_attachments(self, files: List[str]):
        self.files = [("file", (file, open(file, "rb"))) for file in files]
        return self


class WithDelegatedAttachments(WithAttachmentsTrait, ABC):
    T = TypeVar("T", bound="WithDelegatedAttachments")

    @abstractmethod
    def _get_attachment(self) -> WithAttachmentsTrait:
        pass

    def with_attachments(self: T, files: List[str]) -> T:
        self._get_attachment().with_attachments(files)
        return self
