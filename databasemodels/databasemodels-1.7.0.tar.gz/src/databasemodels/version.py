from dataclasses import dataclass
from typing import Optional


__all__ = [
    'Version'
]


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    tag: Optional[str] = None

    def __post_init__(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError(f'Illegal Version Number ({self.major}.{self.minor}.{self.patch})')

        if self.tag == '':
            raise ValueError(f'Illegal Tag Value ({self.tag})')

    def __str__(self) -> str:
        if self.tag is None:
            return f'{self.major}.{self.minor}.{self.patch}'
        return f'{self.major}.{self.minor}.{self.patch}-{self.tag}'
