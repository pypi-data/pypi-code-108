"""
Nozomi
Encoder Module
author: hugh@blinkybeach.com
"""
from nozomi.data.abstract_encodable import AbstractEncodable
from json import JSONEncoder
from typing import Any


class Encoder(JSONEncoder):
    """A JSON encoder capable of interacting with Encodable objects"""
    def default(self, object) -> Any:

        if isinstance(object, AbstractEncodable):
            return object.encode()

        if (
                isinstance(object, list)
                and False not in [
                    isinstance(o, AbstractEncodable) for o in object
                ]
        ):
            return [o.encode() for o in object]

        return super().default(object)
