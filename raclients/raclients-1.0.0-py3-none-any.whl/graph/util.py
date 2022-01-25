# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Optional

from graphql import GraphQLError
from graphql import Source
from graphql import SourceLocation


def graphql_error_from_dict(d: dict, query: Optional[str] = None) -> GraphQLError:
    """
    Construct GraphQLError from error dict returned from the server.

    Args:
        d: Error dict.
        query: Original request query. Optional, but allows for better error messages.
    """
    error = GraphQLError(
        message=d["message"],
        # nodes=d.get("nodes"),
        source=Source(body=query) if query is not None else None,
        positions=d.get("positions"),
        path=d.get("path"),
        extensions=d.get("extensions"),
    )

    # For some reason, GraphQLError doesn't take locations in the constructor
    if error.locations is None and "locations" in d:
        error.locations = [SourceLocation(**loc) for loc in d["locations"]]

    return error
