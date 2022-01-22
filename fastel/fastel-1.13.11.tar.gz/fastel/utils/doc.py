from typing import Dict

from fastapi import APIRouter
from fastapi.routing import BaseRoute  # type: ignore

_api_docs = {}


def init_docs(docs: Dict[str, str]) -> None:
    global _api_docs
    _api_docs = docs


def router_with_doc(router: APIRouter) -> APIRouter:
    route: BaseRoute
    for route in router.routes:
        method = next(iter(route.methods))
        path = route.path
        key = f"{method} {path}"
        print(key)

        doc = _api_docs.get(key, None)
        if doc:
            route.description = doc
        else:
            route.description = "No doc available"
    return router
