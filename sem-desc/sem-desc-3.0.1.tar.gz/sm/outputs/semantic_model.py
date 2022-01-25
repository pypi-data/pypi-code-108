import enum
import tempfile
from copy import copy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Set, Tuple, Union

import matplotlib.pyplot as plt
import orjson
import pydot
from colorama import Back, Fore, Style, init
from graph.retworkx import (
    BaseEdge,
    BaseNode,
    RetworkXDiGraph,
)
from IPython import get_ipython
from IPython.core.display import display
from PIL import Image
from sm.misc import auto_wrap


@dataclass
class SemanticType:
    class_abs_uri: str
    predicate_abs_uri: str
    class_rel_uri: str
    predicate_rel_uri: str

    @property
    def label(self):
        return (self.class_rel_uri, self.predicate_rel_uri)

    def is_entity_type(self) -> bool:
        """Telling if this semantic type is for entity column"""
        return self.predicate_abs_uri in {
            "http://www.w3.org/2000/01/rdf-schema#label",
            "http://schema.org/name",
        }

    def __hash__(self):
        return hash((self.class_abs_uri, self.predicate_abs_uri))

    def __eq__(self, other):
        if not isinstance(other, SemanticType):
            return False

        return (
            self.class_abs_uri == other.class_abs_uri
            and self.predicate_abs_uri == other.predicate_abs_uri
        )

    def __str__(self):
        return f"{self.class_rel_uri}--{self.predicate_rel_uri}"

    def __repr__(self):
        return f"SType({self})"


@dataclass(eq=True)
class ClassNode(BaseNode[int]):
    abs_uri: str
    rel_uri: str
    approximation: bool = False
    readable_label: Optional[str] = None
    id: int = -1  # id is set automatically after adding to graph

    @property
    def label(self):
        return self.readable_label or self.rel_uri


@dataclass(eq=True)
class DataNode(BaseNode[int]):
    col_index: int
    label: str
    id: int = -1  # id is set automatically after adding to graph


class LiteralNodeDataType(str, enum.Enum):
    String = "string"
    # should use full URI
    Entity = "entity-id"


@dataclass(eq=True)
class LiteralNode(BaseNode[int]):
    value: str
    # readable label of the literal node, should not confuse it with value
    readable_label: Optional[str] = None
    # whether the literal node is in the surround context of the dataset
    is_in_context: bool = False
    datatype: LiteralNodeDataType = LiteralNodeDataType.String
    id: int = -1  # id is set automatically after adding to graph

    @property
    def label(self):
        return self.readable_label or self.value


Node = Union[ClassNode, DataNode, LiteralNode]


@dataclass(eq=True)
class Edge(BaseEdge[int, str]):
    source: int
    target: int
    abs_uri: str
    rel_uri: str
    approximation: bool = False
    readable_label: Optional[str] = None
    id: int = -1  # id is set automatically after adding to graph

    @property
    def key(self):
        return self.abs_uri

    @property
    def label(self):
        return self.readable_label or self.rel_uri


class SemanticModel(RetworkXDiGraph[str, Node, Edge]):
    def __init__(self, check_cycle=False, multigraph=True):
        super().__init__(check_cycle=check_cycle, multigraph=multigraph)
        self.column2id: List[int] = []
        self.value2id: Dict[str, int] = {}

    def get_data_node(self, column_index: int) -> DataNode:
        return self._graph.get_node_data(self.column2id[column_index])

    def get_literal_node(self, value: str) -> LiteralNode:
        """Get literal node by value O(n). Throw error when the value does not found"""
        return self._graph.get_node_data(self.value2id[value])

    def has_data_node(self, column_index: int) -> bool:
        return column_index < len(self.column2id) and self.column2id[column_index] != -1

    def add_node(self, node: Node) -> int:
        node_id = super().add_node(node)
        if isinstance(node, DataNode):
            while len(self.column2id) - 1 < node.col_index:
                self.column2id.append(-1)
            assert self.column2id[node.col_index] == -1
            self.column2id[node.col_index] = node_id
        elif isinstance(node, LiteralNode):
            assert node.value not in self.value2id
            self.value2id[node.value] = node_id
        return node_id

    def get_semantic_types_of_column(self, col_index: int) -> List[SemanticType]:
        dnode = self.get_data_node(col_index)
        sem_types = set()
        for e in self.in_edges(dnode.id):
            u = self.get_node(e.source)
            assert isinstance(u, ClassNode)
            sem_types.add(SemanticType(u.abs_uri, e.abs_uri, u.rel_uri, e.rel_uri))
        return list(sem_types)

    def get_semantic_types(self) -> Set[SemanticType]:
        sem_types = set()
        for e in self.iter_edges():
            u = self.get_node(e.source)
            assert isinstance(u, ClassNode)
            if isinstance(self.get_node(e.target), ClassNode):
                continue

            sem_types.add(SemanticType(u.abs_uri, e.abs_uri, u.rel_uri, e.rel_uri))
        return sem_types

    def copy(self):
        sm = super().copy()
        sm.column2id = copy(self.column2id)
        sm.value2id = copy(self.value2id)
        return sm

    def deep_copy(self):
        sm = self.copy()
        for n in sm.iter_nodes():
            sm.update_node(copy(n))
        for e in sm.iter_edges():
            sm.update_edge(copy(e))
        return sm

    def to_dict(self):
        return {
            "version": 1,
            "nodes": [asdict(u) for u in self.iter_nodes()],
            "edges": [asdict(e) for e in self.iter_edges()],
        }

    def to_json_file(self, outfile: Union[str, Path]):
        with open(outfile, "wb") as f:
            f.write(orjson.dumps(self.to_dict(), option=orjson.OPT_INDENT_2))

    @staticmethod
    def from_dict(record: dict):
        sm = SemanticModel()
        id2node = {}
        for u in record["nodes"]:
            if "col_index" in u:
                id2node[u["id"]] = sm.add_node(DataNode(**u))
            elif "abs_uri" in u:
                id2node[u["id"]] = sm.add_node(ClassNode(**u))
            else:
                lnode = LiteralNode(**u)
                lnode.datatype = LiteralNodeDataType(lnode.datatype)
                id2node[u["id"]] = sm.add_node(lnode)
        for e in record["edges"]:
            e["source"] = id2node[e["source"]]
            e["target"] = id2node[e["target"]]
            assert sm.has_node(e["source"]) and sm.has_node(e["target"])
            sm.add_edge(Edge(**e))
        return sm

    @staticmethod
    def from_json_file(infile: Union[str, Path]):
        with open(infile, "rb") as f:
            record = orjson.loads(f.read())
            return SemanticModel.from_dict(record)

    def draw(
        self,
        filename: Optional[str] = None,
        format: Literal["png", "jpg"] = "png",
        quality: int = 100,
        no_display: bool = False,
        max_char_per_line: int = 20,
    ):
        """
        Parameters
        ----------
        filename : str | none
            output to a file or display immediately (inline if this is jupyter lab)

        format: png | jpg
            image format

        quality: int
            if it's < 100, we will compress the image using PIL

        no_display: bool
            if the code is running inside Jupyter, if enable, it returns the object and manually display (default is
            automatically display)

        max_char_per_line: int
            wrap the text if it's too long

        Returns
        -------
        """
        if filename is None:
            fobj = tempfile.NamedTemporaryFile()
            filename = fobj.name
        else:
            fobj = None

        dot_g = pydot.Dot(graph_type="digraph")
        for u in self.iter_nodes():
            if isinstance(u, ClassNode):
                label = auto_wrap(u.label.replace(":", r"\:"), max_char_per_line)
                dot_g.add_node(
                    pydot.Node(
                        name=u.id,
                        label=label,
                        shape="ellipse",
                        style="filled",
                        color="white",
                        fillcolor="lightgray",
                    )
                )
            elif isinstance(u, DataNode):
                label = auto_wrap(
                    fr"C{u.col_index}\:" + u.label.replace(":", r"\:"),
                    max_char_per_line,
                )
                dot_g.add_node(
                    pydot.Node(
                        name=u.id,
                        label=label,
                        shape="plaintext",
                        style="filled",
                        fillcolor="gold",
                    )
                )
            else:
                label = auto_wrap(u.value, max_char_per_line)
                dot_g.add_node(
                    pydot.Node(
                        name=u.id,
                        label=label,
                        shape="plaintext",
                        style="filled",
                        fillcolor="purple",
                    )
                )

        for e in self.iter_edges():
            label = auto_wrap(e.label.replace(":", r"\:"), max_char_per_line)
            dot_g.add_edge(
                pydot.Edge(
                    e.source, e.target, label=label, color="brown", fontcolor="black"
                )
            )

        # graphviz from anaconda does not support jpeg so use png instead
        dot_g.write(filename, prog="dot", format=format)
        if quality < 100:
            im = Image.open(filename)
            im.save(filename, optimize=True, quality=quality)

        if fobj is not None:
            img = Image.open(filename)
            try:
                if no_display:
                    return img
            finally:
                fobj.close()

            try:
                shell = get_ipython().__class__.__name__
                if shell == "ZMQInteractiveShell":
                    display(img)
                else:
                    plt.imshow(img, interpolation="antialiased")
                    plt.show()
            except NameError:
                plt.imshow(img, interpolation="antialiased")
                plt.show()
            finally:
                fobj.close()

    def draw_difference(
        self,
        gold_sm: "SemanticModel",
        filename=None,
        format="jpeg",
        no_display: bool = False,
        max_char_per_line: int = 20,
    ):
        """
        Colors:
        * green, red for edges/nodes in the pred_sm that does not appear in the gold_sm
        * lightgray for edges/nodes that are in the gold_sm but not in the pred_sm

        Parameters
        ----------
        gold_sm : SemanticModel
            the correct semantic model that we are going to compare to
        filename : str | none
            output to a file or display immediately (inline if this is jupyter lab)

        no_display : bool
            if the code is running inside Jupyter, if enable, it returns the object and manually display (default is
            automatically display)

        max_char_per_line: int
            wrap the text if it's too long

        Returns
        -------
        """
        from sm.evaluation.sm_metrics import precision_recall_f1

        if filename is None:
            fobj = tempfile.NamedTemporaryFile()
            filename = fobj.name
        else:
            fobj = None

        bijection = precision_recall_f1(gold_sm, self).bijection
        dot_g = pydot.Dot(graph_type="digraph")
        data_nodes = set()
        for u in self.iter_nodes():
            if isinstance(u, ClassNode):
                if bijection.prime2x[u.id] is None:
                    # this is a wrong node
                    fillcolor = "tomato"
                else:
                    fillcolor = "mediumseagreen"

                label = auto_wrap(u.label.replace(":", r"\:"), max_char_per_line)
                dot_g.add_node(
                    pydot.Node(
                        name=u.id,
                        label=label,
                        shape="ellipse",
                        style="filled",
                        color="white",
                        fillcolor=fillcolor,
                    )
                )
            elif isinstance(u, DataNode):
                data_nodes.add(u.col_index)
                dot_uid = f"C{u.col_index:02d}_{u.label}"
                label = auto_wrap(
                    f"C{u.col_index}: " + u.label.replace(":", r"\:"), max_char_per_line
                )
                dot_g.add_node(
                    pydot.Node(
                        name=dot_uid,
                        label=label,
                        shape="plaintext",
                        style="filled",
                        fillcolor="gold",
                    )
                )
            else:
                raise NotImplementedError()

        # node in gold_sm doesn't appear in the pred_sm
        for u in gold_sm.iter_nodes():
            if isinstance(u, ClassNode):
                if bijection.x2prime[u.id] is None:
                    # class node in gold model need to give a different namespace (`gold:`) to avoid collision
                    dot_uid = ("gold:" + str(u.id)).replace(":", "_")
                    dot_g.add_node(
                        pydot.Node(
                            name=dot_uid,
                            label=auto_wrap(
                                u.label.replace(":", r"\:"), max_char_per_line
                            ),
                            shape="ellipse",
                            style="filled",
                            color="white",
                            fillcolor="lightgray",
                        )
                    )
            elif isinstance(u, DataNode):
                if u.col_index not in data_nodes:
                    dot_uid = f"C{u.col_index:02d}_{u.label}"
                    dot_g.add_node(
                        pydot.Node(
                            name=dot_uid,
                            label=auto_wrap(
                                f"C{u.col_index}: " + u.label.replace(":", r"\:"),
                                max_char_per_line,
                            ),
                            shape="plaintext",
                            style="filled",
                            fillcolor="lightgray",
                        )
                    )
            else:
                raise NotImplementedError()

        # add edges in pred_sm
        x_triples = set()
        for e in gold_sm.iter_edges():
            v = gold_sm.get_node(e.target)
            if isinstance(v, ClassNode):
                target = v.id
            elif isinstance(v, DataNode):
                target = (v.col_index, v.label)
            else:
                target = v.value
            x_triples.add((e.source, e.label, target))

        x_prime_triples = set()
        for e in self.iter_edges():
            uid, vid = e.source, e.target
            v = self.get_node(vid)
            x_prime_triple = (
                bijection.prime2x[uid],
                e.label,
                bijection.prime2x[vid]
                if isinstance(v, ClassNode)
                else ((v.col_index, v.label) if isinstance(v, DataNode) else v.value),
            )
            x_prime_triples.add(x_prime_triple)
            if x_prime_triple in x_triples:
                color = "darkgreen"
            else:
                color = "red"

            dot_u = uid
            dot_v = (
                vid
                if isinstance(v, ClassNode)
                else (
                    f"C{v.col_index:02d}_{v.label}"
                    if isinstance(v, DataNode)
                    else v.value
                )
            )
            dot_g.add_edge(
                pydot.Edge(
                    dot_u,
                    dot_v,
                    label=auto_wrap(e.label.replace(":", r"\:"), max_char_per_line),
                    color=color,
                    fontcolor="black",
                )
            )

        # add edges in gold_sm that is not in pred_sm
        for x_triple in x_triples:
            if x_triple not in x_prime_triples:
                # class node in gold model need to give a different namespace (`gold:`) to avoid collision
                dot_u = (
                    "gold:" + x_triple[0]
                    if bijection.x2prime[x_triple[0]] is None
                    else bijection.x2prime[x_triple[0]]
                )
                dot_u = dot_u.replace(":", "_")

                if isinstance(x_triple[2], tuple):
                    dot_v = f"C{x_triple[2][0]:02d}_{x_triple[2][1]}"
                else:
                    dot_v = (
                        "gold:" + x_triple[2]
                        if bijection.x2prime[x_triple[2]] is None
                        else bijection.x2prime[x_triple[2]]
                    )
                    dot_v = dot_v.replace(":", "_")

                dot_g.add_edge(
                    pydot.Edge(
                        dot_u,
                        dot_v,
                        label=auto_wrap(
                            x_triple[1].replace(":", r"\:"), max_char_per_line
                        ),
                        color="gray",
                        fontcolor="black",
                    )
                )

        # graphviz from anaconda does not support jpeg so use png instead
        dot_g.write(filename, prog="dot", format="jpeg")

        if fobj is not None:
            img = Image.open(filename)
            try:
                if no_display:
                    return img
            finally:
                fobj.close()

            try:
                shell = get_ipython().__class__.__name__
                if shell == "ZMQInteractiveShell":
                    display(img)
                else:
                    plt.imshow(img, interpolation="antialiased")
                    plt.show()
            except NameError:
                plt.imshow(img, interpolation="antialiased")
                plt.show()
            finally:
                fobj.close()

    def print(self, colorful: bool = True, indent=4, _cache={}):
        if colorful and "init_colorama" not in _cache:
            init()
            _cache["init_colorama"] = True

        def fmt_node(node: Node):
            if isinstance(node, ClassNode):
                lbl = f"{node.id}"
            elif isinstance(node, DataNode):
                lbl = f"col-{node.col_index}"
            elif isinstance(node, LiteralNode):
                lbl = f"value:{node.value}"
            return f"{Back.BLUE}{Fore.BLACK}{lbl}{Style.RESET_ALL}"

        fmt_edge = lambda id: f"{Back.GREEN}{Fore.BLACK}{id}{Style.RESET_ALL}"
        """Print the semantic model, assuming it is a tree"""
        roots = [n for n in self.iter_nodes() if self.in_degree(n.id) == 0]
        for root in roots:
            print(f"\n---")
            stack: List[Tuple[int, Optional[Edge], Node]] = [(0, None, root)]
            while len(stack) > 0:
                depth, edge, node = stack.pop()
                tab = " " * depth * indent
                if edge is None:
                    print(f"{tab}[{fmt_node(root)}] {root.label}")
                else:
                    print(
                        f"{tab}-({fmt_edge(edge.label)})-> [{Back.BLUE}{Fore.BLACK}{fmt_node(node)}{Style.RESET_ALL}] {node.label}"
                    )

                for edge in self.out_edges(node.id):
                    target = self.get_node(edge.target)
                    stack.append((depth + 1, edge, target))
