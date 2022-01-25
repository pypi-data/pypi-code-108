from typing import Dict
from typing import Optional

from tecton_proto.args import basic_info_pb2


def prepare_basic_info(
    *, name: str, description: str = "", family: str = "", tags: Optional[Dict[str, str]], owner: str = ""
):
    info = basic_info_pb2.BasicInfo()
    info.name = name
    info.description = description
    info.family = family
    info.tags.update(tags or {})
    info.owner = owner
    return info
