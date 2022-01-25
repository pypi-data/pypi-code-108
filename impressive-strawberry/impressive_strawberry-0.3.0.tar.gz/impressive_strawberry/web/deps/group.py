from uuid import UUID

import fastapi

from impressive_strawberry.database import tables, engine
from impressive_strawberry.web import crud
from impressive_strawberry.web.deps.application import dep_application_this
from impressive_strawberry.web.deps.database import dep_dbsession

__all__ = (
    "dep_group_thisapp",
)


def dep_group_thisapp(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        application: tables.Application = fastapi.Depends(dep_application_this),
        group: str = fastapi.Query(...)
) -> tables.Group:
    """
    Dependency which parses the ``group`` query parameter into a :class:`.tables.Group`, trying to parse it as a UUID first, then falling back to using it as the crystal.

    It is limited to the groups accessible to the application the request is being performed as.
    """
    try:
        uuid = UUID(group)
    except ValueError:
        return crud.quick_retrieve(session, tables.Group, application=application, crystal=group)
    else:
        return crud.quick_retrieve(session, tables.Group, application=application, id=uuid)
