from uuid import UUID

import fastapi

from impressive_strawberry.database import tables, engine
from impressive_strawberry.web import crud
from impressive_strawberry.web.deps.application import dep_application_this
from impressive_strawberry.web.deps.database import dep_dbsession
from impressive_strawberry.web.errors import ResourceNotFound

__all__ = (
    "dep_unlock_thisapp",
)


def dep_unlock_thisapp(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        application: tables.Application = fastapi.Depends(dep_application_this),
        unlock: UUID = fastapi.Query(...),
) -> tables.Unlock:
    """
    Dependency which parses the ``unlock`` query parameter into a :class:`.tables.Unlock`, parsing it as a UUID.

    It is limited to the unlocks accessible to the application the request is being performed as.
    """
    result = crud.quick_retrieve(session, tables.Unlock, id=unlock)
    if result.user.application != application:
        raise ResourceNotFound()
    return result
