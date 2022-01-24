from collections import OrderedDict
from typing import Any, Dict, Iterator, List, Tuple, Union

from antlr4.tree.Tree import TerminalNode, Token, Tree
from triad.utils.assertion import assert_or_throw
from triad.utils.hash import to_uuid

from qpd.dataframe import DataFrame, DataFrames
from qpd._parser.sql import QPDSql
from qpd.constants import AGGREGATION_FUNCTIONS, JOIN_TYPES
from qpd.workflow import QPDWorkflow


class ColumnMention(object):
    def __init__(self, df_name: str, col_name: str):
        self.df_name = df_name
        self.col_name = col_name
        self.encoded = "_" + to_uuid(df_name, col_name).split("-")[-1]
        self.expr = df_name + "." + col_name

    def __repr__(self) -> str:
        return self.expr

    def __hash__(self) -> int:
        return hash((self.df_name, self.col_name))

    def __eq__(self, other: Any) -> bool:
        return self.df_name == other.df_name and self.col_name == other.col_name


class ColumnMentions(object):
    def __init__(self, *data: Any):
        self._data: Dict[ColumnMention, int] = OrderedDict()
        self.add(*data)

    def add(self, *data: Any) -> "ColumnMentions":
        for x in data:
            if isinstance(x, ColumnMention):
                self._data[x] = 1
            elif isinstance(x, ColumnMentions):
                self._data.update(x._data)
            elif isinstance(x, tuple):
                self._data[ColumnMention(x[0], x[1])] = 1
            else:
                raise ValueError(f"{x} is invalid")
        return self

    def __contains__(self, m: ColumnMention) -> bool:
        return m in self._data

    def __iter__(self) -> Iterator[ColumnMention]:
        return iter(self._data.keys())

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return ",".join(x.__repr__() for x in self)

    @property
    def single(self) -> ColumnMention:
        assert_or_throw(len(self._data) == 1, f"multiple mentions: {self._data}")
        return next(iter(self._data.keys()))


class Join(object):
    def __init__(
        self,
        df_name: str,
        df: DataFrame,
        join_type: str = "",
        natural: bool = False,
        criteria_context: Any = None,
    ):
        self.df_name = df_name
        self.df = df
        self.join_type = join_type
        self.natural = natural
        self.criteria_context = criteria_context
        self.conditions: List[Any] = []

    def set_conditions(self, cond: List[Any]):
        self.conditions = cond


class VisitorContext(object):
    def __init__(self, *args: Any, **kwargs: Any):
        self._data: Dict[str, Any] = {}
        for v in args:
            if isinstance(v, VisitorContext):
                # self._data.update(v._data)
                self._data = v._data
            elif isinstance(v, Dict):
                self._data.update(v)
            else:
                raise ValueError(f"{v} is invalid")
        self._data.update(kwargs)
        if "node_to_token" not in self._data:
            self._data["node_to_token"] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    @property
    def workflow(self) -> QPDWorkflow:
        return self._data["workflow"]

    @property
    def sql(self) -> QPDSql:
        return self._data["sql"]

    @property
    def current(self) -> DataFrame:
        return self._data["current"]

    def update_current(self, df: DataFrame) -> DataFrame:
        self._data["current"] = df
        return df

    @property
    def dfs(self) -> DataFrames:
        return self._data["dfs"]

    def add_column_mentions(self, ctx: Any) -> ColumnMentions:
        if "col_mentions" in self._data and id(ctx) in self._data["col_mentions"]:
            return self.get_column_mentions(ctx)
        expr = self.to_str(ctx, "")
        assert_or_throw(expr != "*", ValueError("'*' shouldn't be used here"))
        mentions = ColumnMentions(*self.dfs._resolver.get_cols(expr))
        if "col_mentions" not in self._data:
            self._data["col_mentions"] = {id(ctx): mentions}
        else:
            self._data["col_mentions"][id(ctx)] = mentions
        if "all_mentions" not in self._data:
            self._data["all_mentions"] = ColumnMentions()
        self._data["all_mentions"].add(mentions)
        return mentions

    def get_column_mentions(self, ctx: Any) -> ColumnMentions:
        return self._data["col_mentions"][id(ctx)]  # type:ignore

    @property
    def all_column_mentions(self) -> ColumnMentions:
        v = self._data.get("all_mentions", None)
        if v is None:
            return ColumnMentions()
        return v

    def add_join_relation(self, join: Join) -> None:
        if "joins" not in self._data:
            self._data["joins"] = []
        for j in self._data["joins"]:
            assert_or_throw(
                j.df_name != join.df_name,
                ValueError(f"{join.df_name} is already in join line"),
            )
        self._data["joins"].append(join)

    @property
    def joins(self) -> List[Join]:
        return self.get("joins", [])

    def set_col_encoded(self) -> None:
        return self.set("col_encoded", True)

    @property
    def col_encoded(self) -> bool:
        return self.get("col_encoded", False)

    def ctx_to_col_names(self, ctx: Any) -> List[str]:
        expr = self.to_str(ctx, "")
        cols = self.dfs.name_resolver.get_cols(expr)
        if self.col_encoded:
            return [self._obj_to_col_name(x) for x in cols]
        else:
            return [x[0] + "." + x[1] for x in cols]

    def to_str(self, node: Union[Tree, Token, str, None], delimit: str = " ") -> str:
        if isinstance(node, str):
            return node
        if node is None:
            return ""
        return delimit.join(
            self._get_node_str(node, self._data["node_to_token"])[1]
        ).rstrip(" ")

    def expr(self, node: Union[Tree, Token, None]) -> str:
        return self.to_str(node, " ")

    def _obj_to_col_name(self, obj: Any):
        return "_" + to_uuid(obj).split("-")[-1]

    def _get_node_str(
        self, node: Union[Tree, Token], cache: Dict[int, Tuple[Token, List[str]]]
    ) -> Tuple[Token, List[str]]:
        if id(node) in cache:
            return cache[id(node)]
        elif isinstance(node, Token):
            res = (node, [self.sql.raw_code[node.start : node.stop + 1]])
        elif isinstance(node, TerminalNode):
            res = self._get_node_str(node.getSymbol(), cache)
        else:
            strs: List[str] = []
            first: Any = None
            for i in range(node.getChildCount()):
                t, arr = self._get_node_str(node.getChild(i), cache)
                if first is None:
                    first = t
                strs += arr
            res = (first, strs)
        cache[id(node)] = res
        return res


def normalize_join_type(join_type: str) -> str:
    orig = join_type
    join_type = "_".join(x for x in join_type.strip().lower().split(" ") if x != "")
    if join_type == "" or join_type == "_":
        return "inner"
    if join_type in ["left", "right", "full"]:
        return join_type + "_outer"
    if join_type in ["semi", "anti"]:
        return "left_" + join_type
    assert_or_throw(join_type in JOIN_TYPES, ValueError(f"{orig} is invalid"))
    return join_type


def is_agg(func: str) -> bool:
    return func.lower() in AGGREGATION_FUNCTIONS
