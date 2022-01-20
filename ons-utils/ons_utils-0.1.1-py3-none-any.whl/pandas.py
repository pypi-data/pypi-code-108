"""A set of helper functions in pandas."""
from typing import Callable
import pandas as pd
from flatten_dict import flatten

from .generic import fill_tuple_keys


def nested_dict_to_df(
    d: dict,
    columns: list = None,
    level_names: list = None,
) -> pd.DataFrame:
    """Flattens a nested dict and converts to a DataFrame with MultiIndex."""
    # Level of nesting may vary, this standardises the length.
    new_d = fill_tuple_keys(flatten(d), fill_method='ffill')
    idx = pd.MultiIndex.from_tuples(new_d.keys(), names=level_names)
    return pd.DataFrame(new_d.values(), index=idx, columns=columns)


class Stacker():
    """Provides methods to stack and unstack a tidy DataFrame."""

    def __init__(
        self,
        value_cols: list,
        index_cols: list,
        transpose: bool = False,
    ):
        """Init the stacker.

        value_cols: those unaffected by the stacking operation
        index_cols: the cols to keep as the key axis
        transpose: whether to transpose the resulting dataframe
            default is the index is set as columns
        """
        self.value_cols = value_cols
        self.index_cols = index_cols
        self.transpose = transpose

    def unstack(self, df):
        """Set all but value_cols as index, then unstacks index_cols."""
        # Save the column order for the stacking
        self.all_cols = df.columns

        set_cols = [col for col in df.columns if col not in self.value_cols]

        df = df.set_index(set_cols)
        unstacked_df = df.unstack(self.index_cols)

        if self.transpose:
            unstacked_df = unstacked_df.T

        return unstacked_df

    def stack(self, df):
        """Stacks index_cols back to the index and resets index with
        same column order.
        """
        if self.transpose:
            df = df.T

        stacked_df = df.stack(self.index_cols)
        return stacked_df.reset_index()[self.all_cols]


def convert_level_to_datetime(df, level, axis=0):
    """Convert the given level of a MultiIndex to DateTime."""
    # Get a new list of levels with those defined by level converted
    # to datetime
    new_levels = [
        pd.to_datetime(df.axes[axis].levels[i]) if name == level
        else df.axes[axis].levels[i]
        for i, name in enumerate(df.axes[axis].names)
    ]

    # Create a new MultiIndex from the levels and set as axis
    new_idx = df.axes[axis].set_levels(new_levels)
    return df.set_axis(new_idx, axis=axis)


class MultiIndexSlicer:
    """Provides a method to return a MultiIndex slice on the levels given
    in the instance.
    """

    def __init__(self, df, levels, axis=0):
        """
        levels: the MultiIndex levels to build a slice generator for
        axis: The axis for the MultiIndex to slice on
        """
        self.levels = levels
        self.df = df
        self.axis = axis

    def get_slicer(self, *args):
        """Return a MultiIndex slice for the given args."""
        if len(args) != len(self.levels):
            return ValueError(
                f"len args must be same as len self.levels: {len(self.levels)}"
            )

        args = iter(args)

        return tuple([
          next(args) if name in self.levels
          else slice(None)
          for name in self.df.axes[self.axis].names
        ])


def get_index_level_values(df, levels, axis=0):
    """Return each combination of level values for given levels."""
    return list(
        df.axes[axis].to_frame()[levels]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )


def shifted_within_year_apply(
    df: pd.DataFrame,
    method: Callable[[pd.DataFrame], pd.DataFrame],
    axis: int = 0,
) -> pd.DataFrame:
    """Apply the given method within year for Feb-Jan+1 timespan."""
    return (
        df
        .shift(-1, axis=axis)
        .groupby(lambda x: x.year, axis=axis)
        .apply(method)
        .shift(1, axis=axis)
    )


def shifted_within_year_ffill(df: pd.DataFrame, axis: int = 0) -> pd.DataFrame:
    """Forward fill within year for Feb-Jan+1 timespan."""
    return shifted_within_year_apply(df, lambda x: x.ffill(), axis)
