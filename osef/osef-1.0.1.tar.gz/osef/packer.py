"""Functions to pack data to osef format"""
import traceback
from struct import Struct
from typing import Any, Union

from osef import types
from osef._logger import osef_logger
from osef.constants import _Tlv, _TreeNode, _STRUCT_FORMAT
from osef.parser import _align_size


# -- Public functions --
def pack(frame: dict) -> bytes:
    """Encode an osef frame content to a TLV

    :param frame: osef frame dict to be packed in the OSEF format (TLV)
    :raise Raises exception on unknown type
    :return: bytes tlv
    """
    tree = _pack_to_tree(types.OsefTypes.TIMESTAMP_DATA, frame["timestamped_data"])
    return _tree_to_bin(tree)


def _encode_tlv(tlv: _Tlv) -> bytes:
    """Encode a single TLV to bytes sequence"""
    return Struct(_STRUCT_FORMAT % _align_size(tlv.length)).pack(*tlv)


def _tree_to_bin(tree: _TreeNode) -> bytes:
    """Encode a whole tree to binary TLVs"""
    out = bytes()

    # Go through the tree and encode to TLV->bin each branch/leaf
    if tree.leaf_value is not None:
        tlv = _Tlv(tree.type, len(tree.leaf_value), tree.leaf_value)
    else:
        for child in tree.children:
            out = out + _tree_to_bin(child)
        tlv = _Tlv(tree.type, len(out), out)
    return _encode_tlv(tlv)


def _pack_to_tree(osef_type: Union[types.OsefTypes, str], value: Any) -> _TreeNode:
    """Parse an item and generate a TreeNode, using OSEF types"""
    if isinstance(osef_type, str):
        osef_type = types.get_type_by_key(osef_type)
    type_info = types.get_type_info_by_id(osef_type.value)

    # For leaves or unknown, return value
    if isinstance(type_info.node_info, types.LeafInfo):
        return _TreeNode(osef_type.value, None, _pack_value(value, type_info.node_info))

    # For non-leaves, add each child to a list
    children = []
    if type_info.node_info.type == list:
        for child in value:
            child_k, child_v = list(child.items())[0]
            children.append(_pack_to_tree(child_k, child_v))
    elif type_info.node_info.type == dict:
        for child_k, child_v in value.items():
            children.append(_pack_to_tree(child_k, child_v))
    else:
        raise ValueError("Unsupported internal node type.")
    return _TreeNode(osef_type.value, children, None)


def _pack_value(value: Any, leaf_info: types.LeafInfo) -> bytes:
    """Pack a leaf value to a python object (type depends on type of leaf).

    :param value: object to be packed.
    :param leaf_info: type info for unpacking and conversion to python object.
    :return: bytes
    """
    try:
        if leaf_info.pack_function is not None:
            return leaf_info.pack_function(value)
        # unknown parser
        return value
    except Exception:  # pylint: disable=broad-except
        osef_logger.error(
            f"Exception occurred while packing value for {leaf_info}:\n"
            f"Details: {traceback.format_exc()}"
        )
        return value
