"""plugins for IDEs.
"""
import inspect
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from attr import Factory
from attr import attrib
from attr import attrs

from _pistar.config.cmdline import hookimpl
from _pistar.pistar_pytest.utils import write_attr

if TYPE_CHECKING:
    from _pistar.main import Session
    from _pistar.utilities.testcase.case import TestCase


@attrs
class FSNode:
    """
    The file system node for case tree.

    """

    name = attrib(default=None)
    uri = attrib(default=None)
    children = attrib(type=List["FSNode"], default=Factory(list))

    @classmethod
    def from_path(cls, path: Path) -> "FSNode":
        return cls(name=path.name, uri=str(path.absolute()))


@attrs
class Line:
    line = attrib(type=int, default=0)
    character = attrib(type=int, default=0)


@attrs
class Range:
    start = attrib(type=Line, default=None)
    end = attrib(type=Line, default=None)


@attrs
class CaseNode(FSNode):
    range = attrib(type=Optional[Range], default=None)

    @classmethod
    def from_case(cls, case: "TestCase") -> "CaseNode":
        path = Path(case.path).absolute()
        _, lineno = inspect.findsource(case.clazz)
        line = Line(lineno, 0)
        ranges = Range(line, line)

        return cls(name=case.name, uri=str(path), range=ranges)


class CollectTree:
    def __init__(self, session: "Session"):
        self._node_cache: Dict[Path, FSNode] = dict()
        self.session: "Session" = session

    @classmethod
    def from_session(cls, session: "Session") -> "CollectTree":
        return cls(session)

    def build_tree(self, target: str):
        root = self.session.rootpath
        self._node_cache[root] = FSNode.from_path(root)

        all_path = frozenset(self.session._initialpaths)
        for path in all_path:
            self._node_cache[path] = FSNode.from_path(path)

        self._build()

        for path in all_path:

            node = self._node_cache.get(path, None)
            if node:
                write_attr(node, str(self.session.outpath), target)

    def _build(self):
        for case in self.session.cases:
            case_node = CaseNode.from_case(case)
            self._insert(case_node)

    def _insert(self, node: FSNode):

        if isinstance(node, CaseNode):
            father = Path(node.uri)
        else:
            father = Path(node.uri).parent
        if father is None:
            return
        father_node = self._node_cache.get(father, None)
        if father_node:
            father_node.children.append(node)
        else:
            new_node = FSNode.from_path(father)
            new_node.children.append(node)
            self._node_cache[father] = new_node
            self._insert(new_node)


@hookimpl
def pistar_collect_finish(session: "Session"):
    """
    This hook implement writes a collect tree when using "--collectonly".
    Some IDE plugin (ex:vscode) uses this file to rendering case tree.
    """
    if len(session.cases) > 0 and session.config.collectonly:
        tree = CollectTree.from_session(session)
        tree.build_tree("collect.json")
