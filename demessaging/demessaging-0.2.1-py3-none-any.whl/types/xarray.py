"""Custom types for the validation of backend module routines."""
from typing import Union

import xarray as xr

from demessaging.config import registry
from demessaging.types import TypeMixinSlots


class DataArray(xr.DataArray, TypeMixinSlots):
    # an extension of the common :class:`xarray.DataArray` with the necessary
    # classmethods for pydantic

    __slots__ = ()

    __doc__ = xr.DataArray.__doc__

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict):
            return xr.DataArray.from_dict(v)
        elif isinstance(v, str):
            return xr.open_dataarray(v.encode("utf-8"))
        elif isinstance(v, bytes):
            return xr.open_dataarray(v)
        else:
            return xr.DataArray(v)


class Dataset(xr.Dataset, TypeMixinSlots):

    __slots__ = ()

    __doc__ = xr.Dataset.__doc__

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict):
            return xr.Dataset.from_dict(v)
        elif isinstance(v, str):
            return xr.open_dataset(v.encode("utf-8"))
        elif isinstance(v, bytes):
            return xr.open_dataset(v)
        else:
            return xr.Dataset(v)


def encode_xarray(obj: Union[xr.DataArray, xr.Dataset]) -> bytes:
    return obj.to_netcdf()  # type: ignore


registry.register_import("demessaging.types.xarray")

for _cls in [DataArray, xr.DataArray, Dataset, xr.Dataset]:
    registry.register_encoder(_cls, encode_xarray)
