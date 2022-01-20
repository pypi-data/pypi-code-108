"""Utilities"""
import io
import json


def stream_load(data: io.BytesIO):
    """Load JSON data as steam

    From <https://stackoverflow.com/questions/6886283/how-i-can-i-lazily-read-multiple-json-values-from-a-file-stream-in-python>
    """  # pylint: disable=line-too-long
    start_pos = 0

    while True:
        try:
            obj = json.load(data)
            yield obj

            return
        except json.JSONDecodeError as exc:
            data.seek(start_pos)
            json_str = data.read(exc.pos)
            obj = json.loads(json_str)
            start_pos += exc.pos
            yield obj
