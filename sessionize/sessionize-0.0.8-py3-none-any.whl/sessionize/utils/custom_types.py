from typing import Any, Union

from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine, Connection


Record = dict[str, Any]
SqlConnection = Union[Engine, Session, Connection]