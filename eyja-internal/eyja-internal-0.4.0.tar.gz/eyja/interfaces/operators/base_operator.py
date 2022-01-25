from typing import Type

from eyja.interfaces.db import BaseStorageModel


class BaseModelOperator:
    model = Type[BaseStorageModel]
