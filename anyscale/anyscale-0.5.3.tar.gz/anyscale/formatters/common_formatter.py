from datetime import datetime
import json
from typing import Any


def _json_converter(o: Any) -> Any:
    """
    Custom JSON convert to handle datetime objects from the server.

    Without this, we'll see errors like "datetime is not JSON serializable"
    """

    if isinstance(o, datetime):
        return o.__str__()


def prettify_json(json_obj: Any) -> str:
    """
    Converts a JSON object into a pretty-printable string.
    """

    return json.dumps(json_obj, default=_json_converter, sort_keys=True, indent=4)
