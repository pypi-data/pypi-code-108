from functools import partial
from http import HTTPStatus
from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import UJSONResponse


def _post(self, *args, **kwargs):
    _set_default_status(kwargs, HTTPStatus.CREATED)
    return APIRouter.post(self, *args, **kwargs)


def _delete(self, *args, **kwargs):
    _set_default_status(kwargs, HTTPStatus.NO_CONTENT)
    return APIRouter.delete(self, *args, **kwargs)


def _set_default_status(kwargs: dict[str, Any], status: int):
    kwargs.setdefault('status_code', status)


def _overload_function(target: APIRouter, name: str, func: Callable) -> None:
    setattr(target, name, partial(func, target))


def router_factory(create_post: bool, no_content_delete: bool):
    """Returns a router with default response class as :class:`fastapi.responses.UJSONResponse`
    :param:`create_post` - overrides :method:`fastapi.APIRouter.post` to use HTTP_201_CREATED as default status code.
    :param:`no_content_delete` - overrides :method:`fastapi.APIRouter.delete` to use HTTP_204_NO_CONTENT as default status code.
    """
    router = APIRouter(default_response_class=UJSONResponse)
    if create_post:
        _overload_function(router, 'post', _post)
    if no_content_delete:
        _overload_function(router, 'delete', _delete)
    return router
