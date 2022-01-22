import random
from typing import Any, Type

from .decode_static import prod_cert, stg_cert
from .jwt_payload import JWTPayloadBuilder
from .kms_encode import kms_encode as encode
from .pem_coder import pem_encode, pem_random_key


class JWTEncoder:
    payload_builder_class: Type[JWTPayloadBuilder]
    stage: str = "stg"

    def __init__(self, client: Any) -> None:
        self.client = client

    def encode(self, user: Any, pem: bool = False) -> str:
        builder = self.payload_builder_class(client=self.client, data=user)
        payload = builder.get_payload()

        if pem:
            kid, private_key = pem_random_key(self.stage)
            return pem_encode(
                payload,
                private_key,
                headers={"kid": kid},
            )

        keys = stg_cert if self.stage == "stg" else prod_cert
        key = random.choice(keys["keys"])["kid"]
        return encode(payload, key=key, headers={"kid": key})
