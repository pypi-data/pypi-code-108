"""
about
"""

from typing import List
from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi

about_v1 = Blueprint("about_v1", url_prefix="/about")


@about_v1.get("/", version=1)
@openapi.tag("General")
@openapi.response(
    200,
    {
        "application/json": {
            "mode": str,
            "versions": List[str],
        }
    },
    description="OK",
)
@openapi.description("Returns the supported API versions.")
async def about_v1_get(request):  # pylint: disable=unused-argument
    """
    Lists general information about the API.
    """
    return json(
        {
            "mode": "dbus",
            "versions": ["v1", "v2"],
        },
        200
    )
