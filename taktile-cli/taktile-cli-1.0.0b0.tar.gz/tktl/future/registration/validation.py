import typing as t
from functools import singledispatch

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from .exceptions import ValidationError


@singledispatch
def validate(
    value: t.Union[np.ndarray, pd.DataFrame, pd.Series],
    *,
    sample: t.Union[np.ndarray, pd.DataFrame, pd.Series],
    minimal_subset: t.Optional[t.Set[str]] = None,
) -> t.Union[np.ndarray, pd.DataFrame, pd.Series]:
    raise ValidationError(f"Can't validate value of type: {type(value)}")


@validate.register
def _validate_numpy(
    value: np.ndarray,
    *,
    sample: t.Union[np.ndarray, pd.DataFrame, pd.Series],
    minimal_subset: t.Optional[t.Set[str]] = None,
) -> np.ndarray:
    if type(value) != type(sample):
        raise ValidationError(
            f"Expected value of type {type(sample)}, got {type(value)}"
        )

    if value.shape[1:] != sample.shape[1:]:
        raise ValidationError(
            "Could not validate numpy array shape. "
            f"Value has shape {value.shape[1:]}, expected shape: {sample.shape[1:]}"
        )

    # We choose not to validate the dtypes here

    return value


@validate.register
def _validate_series(
    value: pd.Series,
    *,
    sample: t.Union[np.ndarray, pd.DataFrame, pd.Series],
    minimal_subset: t.Optional[t.Set[str]] = None,
) -> pd.Series:
    if type(value) != type(sample):
        raise ValidationError(
            f"Expected value of type {type(sample)}, got {type(value)}"
        )

    # We choose not to validate the dtypes here

    return value


@validate.register
def _validate_dataframe(
    value: pd.DataFrame,
    *,
    sample: t.Union[np.ndarray, pd.DataFrame, pd.Series],
    minimal_subset: t.Optional[t.Set[str]] = None,
) -> pd.DataFrame:
    if not isinstance(sample, pd.DataFrame):
        raise ValidationError(
            f"Expected value of type {type(sample)}, got {type(value)}"
        )

    # We choose not to validate the dtypes here

    def decode(x: t.Union[str, bytes]) -> str:
        if isinstance(x, bytes):
            return x.decode()
        return x

    value.columns = [decode(x) for x in value.columns]

    sent_columns = {x for x in value.columns.to_list()}  # type: ignore
    expected_columns = {x for x in sample.columns.to_list()}  # type: ignore

    if minimal_subset is None:
        if sent_columns != expected_columns:
            missing = expected_columns.difference(sent_columns)
            superfluous = sent_columns.difference(expected_columns)
            raise ValidationError(
                "Column mismatch: " f"Missing columns: {missing} "
                if missing
                else "" f"Superfluous columns: {superfluous}"
                if superfluous
                else ""
            )
    else:
        if not sent_columns.issubset(expected_columns):
            raise ValidationError(
                "Column mismatch: "
                f"Superfluous columns: {sent_columns.difference(expected_columns)}."
            )
        if not minimal_subset.issubset(sent_columns):
            raise ValidationError(
                "Column mismatch: "
                f"Missing columns: {minimal_subset.difference(sent_columns)}."
            )
        sample = sample[value.columns]

    value = value[sample.columns.to_list()]  # type: ignore # ordering
    return value.astype(sample.dtypes.to_dict())  # type: ignore # dtypes. TODO: Improve this
