from uuid import UUID

import fastapi

from impressive_strawberry.database import tables, engine
from impressive_strawberry.web import crud
from impressive_strawberry.web.deps.database import dep_dbsession
from impressive_strawberry.web.deps.group import dep_group_thisapp

__all__ = (
    "dep_achievement_thisapp",
    "dep_achievement_token"
)


def dep_achievement_thisapp(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        group: tables.Group = fastapi.Depends(dep_group_thisapp),
        achievement: str = fastapi.Query(...)
) -> tables.Achievement:
    """
    Dependency which parses the ``achievement`` query parameter into an :class:`.tables.Achievement`, trying to parse it as a UUID first, then falling back to using it as the crystal.

    It is limited to the achievements belonging to the group being used in the request.
    """
    try:
        uuid = UUID(achievement)
    except ValueError:
        return crud.quick_retrieve(session, tables.Achievement, group=group, crystal=achievement)
    else:
        return crud.quick_retrieve(session, tables.Achievement, group=group, id=uuid)


def dep_achievement_token(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        token: str = fastapi.Query(...),
) -> tables.Achievement:
    """
    Dependency which parses the ``token`` query parameter into an :class:`.tables.Achievement` by filtering on the value of the token.
    """
    return crud.quick_retrieve(session, tables.Achievement, token=token)
