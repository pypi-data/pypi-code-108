from functools import cached_property, wraps
from typing import Any, Dict, Literal, MutableSequence, Optional, List
from pydantic import BaseModel
import atexit
import httpx
from pydantic.class_validators import validator


def kill_go():
    import psutil

    for p in psutil.process_iter():
        if "pygobin" in p.name():
            proc = psutil.Process(p.pid)
            proc.terminate()


atexit.register(kill_go)


def auto_abort(func):
    @wraps(func)
    def instead(self, *args, **kwd):
        try:
            res = func(self, *args, **kwd)
            return res
        except httpx.ConnectError:
            raise
        except Exception as e:
            kill_go()
            raise e
        finally:
            ...

    return instead


exclude = {"api", "pid"}


class Service(BaseModel):
    pid: int

    class Config:
        # arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @auto_abort
    def get(self, data: dict = {}):
        d = self.dict(exclude=exclude)
        if data:
            d.update(data)
        res = httpx.get(self.api, params=d, timeout=None)
        if res == None:
            raise ValueError("Result not exist please check your arguments")
        return res.json()

    @auto_abort
    def post(self, data: dict = {}):
        d = {**self.dict(exclude=exclude), **data}
        res = httpx.post(self.api, json=d, timeout=None)
        if res == None:
            raise ValueError("Result not exist please check your arguments")

        return res.json()

    @cached_property
    def api(self):
        from .core import HOST, service_pool

        info = service_pool[self.pid]
        _api = self.schema()["title"]
        return f"{HOST}:{info.port}/{_api}"


class Hello(Service):
    ...


class Save(Service):
    ...


class SaveAs(Service):
    path: str


class Close(Service):
    ...


class HighLight(Service):
    sheet_name: str
    tar_type: Literal["row", "col", "cell"]
    targets: List[str]
    color: List[str] = ["#FEF9B0"]


class AddSheet(Service):
    sheet_name: str


class DeleteSheet(Service):
    sheet_name: str


# never use this ...
# class GetSheet(Service):
#     ...


class GetSheets(Service):
    ...


class GetRows(Service):
    sheet_name: str


class GetCols(Service):
    sheet_name: str


class DeleteCol(Service):
    sheet_name: str
    col_axis: str


class DeleteRow(Service):
    sheet_name: str
    row_axis: int


class WriteRows(Service):
    sheet_name: str
    rows: dict

    @validator("rows", pre=True)
    def rows_value_can_only_be_list(cls, rows: dict):
        # assert isinstance(rows, dict)
        return {str(k): v.data for k, v in rows.items()}  # value must be Row instance


class AppendRow(Service):
    sheet_name: str
    row: MutableSequence

    @validator("row", pre=True)
    def row_must_be_a_list(cls, row):
        return row.data


class AppendCol(Service):
    sheet_name: str
    col: MutableSequence

    @validator("col", pre=True)
    def col_must_be_a_list(cls, col):
        return col.data


class GetCell(Service):
    sheet_name: str
    axis: str


class SetCell(Service):
    sheet_name: str
    axis: str
    val: Any


class SetCells(Service):
    sheet_name: str
    cells_map: dict


class TotalCols(Service):
    sheet_name: str


class SearchCell(Service):

    val: str
    regex: Optional[str] = None
