from dataclasses import dataclass
import os


@dataclass
class FilePathExt:
    filepath: str

    def __post_init__(self):
        root, ext = os.path.splitext(self.filepath)

        self._path = ''
        self._filename = ''
        self._extension = ext[1:]

    @property
    def path(self):
        return self._path

    @property
    def filename(self):
        return self._filename

    @property
    def extension(self):
        return self._extension


f = r'D:\test\test\0202.mp4'

fpe = FilePathExt(f)

print(fpe.filepath)
print(fpe.extension)

print(os.path.splitext(f)[1][1:])
print(os.path.splitext(f))

