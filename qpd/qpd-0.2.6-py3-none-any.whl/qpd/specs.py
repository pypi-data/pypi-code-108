from typing import Any, Dict, Iterator, List, Set, no_type_check

from triad.utils.assertion import assert_or_throw
from triad.utils.hash import to_uuid

from qpd.constants import AGGREGATION_FUNCTIONS, WINDOW_FUNCTIONS


class SpecBase(object):
    def __init__(self, name: str, **kwargs: Any):
        self._name = name
        self._metadata: Dict[str, Any] = kwargs
        self._uuid = to_uuid(str(type(self)), self._name, self._metadata)

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return (self._name, self._metadata).__repr__()

    def __uuid__(self) -> str:
        return self._uuid

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other) and self._uuid == other._uuid

    def __hash__(self) -> int:
        return hash(self._uuid)


class ArgumentSpec(SpecBase):
    def __init__(self, is_col: bool, value: Any):
        super().__init__("", is_col=is_col, value=value)

    @property
    def is_col(self) -> bool:
        return self._metadata["is_col"]

    @property
    def value(self) -> Any:
        return self._metadata["value"]


class OrderItemSpec(SpecBase):
    def __init__(self, name, asc: bool = True, na_position="auto"):
        if na_position == "auto":
            pd_na_position = "first" if asc else "last"
        elif na_position in ["first", "last"]:
            pd_na_position = na_position
        else:
            raise ValueError(f"{na_position} is invalid")
        super().__init__(
            name, asc=asc, na_position=na_position, pd_na_position=pd_na_position
        )

    @property
    def asc(self) -> bool:
        return self._metadata["asc"]

    @property
    def na_position(self) -> str:
        return self._metadata["na_position"]

    @property
    def pd_na_position(self) -> str:
        return self._metadata["pd_na_position"]


class OrderBySpec(SpecBase):
    @no_type_check
    def __init__(self, *items: List[Any]):
        data: List[OrderItemSpec] = []
        names: Set[str] = set()
        first_ct, last_ct = 0, 0
        for i in items:
            if not isinstance(i, OrderItemSpec):
                if isinstance(i, str):
                    i = OrderItemSpec(i)
                else:
                    i = OrderItemSpec(*list(i))
            assert_or_throw(i.name not in names, ValueError(f"{i.name} already exists"))
            names.add(i.name)
            if i.pd_na_position == "first":
                first_ct += 1
            else:
                last_ct += 1
            data.append(i)
        pd_na_position = "last" if last_ct == len(data) else "first"
        super().__init__("", items=data, pd_na_position=pd_na_position)

    @property
    def items(self) -> List[OrderItemSpec]:
        return self._metadata["items"]

    @property
    def keys(self) -> List[str]:
        return [x.name for x in self]

    @property
    def asc(self) -> List[bool]:
        return [x.asc for x in self]  # type: ignore

    @property
    def pd_na_position(self) -> str:
        return self._metadata["pd_na_position"]

    def __iter__(self) -> Iterator[OrderItemSpec]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)


class PreciateSpec(SpecBase):
    def __init__(self, name: str, positive: bool, **kwargs: Any):
        super().__init__(name, positive=positive, **kwargs)

    @property
    def positive(self) -> bool:
        return self._metadata["positive"]


class IsValueSpec(PreciateSpec):
    def __init__(self, value_expr: str, positive: bool):
        super().__init__(name=value_expr.lower(), positive=positive)

    @property
    def value_expr(self) -> str:
        return self.name


class IsInSpec(PreciateSpec):
    def __init__(self, mode: str, positive: bool, *values: ArgumentSpec):
        mode = mode.lower()
        assert_or_throw(mode in ["in", "between"], ValueError(mode))
        super().__init__(name=mode, positive=positive, values=values)

    @property
    def is_between(self) -> bool:
        return self.name.lower() == "between"

    @property
    def values(self) -> List[ArgumentSpec]:
        return self._metadata["values"]


class FunctionSpec(SpecBase):
    def __init__(self, name: str, unique: bool, dropna: bool, **kwargs: Any):
        super().__init__(name, unique=unique, dropna=dropna, **kwargs)

    @property
    def unique(self) -> bool:
        return self._metadata["unique"]

    @property
    def dropna(self) -> bool:
        return self._metadata["dropna"]


class AggFunctionSpec(FunctionSpec):
    def __init__(self, name: str, unique: bool, dropna: bool):
        assert_or_throw(
            name in AGGREGATION_FUNCTIONS,
            ValueError(f"{name} is not an aggregation function"),
        )
        super().__init__(name, unique=unique, dropna=dropna)


class WindowFrameSpec(SpecBase):
    def __init__(self, frame_type: str, start: Any = None, end: Any = None):
        super().__init__(frame_type, start=start, end=end)

    @property
    def start(self) -> Any:
        return self._metadata["start"]

    @property
    def end(self) -> Any:
        return self._metadata["end"]


class NoWindowFrame(WindowFrameSpec):
    def __init__(self):
        super().__init__("")


class RollingWindowFrame(WindowFrameSpec):
    def __init__(self, start: Any, end: Any):
        super().__init__("rolling", start=start, end=end)
        window = None if start is None or end is None else end - start + 1
        self._metadata["window"] = window
        assert_or_throw(
            self.window is None or self.window > 0, ValueError(f"invalid {start} {end}")
        )

    @property
    def window(self) -> int:
        return self._metadata["window"]


def make_windowframe_spec(
    frame_type: str, start: Any = None, end: Any = None
) -> WindowFrameSpec:
    frame_type = frame_type.lower()
    if frame_type == "":
        return NoWindowFrame()
    if frame_type == "rows":
        if isinstance(start, str):
            start = int(start)
        if isinstance(end, str):
            end = int(end)
        if start is None and end is None:
            return NoWindowFrame()
        return RollingWindowFrame(start, end)
    raise NotImplementedError(frame_type)


class WindowSpec(SpecBase):
    def __init__(
        self,
        name: str,
        partition_keys: List[str],
        order_by: OrderBySpec,
        windowframe: WindowFrameSpec,
    ):
        self._spec_uuid = to_uuid(partition_keys, order_by, windowframe)
        if name == "":
            name = "_" + self.spec_uuid.split("-")[-1]
        super().__init__(
            name,
            partition_keys=partition_keys,
            order_by=order_by,
            windowframe=windowframe,
        )

    @property
    def spec_uuid(self) -> str:
        return self._spec_uuid

    @property
    def partition_keys(self) -> List[str]:
        return self._metadata["partition_keys"]

    @property
    def order_by(self) -> OrderBySpec:
        return self._metadata["order_by"]

    @property
    def windowframe(self) -> WindowFrameSpec:
        return self._metadata["windowframe"]


class WindowFunctionSpec(FunctionSpec):
    def __init__(self, name: str, unique: bool, dropna: bool, window: WindowSpec):
        assert_or_throw(
            name in WINDOW_FUNCTIONS, ValueError(f"{name} is not an window function")
        )
        super().__init__(name, unique=unique, dropna=dropna, window=window)

    @property
    def window(self) -> WindowSpec:
        return self._metadata["window"]

    @property
    def has_windowframe(self) -> bool:
        return not isinstance(self.window.windowframe, NoWindowFrame)

    @property
    def has_partition_by(self) -> bool:
        return len(self.window.partition_keys) > 0

    @property
    def has_order_by(self) -> bool:
        return len(self.window.order_by) > 0
