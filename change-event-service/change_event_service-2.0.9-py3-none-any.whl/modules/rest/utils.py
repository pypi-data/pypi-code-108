from dataclasses import dataclass, field
from typing import Union


@dataclass
class PaginationObject:
    page: int
    total: int
    total_pages: int


@dataclass
class ResponseObject:
    statusCode: Union[int, str]
    data: dict = field(default_factory=dict)
    message: str = None
    exceptionDetails: str = None
    page: PaginationObject = None

    def __post_init__(self):
        if self.statusCode == 200:
            self.statusCode = 'OK-200'
        elif self.statusCode == 201:
            self.statusCode = 'CREATED-201'
        elif self.statusCode >= 400:
            self.statusCode = f'EX-{self.statusCode}'
