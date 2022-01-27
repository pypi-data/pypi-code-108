import math
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import (
    DepthMeasurementData,
    DepthMeasurementDataColumn,
    DepthMeasurementRow,
    DistanceUnit,
    SequenceSource,
)


class DepthMeasurementRows:
    """Custom data class for the data collected from surveys, so they can be
    displayed as dataframes correctly
    """

    def __init__(
        self,
        cdf_id: int,
        source: SequenceSource,
        columns: List[DepthMeasurementDataColumn],
        rows: List[DepthMeasurementRow],
        unit: DistanceUnit,
    ):
        self.id = cdf_id
        self.source = source
        self.columns = columns
        self.rows = rows
        self.unit = unit

    @staticmethod
    def from_measurement_data(measurement_data: DepthMeasurementData):
        return DepthMeasurementRows(
            measurement_data.id,
            measurement_data.source,
            measurement_data.columns,
            measurement_data.rows,
            measurement_data.depth_unit,
        )

    # Code for dump and to_pandas copied from sequences in cdf
    def dump(self, camel_case: bool = False) -> Dict[str, Any]:
        """Dump data to python primitives (to deserialized json).

        Args:
            camel_case (bool, optional): Set to `true` for camel case. Defaults to False.

        Returns:
            Dict[str, Any]: json-like
        """
        dumped = {
            "id": self.id,
            "sequence_external_id": self.source.sequence_external_id,
            "columns": self.columns,
            "rows": [{"rowNumber": r.row_number, "depth": r.depth, "values": r.values} for r in self.rows],
        }
        if camel_case:
            dumped = {to_camel_case(key): value for key, value in dumped.items()}
        return {key: value for key, value in dumped.items() if value is not None}

    def to_pandas(self, column_names: str = "columnExternalId|measurementType") -> pd.DataFrame:
        """Converts the MeasurementList to a pandas DataFrame.

        Args:
            column_names (str): Changes the format of the column names. Set to
                ``columnExternalId``, ``measurementType``, or a combination of them
                separated by ``|``. Default is ``columnExternalId|measurementType``.
        """
        options = ["sequenceExternalId", "id", "columnExternalId", "measurementType"]
        for column_name in column_names.split("|"):
            if column_name not in options:
                valid_options = ", ".join(options)
                raise ValueError(f"Invalid column_names value, should be one of {valid_options} separated by |.")

        column_names = (
            column_names.replace("columnExternalId", "{columnExternalId}")
            .replace("sequenceExternalId", "{sequenceExternalId}")
            .replace("id", "{id}")
            .replace("measurementType", "{measurementType}")
        )
        df_columns = [
            column_names.format(
                id=str(self.id),
                sequenceExternalId=str(self.source.sequence_external_id),
                columnExternalId=column.external_id,
                measurementType=column.measurement_type,
            )
            for column in [column for column in self.columns]
        ]

        row_values = [row.values for row in self.rows]
        index = pd.Float64Index(name="depth", data=[row.depth for row in self.rows])
        return pd.DataFrame(
            [[x if x is not None else math.nan for x in r] for r in row_values],
            index=index,
            columns=df_columns,
        )

    def plot(self, *, curves: List[str] = [], log_curves: List[str] = []):
        colours = ["green", "red", "blue"]

        def get_measurement_type(target):
            for c in self.columns:
                if c.external_id == target:
                    return c.measurement_type
            return None

        df = self.to_pandas("columnExternalId|measurementType")
        df.reset_index(inplace=True)

        min_depth = df.iloc[0]["depth"]
        max_depth = df.iloc[-1]["depth"]
        # 6% (2 * 3%) of the graph will be whitespace without any data
        off_set = (max_depth - min_depth) * 0.03
        min_depth -= off_set
        max_depth += off_set

        if not curves and not log_curves:
            curves = [c.external_id for c in self.columns]

        fig, axs = plt.subplots(figsize=(15, 15))
        fig.suptitle(f"Sequence external id: {self.source.sequence_external_id}", fontsize=14, fontweight="bold")

        all_curves = [(c, False) for c in curves] + [(c, True) for c in log_curves]

        for index, (curve, is_log) in enumerate(all_curves):
            mt = get_measurement_type(curve)
            if mt is None:
                continue
            ax = plt.subplot2grid((1, len(all_curves)), (0, index))
            ax.plot(f"{curve}|{mt}", "depth", data=df, color=colours[index % len(colours)])
            if index > 0:
                plt.setp(ax.get_yticklabels(), visible=False)
            else:
                depth_label = (
                    self.unit.factor
                    and self.unit.factor != 1.0
                    and f"{self.unit.factor} {self.unit.unit.value}"
                    or self.unit.unit.value
                )
                ax.set_ylabel(depth_label)
            if is_log:
                ax.semilogx()
            ax.set_xlabel(f"{curve}\n{mt}")
            ax.set_ylim(max_depth, min_depth)
            ax.xaxis.set_ticks_position("top")
            ax.xaxis.set_label_position("top")
            ax.grid()

        fig.subplots_adjust(wspace=0.05)

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self.rows[item]

    def __iter__(self):
        return self.rows.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.rows]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.rows.__len__()
