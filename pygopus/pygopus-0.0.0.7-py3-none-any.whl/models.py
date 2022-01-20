from typing import List, MutableSequence, Optional, Tuple, Literal, Union, Any
from .service import HighLight, SetCells
from .utils import int_to_colname
from collections import UserList


class Axis:

    pos: Tuple[int, int]  # x,y -> col,row

    def __init__(self, x: int, y: int) -> None:
        x = x if x > 0 else 1
        y = y if y > 0 else 1

        self.pos = (x, y)

    def skip(self, x, y):
        col, row = self.pos
        self.axis = Axis(col + x, row + y)
        return self

    def __repr__(self):
        return self.name()

    def __str__(self):
        return self.name()

    def name(self):
        col, row = self.pos

        return f"{int_to_colname(col)}{row}"

    def down(self):
        col, row = self.pos
        return Axis(col, row + 1)

    def up(self):
        col, row = self.pos
        return Axis(col, row - 1)

    def down_seq(self, length: int):  # not contain self axis
        col, row = self.pos
        return [Axis(col, row + i + 1) for i in range(length)]

    def right(self):
        col, row = self.pos
        return Axis(col + 1, row)

    def left(self):
        col, row = self.pos
        return Axis(col - 1, row)

    def right_seq(self, length: int):  # not contain self axis
        col, row = self.pos
        return [Axis(col + i + 1, row) for i in range(length)]


class Figure(UserList):
    _pid: int
    # _skip: Optional[Tuple[int, int]]
    axis: Axis
    sheet_name: str

    def __init__(self, initlist: MutableSequence[Any]) -> None:
        super().__init__(initlist)

    @property
    def cells(self) -> Tuple[Axis]:
        _res = []

        if type(self).__name__ == "Row":
            axs = [self.axis] + self.axis.right_seq(len(self.data) - 1)
            # _res = [a.name() for a in axs]
            _res = [a for a in axs]

        if type(self).__name__ == "Col":
            axs = [self.axis] + self.axis.down_seq(len(self.data) - 1)
            # _res = [a.name() for a in axs]
            _res = [a for a in axs]
        return tuple(_res)

    def dict(self):
        return {k: v for k, v in zip(self.cells, self.data)}

    def info(self, pos: Tuple[int, int], pid: int, sheet_name: str):
        self._pid = pid
        self.sheet_name = sheet_name
        self.axis = Axis(*pos)
        return self

    def highlight(self, color: str = "#FEF9B0", at: Union[int, List[int]] = None):

        _color = [color]
        at = [at] if isinstance(at, int) else at
        targets = [str(c) for c in self.cells] if at == None else [str(self.cells[i]) for i in at]
        # targets = self.cells if at == None else [self.cells[at]]

        res = HighLight(
            pid=self._pid,
            sheet_name=self.sheet_name,
            tar_type="row",
            targets=targets,
            color=_color,
        ).post()

        return res


class Row(Figure):
    def next_row_start_axis(self):
        return self.axis.down()

    def next_row_cells_axis(self):
        next_start_axis = self.axis.down()
        return [next_start_axis] + next_start_axis.right_seq(len(self.data) - 1)

    def prev_row_start_axis(self):
        return self.axis.up()


class Col(Figure):
    def next_col_start_axis(self):
        return self.axis.right()

    def next_col_cells_axis(self):
        next_start_axis = self.axis.right()
        return [next_start_axis] + next_start_axis.down_seq(len(self.data) - 1)

    def prev_col_start_axis(self):
        return self.axis.left()


class FigureContainer(UserList):
    _pid: int
    sheet_name: str

    def get_last_one(self) -> Optional[Figure]:
        return self.data[-1] if self.data else None

    def dict(self, reset_key: Tuple[int, int] = None, cells_as_key=False):

        if reset_key:
            x, y = reset_key
            # Not only row also co
            return {Axis(x, y + i): row for i, row in enumerate(self.data)}
        if cells_as_key:
            return {row.cells: row for row in self.data}

        return {row.axis: row for row in self.data}

    def info(self, sheet_name: str, pid: int):
        self._pid = pid
        self.sheet_name = sheet_name
        return self

    def _set_operation(self, type, other, look_at):
        raise NotImplementedError

    def intersection(self, other, look_at) -> List[Row]:
        return self._set_operation(
            type="inter",
            other=other,
            look_at=look_at,
        )

    def difference(self, other, look_at):
        return self._set_operation(
            type="diff",
            other=other,
            look_at=look_at,
        )


class _RowContainer(FigureContainer):
    data: List[Row]

    def __iter__(self):

        return self.data.__iter__()

    def append(self, item: MutableSequence[Any]):
        # should be Union[MutableSequence[Any],Row]

        last_row_axis = self.data[-1].axis if self.data else None
        next_row_axis = last_row_axis.down() if last_row_axis else Axis(1, 1)

        # next_row_cells_axis = [last_one.axis] + last_one.axis.right_seq(len(item) + 1)
        next_row_cells_axis = [next_row_axis] + next_row_axis.right_seq(len(item) - 1)
        cells_map = {str(key): [v] for key, v in zip(next_row_cells_axis, item)}
        res = SetCells(
            pid=self._pid,
            sheet_name=self.sheet_name,
            cells_map=cells_map,
        ).post()
        row = Row(item).info(
            pid=self._pid,
            pos=next_row_axis.pos,
            sheet_name=self.sheet_name,
        )

        self.data.append(row)
        # can be improved here:
        # make a limited list < 100
        # then append list when it get full

    def _set_operation(
        self,
        type: Literal["inter", "diff"],
        other: "_RowContainer",
        look_at: Union[int, Tuple[int, int]],
    ) -> List[Row]:

        # self_match_col = []
        # other_match_col = []

        look_at = look_at if isinstance(look_at, tuple) else (look_at, look_at)
        self_look_at, other_look_at = look_at
        # self_match_col = {row.cells[self_look_at]: row.data[self_look_at] for row in self.data}
        # other_match_col = {row.cells[other_look_at]: row.data[other_look_at] for row in other.data}
        self_match_row_axis = {row.cells[0]: row.data[self_look_at] for row in self.data}
        other_match_row_axis = {row.cells[0]: row.data[other_look_at] for row in other.data}

        _res = []
        if type == "inter":
            # _res = [k for k, v in self_match_col.items() if v in other_match_col.values()]
            _res = [self.dict()[k] for k, v in self_match_row_axis.items() if v in other_match_row_axis.values()]

        if type == "diff":
            # _res = [k for k, v in self_match_col.items() if v not in other_match_col.values()]
            _res = [self.dict()[k] for k, v in self_match_row_axis.items() if v not in other_match_row_axis.values()]

        return _res


class _ColContainer(FigureContainer):
    data: List[Col]

    def __iter__(self):
        return self.data.__iter__()

    def append(self, item: MutableSequence[Any]):
        last_col_axis = self.data[-1].axis if self.data else None
        next_col_axis = last_col_axis.right() if last_col_axis else Axis(1, 1)
        next_col_cells_axis = [next_col_axis] + next_col_axis.down_seq(len(item) - 1)
        cells_map = {str(key): [v] for key, v in zip(next_col_cells_axis, item)}
        res = SetCells(
            pid=self._pid,
            sheet_name=self.sheet_name,
            cells_map=cells_map,
        ).post()
        col = Col(item).info(
            pid=self._pid,
            pos=next_col_axis.pos,
            sheet_name=self.sheet_name,
        )

        self.data.append(col)
        return
