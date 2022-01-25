"""Copyright Alpine Intuition Sàrl team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import gc
import logging
import re
import sys
from types import FunctionType, ModuleType
from typing import Any

import msgpack

log = logging.getLogger(__name__)


def get_encoded_msg(status: str, message: str = None, data: dict = None) -> bytes:
    """Encode message in msgpack."""

    valid_status = ["success", "fail", "error"]
    if status not in ["success", "fail", "error"]:
        raise ValueError(
            f"Invalid status. Available: {', '.join(valid_status)}. Given: {status}"
        )

    msg = {"status": status}
    if message is not None:
        msg["message"] = message
    if data is not None:
        msg["data"] = data  # type: ignore

    return msgpack.packb(msg)


def get_decoded_msg(msg: bytes, mandatory_keys: set):
    """Decoded msgpack message."""

    try:
        decoded_msg = msgpack.unpackb(msg)
    except TypeError:
        error_msg = f"Message must be <class 'bytes'>, got {type(msg)}"
        return False, error_msg, {}
    except msgpack.exceptions.ExtraData:
        error_msg = "Message must be msgpacked"
        return False, error_msg, {}

    if not isinstance(decoded_msg, dict):
        error_msg = (
            "Invalid message type, unpackb message must be a"
            + f"<class 'dict'>, got <class '{type(decoded_msg)}'>"
        )
        return False, error_msg, {}

    if not mandatory_keys.issubset(decoded_msg.keys()):
        missings = ", ".join(mandatory_keys.difference(decoded_msg.keys()))
        error_msg = f"Missing field(s) in message. Missings: {missings}"
        return False, error_msg, {}

    if "status" in decoded_msg:
        if decoded_msg["status"] == "success" and "data" not in decoded_msg:
            error_msg = (
                "Missing field in message. When status is success, "
                + "a 'data' key is needed."
            )
            return False, error_msg, {}
        elif decoded_msg["status"] != "success" and "message" not in decoded_msg:
            error_msg = (
                "Missing field in message. When status is not success, "
                + "a 'message' key is needed."
            )
            return False, error_msg, {}

    return True, "", decoded_msg


def get_obj_size(obj: Any) -> int:
    """Get the bytesize of any object."""

    BLACKLIST = type, ModuleType, FunctionType
    if isinstance(obj, BLACKLIST):
        raise TypeError("get_obj_size() does not take argument of type: {type(obj)}")

    seen_ids = set()
    size = 0
    objects = [obj]

    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = gc.get_referents(*need_referents)

    return size


def sanitize_inputs(inputs: str, verbose: bool = True) -> str:
    """Sanitize a string to avoid shell injection."""
    new_inputs = re.sub("[^A-Za-z0-9_-]+", "", inputs.lower())
    if new_inputs != inputs and verbose:
        log.warning(f"inputs has been sanitized, '{inputs}' -> '{new_inputs}'")
    return new_inputs
