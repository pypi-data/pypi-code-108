import jwt
from typing import Generic, TypeVar, Type

from origin.serialize import simple_serializer


TToken = TypeVar('TToken')


class TokenEncoder(Generic[TToken]):
    """
    Generic helper-class to encode and decode dataclasses to and from JWT.
    """

    class EncodeError(Exception):
        """
        Raised when encoding fails.
        """
        pass

    class DecodeError(Exception):
        """
        Raised when decoding fails.
        """
        pass

    HS256 = 'HS256'
    RS256 = 'RS256'

    def __init__(self, schema: Type[TToken], secret: str, alg: str = HS256):
        """
        TODO

        :param schema:
        :param secret:
        """
        self.schema = schema
        self.secret = secret
        self.alg = alg

        # TODO Detect schema from Generic type instead of parameter

    def encode(self, obj: TToken) -> str:
        """
        TODO

        :param obj:
        :return:
        """
        payload = simple_serializer.serialize(
            obj=obj,
            schema=self.schema,
        )

        # TODO Raise EncodeError

        return jwt.encode(
            payload=payload,
            key=self.secret,
            algorithm=self.alg,
        )

    def decode(self, encoded_jwt: str) -> TToken:
        """
        TODO

        :param encoded_jwt:
        :return:
        """
        try:
            payload = jwt.decode(
                jwt=encoded_jwt,
                key=self.secret,
                algorithms=[self.alg],
            )
        except jwt.DecodeError as e:
            raise self.DecodeError(str(e))

        return simple_serializer.deserialize(
            data=payload,
            schema=self.schema,
        )
