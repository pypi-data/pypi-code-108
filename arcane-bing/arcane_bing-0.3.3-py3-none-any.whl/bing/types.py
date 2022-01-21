from typing import Union, List
from dataclasses import dataclass


@dataclass
class BingErrorDetail:
    code: Union[int, None] = None
    details: Union[str, None] = None
    error_code: Union[str, None] = None
    message: Union[str, None] = None


@dataclass
class BingError:
    tracking_id: str
    errors: List[BingErrorDetail]
