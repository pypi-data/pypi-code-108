from slai.types import ModelTypes
from slai.base_handler import BaseModelHandler
from slai.login import Login
from slai.model import Model

__version__ = "0.1.59"


# most used slai actions go here
model = Model
types = ModelTypes
login = Login
BaseModelHandler = BaseModelHandler

__all__ = [
    "__version__",
    "model",
    "types",
    "base_handler",
    "login",
]
