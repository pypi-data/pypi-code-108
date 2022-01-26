from pathlib import Path
import os
IMAGES_DIR = Path(__file__).parent.absolute()


class StoredImage:

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.name = self.path.stem
        self.image_format = self.path.suffix.removeprefix('.')
        self._bytes: bytes = None

    @property
    def bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = self.path.read_bytes()
        return self._bytes


_IMAGE_CACHE: dict[str, StoredImage] = {}

PLACEHOLDER_IMAGE = StoredImage(IMAGES_DIR.joinpath("placeholder.png"))


def get_image(name: str) -> StoredImage:
    if name in _IMAGE_CACHE:
        return _IMAGE_CACHE[name]
    for dirname, folderlist, filelist in os.walk(IMAGES_DIR):
        for file in filelist:
            if file.casefold() == name:
                path = Path(dirname, file)
                image = StoredImage(path)
                _IMAGE_CACHE[image.name] = image
                return image
