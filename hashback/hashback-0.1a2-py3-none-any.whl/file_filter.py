from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from . import protocol


@dataclass
class FilterPathNode:
    filter_type: protocol.FilterType = field(default=protocol.FilterType.INCLUDE)
    exceptions: Dict[str, "FilterPathNode"] = field(default_factory=dict)


def normalize_filters(filters: Iterable[protocol.Filter]) -> Tuple[List[str], FilterPathNode]:
    """
    Take a list of filters and build them into a tree of filters.
    :param filters: A list of filters
    :return: A _NormalizedFilter tree structure
    """
    result_node = FilterPathNode(filter_type=None)
    patterns = []
    _build_tree(result_node, patterns, filters)
    _patch_and_prune(result_node)
    return patterns, result_node


def _build_tree(tree_root: FilterPathNode, patterns: List[str], filters: Iterable[protocol.Filter]):
    # TODO This somehow needs to work with non system URLS.  Think S3 urls from a Windows Box!
    for filter_item in filters:
        if filter_item.filter is protocol.FilterType.PATTERN_EXCLUDE:
            patterns.append(filter_item.path)
            continue
        if filter_item.path == '.':
            tree_root.filter_type = filter_item.filter
        else:
            filter_path = Path(filter_item.path)
            if filter_path.is_absolute():
                raise ValueError(f"Filter paths must not be absolute.  {filter_item.path} is incorrect.")
            position = tree_root
            for directory in filter_path.parts[:-1]:
                if directory not in position.exceptions:
                    position.exceptions[directory] = FilterPathNode(filter_type=position.filter_type)
                position = position.exceptions[directory]
            directory = filter_path.name
            if directory in position.exceptions:
                position.exceptions[directory].filter_type = filter_item.filter
            else:
                position.exceptions[directory] = FilterPathNode(filter_type=filter_item.filter)


def _patch_and_prune(filters: FilterPathNode, parent_type: protocol.FileType = protocol.FilterType.INCLUDE):
    """
    It's perfectly legitimate for a user to have redundant filters such as excluding a directory inside another that
    is already excluded.  This code will prune filters that are not actually an exception to it's parent.

    Two scenarios for example.  If we EXCLUDE foo but INCLUDE foo/bar then we want foo listed in the backup, but with
    no attributes and containing only bar.  That is, despite excluding foo, we still make a partial backup of it because
    we need to backup foo/bar.

    If we then change the foo/bar filter to EXCLUDE there will be two filters to EXCLUDE foo and EXCLUDE foo/bar.
    It makes no sense at all to say foo has any exceptions.  EXCLUDE foo/bar is not an exception EXCLUDE foo.  So we
    must NOT make a partial backup of foo.

    :param filters:  The filters to prune
    :param parent_type: The effective filter type of the parent.  At the root this will be INCLUDE (default)
    """
    to_prune = []
    if filters.filter_type is None:
        # Patch Nones with the parent_type
        filters.filter_type = parent_type
    for name, child in filters.exceptions.items():
        _patch_and_prune(child, filters.filter_type)
        if child.filter_type is filters.filter_type and not child.exceptions:
            # Here the child is the same as the parent and it has no exceptions so it has no effect... it's meaningless
            to_prune.append(name)
    for name in to_prune:
        del filters.exceptions[name]
