import pathlib
import typing as t

from tktl.core.exceptions import EndpointInstantiationError

from .endpoints import ArrowEndpoint, GenericEndpoint, ProfiledEndpoint, TypedEndpoint
from .endpoints.abc import XType, YType

# Enpoint types sorted by precedence
ENDPOINT_TYPES = [ProfiledEndpoint, ArrowEndpoint, TypedEndpoint, GenericEndpoint]


class Tktl:
    def __init__(self):
        self._endpoints = []

    @property
    def endpoints(self):
        return self._endpoints

    def endpoint(
        self,
        *,
        X: t.Union[XType, str] = None,
        y: t.Union[YType, str] = None,
        profile: t.Optional[str] = None,
        profile_columns: t.Optional[t.List[str]] = None,
        **kwargs,
    ):

        if isinstance(X, str):
            X = pathlib.Path(X)

        if isinstance(y, str):
            y = pathlib.Path(y)

        try:
            Constructor = next(
                endpoint
                for endpoint in ENDPOINT_TYPES
                if endpoint.supported(X=X, y=y, profile=profile)
            )
        except StopIteration:
            raise EndpointInstantiationError(
                f"Arguments of type X={type(X)} y={type(y)} and profile={profile}"
                " are not supported by any endpoint type."
            )

        def decorator(f):
            endpoint = Constructor(
                name=f.__name__,
                func=f,
                position=len(self._endpoints),
                X=X,
                y=y,
                profile_columns=profile_columns,
                profile=profile,
                **kwargs,
            )
            self._endpoints.append(endpoint)
            return f

        return decorator
