from uuid import UUID

import fastapi

from impressive_strawberry.database import tables, engine
from impressive_strawberry.web import crud
from impressive_strawberry.web.deps.achievement import dep_achievement_token
from impressive_strawberry.web.deps.application import dep_application_this
from impressive_strawberry.web.deps.database import dep_dbsession

__all__ = (
    "dep_user_thisapp",
    "dep_user_token",
)


def dep_user_thisapp(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        application: tables.Application = fastapi.Depends(dep_application_this),
        user: str = fastapi.Query(...),
) -> tables.User:
    """
    Dependency which parses the ``user`` query parameter into a :class:`.tables.User`, trying to parse it as a UUID first, then falling back to using it as the crystal.

    It is limited to the users accessible to the application the request is being performed as.
    """
    try:
        uuid = UUID(user)
    except ValueError:
        return crud.quick_retrieve(session, tables.User, application=application, crystal=user)
    else:
        return crud.quick_retrieve(session, tables.User, application=application, id=uuid)


def dep_user_token(
        session: engine.Session = fastapi.Depends(dep_dbsession),
        achievement: tables.Achievement = fastapi.Depends(dep_achievement_token),
        user: str = fastapi.Query(...),
) -> tables.User:
    """
    Dependency which parses the ``user`` query parameter into a :class:`.tables.User`, trying to parse it as a UUID first, then falling back to using it as the crystal.

    It is limited to the users accessible to the application related to the achievement being processed by the current request.
    """
    try:
        uuid = UUID(user)
    except ValueError:
        return crud.quick_retrieve(session, tables.User, application=achievement.group.application, crystal=user)
    else:
        return crud.quick_retrieve(session, tables.User, application=achievement.group.application, id=uuid)
