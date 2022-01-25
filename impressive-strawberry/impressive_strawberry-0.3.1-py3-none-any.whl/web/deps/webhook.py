from uuid import UUID

import fastapi

from impressive_strawberry.database import tables, engine
from impressive_strawberry.web import crud
from impressive_strawberry.web.deps.database import dep_dbsession
from impressive_strawberry.web.deps.group import dep_group_thisapp

__all__ = (
    "dep_webhook_thisapp",
)


def dep_webhook_thisapp(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        group: tables.Group = fastapi.Depends(dep_group_thisapp),
        webhook: str = fastapi.Query(...)
) -> tables.Achievement:
    """
    Dependency which parses the ``achievement`` query parameter into an :class:`.tables.Achievement`, trying to parse it as a UUID first, then falling back to using it as the crystal.

    It is limited to the achievements belonging to the group being used in the request.
    """
    try:
        uuid = UUID(webhook)
    except ValueError:
        return crud.quick_retrieve(session, tables.Webhook, group=group, crystal=webhook)
    else:
        return crud.quick_retrieve(session, tables.Webhook, group=group, id=uuid)
