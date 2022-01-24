import base64
import hmac
import json
import os

from functools import reduce
from base64 import b64decode
from hashlib import sha1

def generate_device_id() -> str:
    identifier = os.urandom(20)
    key = bytes.fromhex("76b4a156aaccade137b8b1e77b435a81971fbd3e")
    mac = hmac.new(key, b"\x32" + identifier, sha1)
    return f"32{identifier.hex()}{mac.hexdigest()}".upper()

def generate_signature(data) -> str:
    try: d = data.encode("utf-8")
    except Exception: d = data

    mac = hmac.new(bytes.fromhex("fbf98eb3a07a9042ee5593b10ce9f3286a69d4e2"), d, sha1)
    return base64.b64encode(bytes.fromhex("32") + mac.digest()).decode("utf-8")

def generate_device_info():
    return {
        "device_id": generate_device_id(),
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.5.33562)"
    }

# okok says: please use return annotations :(( https://www.python.org/dev/peps/pep-3107/#return-values

def decode_sid(sid: str) -> dict:
    return json.loads(b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())

def sid_to_uid(SID: str) -> str: return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str: return decode_sid(SID)["4"]