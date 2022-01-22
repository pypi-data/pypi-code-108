import os
import random
from typing import Any, Dict, Optional, Tuple

import jwt
from jwt.api_jwt import decode_complete

#
# [HOW TO GENERATE KEYs]
# openssl genrsa -out private.pem 2048 # private key
# openssl rsa -in private.pem -out public.pem -RSAPublicKey_out # public key
#
# [LOCAL PEM DIR STRUCTURE]
# .pem
# └── stg
#     └── test
#         ├── private.pem
#         └── public.pem
#


def pem_random_key(env: str) -> Tuple[str, str]:
    keys_dir = f".pem/{env}"
    kid = random.choice(os.listdir(keys_dir))
    private_key = None
    with open(f"{keys_dir}/{kid}/private.pem") as f:
        private_key = f.read()
    return (kid, private_key)


def pem_encode(
    payload: Dict[str, Any],
    key: str,
    headers: Optional[Dict[str, Any]] = None,
) -> str:
    return jwt.encode(
        payload,
        key,
        algorithm="RS256",
        headers=headers,
    )


def pem_decode(token: str) -> Dict[str, Any]:
    completed = decode_complete(token, options={"verify_signature": False})
    public_key = open(
        f".pem/{completed['payload']['env']}/{completed['header']['kid']}/public.pem"
    ).read()
    return jwt.decode(token, public_key, algorithms=["RS256"])
