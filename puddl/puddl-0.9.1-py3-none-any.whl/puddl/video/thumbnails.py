from __future__ import annotations

import typing as t
from pathlib import Path


class Video:
    def __init__(self, data: bytes, encoding: str):
        self.data = data
        self.encoding = encoding

    @classmethod
    def from_path(cls, path: Path) -> Video:
        raise NotImplementedError


class Thumb:
    def __init__(self, data: bytes):
        self.data = data

    def to_png(self) -> t.IO[bytes]:
        raise NotImplementedError


def make_thumbs(video: Video) -> [Thumb]:
    """
    :param video: video Bytewurst
    """
    raise NotImplementedError


if __name__ == '__main__':
    import sys

    video = Video.from_path(sys.argv[1])
    thumbs = make_thumbs(video)
    for i, thumb in enumerate(thumbs):
        png = thumb.to_png()
        path = Path(f'thumbnail_{i:03}.png')
        path.write_bytes(png)
