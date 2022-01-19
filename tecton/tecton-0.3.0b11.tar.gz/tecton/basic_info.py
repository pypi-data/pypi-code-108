from typing import Dict
from typing import Optional

from tecton_proto.args import basic_info_pb2


def prepare_basic_info(
    *,
    name: str,
    description: Optional[str],
    family: Optional[str],
    tags: Optional[Dict[str, str]],
    owner: Optional[str]
):
    info = basic_info_pb2.BasicInfo()
    info.name = name
    info.description = description or ""
    info.family = family or ""
    info.tags.update(tags or {})
    info.owner = owner or ""
    return info
