import os
import re

import fastapi
from fastapi.security import APIKeyHeader

from impressive_strawberry.database import tables
from impressive_strawberry.web import errors

__all__ = (
    "dep_impressive_secret_required",
)

dep_impressive_secret = APIKeyHeader(
    scheme_name="impressive_secret",
    name="Authorization",
    description="The secret required to perform certain actions on Impressive Strawberry.",
    auto_error=False,
)


def dep_impressive_secret_required(
        header: tables.Application = fastapi.Security(dep_impressive_secret),
) -> None:
    """
    Dependency which parses the ``Authorization`` header with the ``Secret XXXXX`` format, raising an error if the secret is invalid or skipping the check completely if the secret is not set.
    """

    if expected_secret := os.environ.get("IS_SECRET"):
        if not header:
            raise errors.MissingAuthHeader()

        if match := re.match(r"^Secret (.+)$", header):
            secret = match.group(1)
        else:
            raise errors.InvalidAuthHeader()

        if secret != expected_secret:
            raise errors.WrongAuthHeader()
