import itertools

import pandas as pd
import plotly.graph_objects as go

from sklearn.preprocessing import MinMaxScaler
from fcapsy.typicality import typicality_avg
from binsdpy.similarity import jaccard, smc, russell_rao

from fcapsy_experiments._styles import css, css_typ


class ConceptTypicality:
    count_label = "Count"

    def __init__(
        self,
        concept: "concepts.lattices.Concept",
        axis: int = 0,
        count: bool = False,
        extra_columns: dict[str, "pd.Series"] = None,
        typicality_functions: dict[str, dict] = None,
    ) -> None:
        """Calculates typiclity for given concept

        Args:
            concept (concepts.lattices.Concept): in which concept the typicality is calculated
            axis (int, optional): if typicality is calculated for objects (0) or attributes (1). Defaults to 0.
            count (bool, optional): if count of attributes/objects should be included as column. Defaults to False.
            extra_columns (dict[str, pandas.Series], optional): extra columns to be included in the table. Defaults to None.
            typicality_functions (dict[str, dict], optional): when specified, user can modify default functions which is used for typicality calculation, see default example. Defaults to None.
        """

        if typicality_functions is None:
            # default typicality configuration
            typicality_functions = {
                "typ_avg": {
                    # must be callable
                    "func": typicality_avg,
                    "args": {"J": [jaccard], "SMC": [smc], "R": [russell_rao]},
                }
            }

        self._concept = concept
        context = self._concept.lattice._context

        if axis == 0:
            self._items_domain = context.objects
            self._items_sets = context._intents
            self._concept_core = self._concept.extent
        elif axis == 1:
            self._items_domain = context.properties
            self._items_sets = context._extents
            self._concept_core = self._concept.intent
        else:
            raise ValueError("Invalid axis index")

        self.axis = axis

        self.df = self._init(concept, count, typicality_functions, extra_columns)

        if extra_columns:
            extra_columns = list(extra_columns.keys())

        self.extra_columns = extra_columns

    def _init(self, concept, count, typicality_functions, extra_columns):
        columns = []

        for name, typicality in typicality_functions.items():
            if typicality["args"]:
                for arg in typicality["args"].keys():
                    columns.append(f"{name}({arg})")
            else:
                columns.append(f"{name}")

        df = pd.DataFrame(index=self._concept_core, columns=columns, dtype=float)

        for item in self._concept_core:
            row = []

            for typicality in typicality_functions.values():
                function = typicality["func"]
                args = typicality["args"].values()
                if args:
                    row = []
                    for name, arg in typicality["args"].items():
                        row.append(function(item, concept, *arg))
                else:
                    row.append(function(item, concept))

            df.loc[item] = row

        if count:
            counts = (extent.bits().count("1") for extent in self._items_sets)

            df[self.count_label] = [
                row[1]
                for row in filter(
                    lambda x: x[0] in self._concept_core,
                    zip(self._items_domain, counts),
                )
            ]

        if extra_columns:
            for name, values in extra_columns.items():
                df[name] = values

        return df

    def to_html(self) -> str:
        """Generates html table.

        Returns:
            str: html output
        """
        final_table = pd.DataFrame()

        for column in self.df.columns:
            round_and_sort = self.df.sort_values(
                column, ascending=False, kind="mergesort"
            )

            final_table[f"{column} order"] = round_and_sort.index
            final_table[column] = round_and_sort.reset_index()[column]

        df = final_table.reset_index().drop("index", axis=1)

        df = df.style.format(precision=3)
        df.background_gradient(cmap="RdYlGn")
        df.set_table_styles(css + css_typ)
        df.hide_index()

        return df.to_html()

    def to_plotly(self) -> "go.Figure":
        """Generates plotly figure.

        Returns:
            go.Figure: figure
        """
        markers = ["square", "diamond", "triangle-up", "circle", "pentagon"]

        scatters = []

        df = self.df.sort_values(self.df.columns[0], ascending=False, kind="mergesort")

        if "Count" in df.columns:
            # scaling Count column
            scaler = MinMaxScaler()
            df["Count"] = scaler.fit_transform(df["Count"].values.reshape(-1, 1))

        if self.extra_columns:
            for extra in self.extra_columns:
                scaler = MinMaxScaler()
                df[extra] = scaler.fit_transform(df[extra].values.reshape(-1, 1))

        for column, marker in zip(df.columns, itertools.cycle(markers)):
            scatters.append(
                go.Scatter(
                    name=column,
                    x=df.index,
                    y=df[column],
                    mode="markers",
                    marker_symbol=marker,
                    marker_line_width=1,
                    marker_size=8,
                )
            )

        fig = go.Figure(data=scatters)

        # layout needs some cleaning
        fig.update_layout(
            font_family="IBM Plex Sans",
            font_color="black",
            margin=dict(l=15, r=15, t=15, b=15),
            xaxis=dict(
                title="objects",
                mirror=True,
                ticks="inside",
                showline=True,
                linecolor="black",
                linewidth=1,
                tickangle=-90,
                gridcolor="rgba(200,200,200,1)",
                tickfont=dict(size=11),
            ),
            yaxis=dict(
                title="typicality",
                mirror=True,
                ticks="inside",
                showline=True,
                linecolor="black",
                linewidth=1,
                range=[0, 1],
                dtick=0.1,
                gridcolor="rgba(200,200,200,0)",
                tickfont=dict(size=11),
            ),
            paper_bgcolor="rgba(255,255,255,1)",
            plot_bgcolor="rgba(255,255,255,1)",
            legend=dict(
                font=dict(size=10),
            ),
        )

        return fig

    def to_plotly_html(
        self, default_width: int = 700, default_height: int = 390
    ) -> str:
        """Generates html version of plotly graph

        Args:
            default_width (int, optional): default graph width. Defaults to 700.
            default_height (int, optional): default graph height. Defaults to 390.

        Returns:
            str: graph html
        """
        return self.to_plotly().to_html(
            full_html=False,
            include_plotlyjs="cdn",
            include_mathjax="cdn",
            default_width=default_width,
            default_height=default_height,
        )
