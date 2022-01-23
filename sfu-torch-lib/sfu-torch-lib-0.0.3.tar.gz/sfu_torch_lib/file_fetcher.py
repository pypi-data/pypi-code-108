import os
import tarfile
from tarfile import TarFile
from typing import Callable, List, Optional, IO

import sfu_torch_lib.io as io


IsMemberType = Callable[[str], bool]


class FileFetcher:
    members: List[str]

    def __init__(self, path: str, is_member: IsMemberType) -> None:
        self.path = path
        self.is_member = is_member

    def __len__(self) -> int:
        return len(self.members)

    def __getitem__(self, index: int) -> str:
        return self.members[index]

    def open_member(self, key: str) -> IO:
        raise NotImplementedError()


class TarFileFetcher(FileFetcher):
    def __init__(
            self, path: str,
            is_member: IsMemberType,
            ephemeral_path: Optional[str] = os.environ.get('DATA_EPHEMERAL_PATH'),
    ) -> None:

        super().__init__(path, is_member)

        self.ephemeral_path = ephemeral_path

        self.members = self.get_members(path, is_member)
        self.container: Optional[TarFile] = None

    @staticmethod
    def get_members(path: str, is_member: Callable[[str], bool]) -> List[str]:
        return [name for name in tarfile.open(path).getnames() if is_member(name)]

    def open_member(self, key: str) -> IO:
        if self.container is None:
            self.container = tarfile.open(self.path)

        prefix = io.generate_path(prefix=self.ephemeral_path)
        path = os.path.join(prefix, key)

        if not io.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.container.extract(key, prefix)

        file_object = io.open(path)

        return file_object


class FileSystemFileFetcher(FileFetcher):
    def __init__(self, path: str, is_member: IsMemberType) -> None:
        super().__init__(path, is_member)

        self.members = self.get_members(path, is_member)

    @staticmethod
    def get_members(path: str, is_member: Callable[[str], bool]) -> List[str]:
        return [
            name
            for name
            in (os.path.relpath(key, path) for key in io.get_files(path))
            if is_member(name)
        ]

    def open_member(self, key: str) -> IO:
        return io.open(io.generate_path(key, self.path))


def get_file_fetcher(path: str, is_member: IsMemberType = lambda _: True) -> FileFetcher:
    if path.endswith('.tar'):
        return TarFileFetcher(path, is_member)
    else:
        return FileSystemFileFetcher(path, is_member)
