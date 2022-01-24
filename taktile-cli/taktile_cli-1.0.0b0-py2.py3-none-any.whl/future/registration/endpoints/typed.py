import typing as t

from pydantic import BaseModel
from taktile_types.enums.endpoint import EndpointKinds

from .abc import XType, YType
from .generic import GenericEndpoint


class TypedEndpoint(GenericEndpoint):
    kind: EndpointKinds = EndpointKinds.TYPED

    @staticmethod
    def supported(
        *, X: XType = None, y: YType = None, profile: t.Optional[str] = None,
    ) -> bool:
        return (
            profile is None
            and isinstance(X, (type(BaseModel), type(t.Any)))
            and isinstance(y, (type(BaseModel), type(t.Any)))
        )
