from typing import Callable

from pydantic import BaseModel


class SecretKeyAccessorModel(BaseModel):
    accessor_function: Callable
