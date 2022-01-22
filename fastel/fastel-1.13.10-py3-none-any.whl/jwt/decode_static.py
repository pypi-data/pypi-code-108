from typing import Any, Dict

from jwt.algorithms import get_default_algorithms
from jwt.api_jwt import decode, decode_complete

from .pem_coder import pem_decode

# https://keys.revtel-api.com/certs.json
prod_cert = {
    "keys": [
        {
            "e": "AQAB",
            "kid": "bc36e546-f24a-4635-a77b-eecb20602504",
            "kty": "RSA",
            "n": "8oPMlKMnG9Uvyr8SMSLf5N7pl2ciEL-OWkAYngAzV1Y492cH8PWWFCibpiXU6iNlBbP_py2O6p8xfMHX1vGCF9uFU__iqc5RBbaCYL1kxczQbCt69tPLdyv3_6FNfMioc62Cym77rEVIa4uRLJl0TB_BJ89beCoL7BO6U1szGz3oVn-4igsc8GQRJOaZkZXY0JIBqB7dTHBgiq1R444ex_Tl1M6E9w45PxzowLOn1GWv6X5wyOSX1z-g60ErmDdxuu3N3lm2fJr9W-mjFgMvo4V9tBQmABaWO573I82IJymxt3C6B1g9Co9P1Thk5zMxtm33Om2FrizinUZbnQAtqQ",
        },
        {
            "e": "AQAB",
            "kid": "d4601977-6244-4a01-87dd-af0c1855886a",
            "kty": "RSA",
            "n": "yrIO_j-qbZfDlbLaTF-TQC38LVv8FVaXV4RPwNwSL_3QQA04HO1lnA8eXf2jV3RbI3WVey9jgDxjIidGAQQ0EJawXX7lPKWj56gDWBjPID7z-32DXicPww7vAgP8KD_GD00bwDnrnPCEveZQ9fAX-9zJpDNLRZlZ-GdgwOP55dIUFaOGeS1GP3jCBcy9auRzthBV4CO2Y_WzC69yL-4WgBPY_cIEc49vZ_Xyyo2mP36-fHzJc9eQ-moRczJ_hlCUe6DPfC99ojMFxXyd9SkD6BvTdnI5Bw-DPd4MCQj6KeSTuWTVfi2zsL2ooX0e8oLqmdhKqEB7T9LAr2efJkBGQQ",
        },
    ]
}

# https://keys.revtel-api.com/certs-stg.json
stg_cert = {
    "keys": [
        {
            "e": "AQAB",
            "kid": "df9885fa-942b-40c0-988c-9c3af76694bc",
            "kty": "RSA",
            "n": "x_-UkGLNQVRBXXW894iokDf7irGQ8rNPzsp-9N4ylVrkES93OL95E_rOdoK0Z8kCuwPOvKfc1QmgBFoJjMMaxI3zLDdDTl9QRIS1e1akecuAdzMj53X_t98Z2pgcT1paoDSkHh7qgYRKmt1xpU7fbKrogjdzqTv3vsnB3tQU2P1-9UJtH3-1BoAVhyiusFqXLH0o6Rp7drMbVYbvyj19nRwcBZz9gtO_bWyYGz0KUtFkm_vc31JmCARif7Tb4vc6FsmjGCgaQ9OSbJLgmYS7ZeVLFomyLKZuDeyAbS0rfzjC6Cf5heu6F2F44MdRoq-QK88nZ19fOpcJk1CkYPtySQ",
        },
        {
            "e": "AQAB",
            "kid": "1a7f2fbe-5112-4450-b7f1-27187d6030fb",
            "kty": "RSA",
            "n": "nPPHuzGJ8M9eZVr2f_CUrzFzyPQ0Ks9R31abO2B6qSOKQb_7aLQC7kOB02wWckyqpKhMRHTVbpKBJXYI1sga_iAaFfDyJ8-RVH3-hbpF1-_Bv7AteGJSZe2Etyi4kFXSZs2pDNOgUS6zvrkdQTlIqSst6MGJNKiaF1OpsmYlwAzJF37YAbrkuNOC1nbQorKkqQzSDa9667ZiEGoU65TGWP0FWwuzSBJGb8AOVNIEdIUaEdTrimoENzJOJR-RHeRGPLpU_Fe7TRj_RLyixDB6Hp_ZyYHW3Su7N3YBu2vZnp42d29E1UMFCU6k_5uoWR6rvosxCL1FkfaoXvpQ78oDmQ",
        },
    ]
}


def decode_static(token: str, pem: bool = False) -> Dict[str, Any]:
    if pem:
        return pem_decode(token)

    unverified = decode_complete(token, options={"verify_signature": False})
    signing_key = None
    signing_keys = stg_cert if unverified["payload"]["env"] == "stg" else prod_cert
    for key in signing_keys["keys"]:
        if key["kid"] == unverified["header"]["kid"]:
            signing_key = key
            break

    algo = get_default_algorithms()["RS256"]  # type: ignore
    signing_key = algo.from_jwk(signing_key)
    verified = decode(
        token, key=signing_key, algorithms=["RS256"], options={"verify_aud": False}  # type: ignore
    )

    return verified
