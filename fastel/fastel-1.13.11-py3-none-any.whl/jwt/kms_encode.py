import base64
import json
from calendar import timegm
from datetime import datetime
from typing import Any, Dict, Optional

import boto3


def kms_encode(
    payload: Dict[str, Any],
    key: str,
    headers: Optional[Dict[str, Any]] = None,
) -> str:
    def base64url_encode(input: bytes) -> bytes:
        return base64.urlsafe_b64encode(input).replace(b"=", b"")

    # Payload
    payload = payload.copy()
    for time_claim in ["exp", "iat", "nbf"]:
        # Convert datetime to a intDate value in known time-format claims
        if isinstance(payload.get(time_claim), datetime):
            payload[time_claim] = timegm(payload[time_claim].utctimetuple())

    json_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    # Header
    header = {"typ": "JWT", "alg": "RS256"}

    if headers:
        header.update(headers)

    json_header = json.dumps(header, separators=(",", ":")).encode()

    segments = []
    segments.append(base64url_encode(json_header))
    segments.append(base64url_encode(json_payload))

    # Segments
    signing_input = b".".join(segments)
    try:
        client = boto3.client("kms", "ap-northeast-1")
        resp = client.sign(
            KeyId=key,
            Message=signing_input,
            SigningAlgorithm="RSASSA_PKCS1_V1_5_SHA_256",
        )
        signature = resp["Signature"]
    except Exception:
        raise RuntimeError("[ERROR] fail to sign with KMS")

    segments.append(base64url_encode(signature))
    encoded_string = b".".join(segments)
    return encoded_string.decode("utf-8")
