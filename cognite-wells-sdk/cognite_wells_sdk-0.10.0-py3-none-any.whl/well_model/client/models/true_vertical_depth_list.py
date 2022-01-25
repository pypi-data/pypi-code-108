from itertools import zip_longest
from typing import Any, Dict, List

from pandas import DataFrame

from cognite.well_model.client.utils._auxiliary import to_camel_case


class TrueVerticalDepthList:
    """Custom list of interpolated true vertical depth values with corresponding list of measured depth
    with support of dataframes

    Attributes:
        true_vertical_depths (List[float]): a list of interpolated true vertical depths
        measured_depths (List[float]): a list of measured depth corresponding to the list of interpolated TVDs
    """

    def __init__(
        self,
        true_vertical_depths: List[float],
        measured_depths: List[float],
    ):
        if len(true_vertical_depths) != len(measured_depths):
            raise AttributeError("True Vertical Depth and measured depth must contain same number of elements")
        self.true_vertical_depths = true_vertical_depths
        self.measured_depths = measured_depths

    def find(self, measured_depth: float) -> float:
        """Finds true vertical depth interpolation based on measured depth

        Args:
            measured_depth (float)
        Raises:
            ValueError: If given measured depth have not been interpolated
        Returns:
            float: True Vertical Depth
        """
        return float(self.true_vertical_depths[self.measured_depths.index(measured_depth)])

    def to_pandas(self, camel_case=True) -> DataFrame:
        """Generate a Pandas Dataframe

        Args:
            camel_case (bool, optional): snake_case if false and camelCase if
                true. Defaults to True.

        Returns:
            DataFrame:
        """
        index_name = "measured_depths"
        if camel_case:
            index_name = to_camel_case(index_name)
        df = DataFrame(self.dump(camel_case=camel_case))
        df.set_index(index_name, inplace=True)
        return df

    def dump(self, camel_case: bool = False) -> Dict[str, Any]:
        """Dump data to python primitives (to deserialized json).

        Args:
            camel_case (bool, optional): Set to `true` for camel case. Defaults to False.

        Returns:
            Dict[str, Any]: json-like
        """
        dumped = {
            "true_vertical_depths": self.true_vertical_depths,
            "measured_depths": self.measured_depths,
        }
        if camel_case:
            dumped = {to_camel_case(key): value for key, value in dumped.items()}
        return {key: value for key, value in dumped.items() if value is not None}

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self.measured_depths[item], self.true_vertical_depths[item]

    def __iter__(self):
        return zip_longest(self.measured_depths, self.true_vertical_depths)

    def __repr__(self):
        return_string = [object.__repr__(md) + "+" + object.__repr__(tvd) for md, tvd in self]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.true_vertical_depths.__len__()
