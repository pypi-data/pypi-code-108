import re

import fastapi
from fastapi.security import APIKeyHeader
from sqlalchemy import sql
from sqlalchemy.orm import Session

from impressive_strawberry.database import tables
from impressive_strawberry.web import errors
from .database import dep_dbsession

__all__ = (
    "dep_application_this",
)

dep_application_token = APIKeyHeader(
    scheme_name="application_token",
    name="Authorization",
    description="The token of the application to authenticate as.",
    auto_error=False,
)


def dep_application_this(
        session: Session = fastapi.Depends(dep_dbsession),
        header: tables.Application = fastapi.Security(dep_application_token),
) -> tables.Application:
    """
    Dependency which parses the ``Authorization`` header with the ``Bearer XXXXX`` format and returns the application having the parsed token.
    """
    if not header:
        raise errors.MissingAuthHeader()

    if match := re.match(r"^Bearer (.+)$", header):
        token = match.group(1)
    else:
        raise errors.InvalidAuthHeader()

    app = session.execute(
        sql.select(tables.Application).where(tables.Application.token == token)
    ).scalar()

    if not app:
        raise errors.WrongAuthHeader()

    return app
