from logging import setLogRecordFactory
from .models import _ColContainer, Col, Row, _RowContainer
from typing import Any, List, Tuple, Union
from dataclasses import dataclass
from random import sample

from .service import *
from path import Path
import pkg_resources
import subprocess
import platform
import httpx
import os


HOST = "http://127.0.0.1"
FOLDER = platform.system()
if not FOLDER:
    raise Exception("Unknown OS")

BIN = pkg_resources.resource_filename(
    "pygopus",
    Path(f"/bin/{FOLDER}/pygobin"),
)


if platform.system() == "Windows":
    BIN = pkg_resources.resource_filename(
        "pygopus",
        Path(f"/bin/{FOLDER}/pygobin.exe"),
    )

service_pool = {}
ports = sample(range(55535, 65535), 10000)


def check_path(path: str):
    p = Path(path)
    if not p.exists():
        raise Exception(f"{ path } is not exists.Please check carefully")


def create_workbook(path: str):
    import shutil

    tpl = pkg_resources.resource_filename(
        "pygopus",
        Path("/bin/tpl.xlsx"),
    )
    shutil.copyfile(tpl, Path(path))


@dataclass
class XlInfo:
    pid: int
    port: int
    file_name: str


class WorkBook:
    @classmethod
    def open(cls, paths: List[str]):
        return [cls(p) for p in paths]

    def __init__(
        self,
        path: str,
        write_mode="",
        debug=False,
    ) -> None:
        # check file here
        if write_mode != "w+":
            # means user want create, so you gotta if file exists.
            check_path(path)

        else:
            create_workbook(path)
            print(f"{path} file created.")

        port = ports.pop()
        pygo_bin = Path(BIN)
        mode = os.stat(pygo_bin).st_mode | 0o100
        pygo_bin.chmod(mode)

        # if os.environ.get("code_platform") != "linux":
        # pygo_bin.chmod(mode)
        # only wroks on 云课堂 docker, well we dont need this anymore

        cmd = f"{BIN} -path {path} -port {port}".split()
        kwd = {}
        import tempfile

        out_temp = tempfile.SpooledTemporaryFile(max_size=100 * 100)

        if debug:
            ...
        else:
            kwd = dict(
                stdout=out_temp.fileno(),
                stderr=out_temp.fileno(),
            )

        # p = subprocess.Popen(args=cmd, **kwd)
        _kwd = {"args": cmd, **kwd}

        p = subprocess.Popen(**_kwd)
        # _ = p.poll()
        self._pid = p.pid
        self.file_name = str(Path(path).abspath())

        info = XlInfo(
            pid=self._pid,
            port=port,
            file_name=self.file_name,
        )
        service_pool.update({self._pid: info})

        while True:
            try:
                res = Hello(pid=self._pid).get()
                break
            except httpx.ConnectError as e:
                if debug:
                    print("Waiting for starting server.")

    def __repr__(self):
        return f"<pygopus.WorkBook at='{self.file_name}'>"

    def __len__(self):
        return len(self.sheets)

    def __getitem__(self, k):
        sheets = {sh.name: sh for sh in self.sheets}
        return sheets[k]

    def __setitem__(self, k: str, v: "Sheet"):
        ...

    def get_sheet(self, name: str):
        try:
            return self[name]
        except KeyError:
            raise Exception(f"there's no sheet named {name}")

    def add(self, name: str):
        res = AddSheet(
            pid=self._pid,
            sheet_name=name,
        ).get()
        return "ok"

    def delete(self, name: str):
        DeleteSheet(
            pid=self._pid,
            sheet_name=name,
        ).get()
        return "ok"

    @property
    def sheets(self):
        res = GetSheets(pid=self._pid).get()
        return [
            Sheet(
                index,
                name,
                pid=self._pid,
            )
            for index, name in res.items()
        ]

    def save(self):
        Save(pid=self._pid).get()

    def save_as(self, path: str):
        SaveAs(pid=self._pid, path=path).get()

    def close(self):
        # import psutil

        # ps = psutil.Process(self._pid)
        # ps.terminate()
        # ps.kill()
        return Close(pid=self._pid).get()


class Sheet:
    def __init__(
        self,
        index: int,
        name: str,
        pid: int,
        skip: Tuple[int, int] = (0, 0),
    ) -> None:
        self.name = name
        self._index = index
        self._pid = pid
        self._rows = _RowContainer()
        self._cols = _ColContainer()
        self._col_offset = None
        self._row_offset = None
        self._head = None

    def __setitem__(self, k, v):
        self.set(k, v)

    def __getitem__(self, k):
        ...

    def __repr__(self):
        return f"<pygopus.Sheet name='{self.name}'>"

    @property
    def head(self):
        return self._head if self._head else self.rows[0]

    @head.setter
    def head(self, other: List):
        ...

    @property
    def body(self):
        ...

    def get_rows(self) -> _RowContainer:
        res = GetRows(
            sheet_name=self.name,
            pid=self._pid,
        ).get()

        return _RowContainer(
            [
                Row(r).info(
                    pid=self._pid,
                    pos=(0, i + 1),
                    sheet_name=self.name,
                )
                for i, r in enumerate(res)
            ]
        ).info(sheet_name=self.name, pid=self._pid)

    @property
    def rows(self) -> _RowContainer:
        if self._rows:
            return self._rows

        rows = self.get_rows()
        self._rows = rows

        return self._rows

    def get_cols(self):
        res = GetCols(
            pid=self._pid,
            sheet_name=self.name,
        ).get()

        return _ColContainer(
            [
                Col(c).info(
                    sheet_name=self.name,
                    pid=self._pid,
                    pos=(i + 1, 0),
                )
                for i, c in enumerate(res)
            ]
        ).info(sheet_name=self.name, pid=self._pid)

    @property
    def cols(self):

        if self._cols:
            return self._cols

        _res = self.get_cols()
        self._cols = _res

        return self._cols

    def get(self, axis: str):

        res = GetCell(
            pid=self._pid,
            sheet_name=self.name,
            axis=axis,
        ).get()
        return res

    def set(self, axis: str, val: Any):

        res = SetCell(
            pid=self._pid,
            sheet_name=self.name,
            axis=axis,
            val=val,
        ).get()
        return res

    def batch_set(self, *args, data: List):

        for index, axis in enumerate(args):
            res = SetCell(
                pid=self._pid,
                sheet_name=self.name,
                axis=axis,
                val=data[index],
            ).get()
        return "ok"

    def write_rows(self, data: Union[List, _RowContainer], start_at=(1, 1)):
        # rows = {f"{start_at}{index+1}": d for index, d in enumerate(data)}

        rows = (
            _RowContainer([Row(d).info(pid=self._pid, sheet_name=self.name, pos=start_at) for d in data])
            if isinstance(data, List)
            else data
        )
        res = WriteRows(
            pid=self._pid,
            sheet_name=self.name,
            # rows=rows,
            rows=rows.dict(reset_key=start_at),
        ).post()

        return res

    def delete_row(self, row_axis: int):
        res = DeleteRow(
            pid=self._pid,
            sheet_name=self.name,
            row_axis=row_axis,
        ).get()
        return

    def flush(self):
        ...

    # contains gt lt eq
    def find(
        self,
        val: str = "",
        regex: str = "",
    ):
        ...

    def option(self):
        ...
