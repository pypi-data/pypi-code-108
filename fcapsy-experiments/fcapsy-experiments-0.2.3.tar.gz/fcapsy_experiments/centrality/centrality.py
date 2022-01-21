import pandas as pd

from fcapsy.centrality import centrality
from fcapsy_experiments._styles import css, css_corr


class Centrality:
    core_label = "is core"
    centrality_label = "Centrality"

    def __init__(
        self,
        concept: "concepts.lattices.Concept",
        axis: int = 0,
        extra_columns: dict[str, "pd.Series"] = None,
        core_indicator: bool = False,
    ) -> None:
        """Calculates centrality table for given concept

        Args:
            concept ([type]): in which concept the centrality is calculated
            axis (int, optional): if centrality is calculated for objects (0) or attributes (1). Defaults to 0.
            extra_columns (dict[str, pandas.Series], optional): extra columns to be included in the table. Defaults to None.
            core_indicator (bool, optional): if concept core indicators should be included. Defaults to False.
        """
        self._concept = concept

        context = self._concept.lattice._context
        if axis == 0:
            self._items_domain = context.objects
            self._concept_core = self._concept.extent
        elif axis == 1:
            self._items_domain = context.properties
            self._concept_core = self._concept.intent
        else:
            raise ValueError("Invalid axis index")

        self.axis = axis

        self.df = self._init(extra_columns, core_indicator)

        if extra_columns:
            extra_columns = list(extra_columns.keys())

        self.extra_columns = extra_columns

    def _init(self, extra_columns, core_indicator):
        df = pd.DataFrame(
            [centrality(item, self._concept) for item in self._items_domain],
            index=self._items_domain,
            columns=[self.centrality_label],
        )

        if extra_columns:
            for name, values in extra_columns.items():
                df[name] = values

        if core_indicator:
            df[self.core_label] = [
                int(item in self._concept_core) for item in self._items_domain
            ]

        return df

    def _filter_sort_df(self, include_core_flag=False, quantile=0.75):
        """Filters results which are equals to zero and anythig which is not present in quantile."""
        filtered_df = self.df.loc[self.df[self.centrality_label] > 0]

        if not include_core_flag:
            filtered_df = filtered_df.drop(list(self._concept_core.members()), axis=0)

        quantile_value = filtered_df.quantile(quantile)[self.centrality_label]
        filtered_df = filtered_df.loc[
            filtered_df[self.centrality_label] >= quantile_value
        ]
        filtered_df = filtered_df.sort_values(
            self.centrality_label, ascending=False, kind="mergesort"
        )

        return filtered_df

    def to_html(self, include_core_flag: bool = False, quantile: float = 0.75) -> str:
        """Generates html table.

        Args:
            include_core_flag (bool, optional): column with information if item is definition core of concept. Defaults to False.
            quantile (float, optional): values outside this quantile will be filtered out. Defaults to 0.75.

        Returns:
            str: html output
        """
        final_table = self._filter_sort_df(
            include_core_flag=include_core_flag, quantile=quantile
        )

        final_table = final_table.style.format(precision=3)
        final_table.background_gradient(cmap="RdYlGn")
        final_table.set_table_styles(css + css_corr)

        return final_table.to_html()
