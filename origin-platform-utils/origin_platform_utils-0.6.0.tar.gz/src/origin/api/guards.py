from typing import List
from abc import abstractmethod

from .context import Context
from .responses import Unauthorized


class EndpointGuard(object):

    @abstractmethod
    def validate(self, context: Context):
        raise NotImplementedError


# class ServiceGuard(EndpointGuard):
#     """
#     Allows only specific services to access this endpoint.
#     """
#     def __init__(self, *services: Service):
#         self.services = services
#
#
# class IssuerGuard(EndpointGuard):
#     """
#     Allows only specific issuers to access this endpoint.
#     """
#     def __init__(self, *services: Service):
#         self.services = services


class TokenGuard(EndpointGuard):
    """
    Only Allows requests with a valid token provided.
    """
    def validate(self, context: Context):
        if context.token is None:
            raise Unauthorized('Unauthorized')


class ScopedGuard(EndpointGuard):
    """
    Only Allows requests with specific scopes granted.
    """
    def __init__(self, *scopes: str):
        self.scopes = scopes

    def validate(self, context: Context):
        if context.token is None:
            raise Unauthorized('Unauthorized')
        for scope in self.scopes:
            if scope not in context.token.scope:
                # TODO Write proper message
                raise Unauthorized('Missing scope %s' % scope)


class Bouncer(object):
    def validate(self, context: Context, guards: List[EndpointGuard]):
        for guard in guards:
            guard.validate(context)


# -- Singletons --------------------------------------------------------------


bouncer = Bouncer()
