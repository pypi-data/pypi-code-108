"""This plugin is modelled on jsonpickles extensions.

Instead of saving pandas DataFrames to json they are saved to either CSV or HDF files.
"""

from typing import Literal, Type
import jsonpickle as jp
from jsonpickle.handlers import BaseHandler, register, unregister
import jsonpickle.ext.pandas as jpxpd

import pandas as pd

from .file import BaseFileHandler
from .numpy import register_handlers as register_numpy_handlers

__all__ = ["register_handlers", "unregister_handlers"]


class PandasDataFrameHandler(BaseHandler, BaseFileHandler):
    def __init__(
        self, archive_handler, mode: Literal["csv", "h5"] = "csv", write_kwargs=None
    ):

        if mode == "h5" and archive_handler._archive_type != "directory":
            raise ValueError("Cannot use hdf store on non-directory archives.")

        BaseFileHandler.__init__(self, archive_handler)
        self._mode = mode
        self._write_kwargs = write_kwargs

    def get_file_id(self):
        return self.get_uuid() + f".{self._mode}"

    def flatten(self, obj, data):

        data["file_uuid"] = self.get_file_id()
        data["shape"] = obj.shape
        data["mode"] = self._mode

        dtype = obj.dtypes.to_dict()

        data["dtypes"] = self.context.flatten(
            {k: str(dtype[k]) for k in dtype}, reset=False
        )
        data["index"] = jp.encode(obj.index)
        data["column_level_names"] = obj.columns.names
        data["header"] = list(range(len(obj.columns.names)))

        if not self._write_kwargs:
            data["write_kwargs"] = {}
        else:
            data["write_kwargs"] = self._write_kwargs

        if self._mode == "csv":
            with self._ah.open_file(data["file_uuid"], mode="w") as open_file:
                obj.to_csv(open_file, **data["write_kwargs"], index=False)

        elif self._mode == "h5":
            kwargs = dict(format="table")
            kwargs.update(data["write_kwargs"])
            obj.to_hdf(
                self._ah.path / data["file_uuid"],
                "dataicer_data",
                **kwargs,
            )

        return data

    def restore(self, data):

        mode = data["mode"]
        dtypes = data["dtypes"]
        index = jp.decode(data["index"])
        column_level_names = data["column_level_names"]

        if mode == "csv":
            with self._ah.open_file(data["file_uuid"], mode="r") as open_file:
                df = pd.read_csv(open_file)

            for key, dtype in dtypes.items():
                df[key] = df[key].astype(dtype=dtype)

        elif mode == "h5":
            df = pd.read_hdf(self._ah.path / data["file_uuid"])
        return df


def register_handlers(
    archive_handler: Type[BaseFileHandler], mode: Literal["csv", "h5"] = "csv"
):
    register_numpy_handlers(archive_handler, mode="txt")
    register(
        pd.DataFrame, PandasDataFrameHandler(archive_handler, mode=mode), base=True
    )
    register(pd.Series, jpxpd.PandasSeriesHandler, base=True)
    register(pd.Index, jpxpd.PandasIndexHandler, base=True)
    register(pd.PeriodIndex, jpxpd.PandasPeriodIndexHandler, base=True)
    register(pd.MultiIndex, jpxpd.PandasMultiIndexHandler, base=True)
    register(pd.Timestamp, jpxpd.PandasTimestampHandler, base=True)
    register(pd.Period, jpxpd.PandasPeriodHandler, base=True)
    register(pd.Interval, jpxpd.PandasIntervalHandler, base=True)


def unregister_handlers():
    jpxpd.unregister_handlers()
