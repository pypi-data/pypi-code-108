import typing

import pandas as pd
import plotly.express as px

from statistics import mean
from itertools import combinations
from binsdpy.similarity import jaccard


class TopRSimilarity:
    def __init__(
        self,
        source: "pd.DataFrame",
        context: "concepts.Context",
        similarity: typing.Callable = jaccard,
        ignore_columns: typing.List[str] = None,
    ) -> None:
        """Calculates TopR similarities for given dataframe.

        Args:
            source (pd.DataFrame): source data (usually objects ordered by multiple metrics)
            context (concepts.Context): source formal context
            similarity (typing.Callable, optional): similarity which should be used. Defaults to jaccard.
            ignore_columns (typing.List[str], optional): which columns to ignore from source dataframe. Defaults to None.
        """
        if ignore_columns is None:
            ignore_columns = []

        self._similarity = similarity
        self._source = source
        self._context = context
        self.df = self._init(self, ignore_columns)

    @staticmethod
    def _k_values_or_until_differs(iterator, r):
        max_idx = len(iterator) - 1

        if r == 0:
            return []

        for idx in range(len(iterator)):
            if idx + 1 < r or (idx < max_idx and iterator[idx] == iterator[idx + 1]):
                yield iterator[idx]
            else:
                yield iterator[idx]
                break

    @staticmethod
    def _top_r_similarity(inst, metric_1_order, metric_2_order, r):
        def _get_vectors(context, items):
            try:
                label_domain = context._extents
                vectors = tuple(
                    map(label_domain.__getitem__, map(context.properties.index, items))
                )
            except ValueError:
                label_domain = context._intents
                vectors = tuple(
                    map(label_domain.__getitem__, map(context.objects.index, items))
                )
            return vectors

        vectors_1 = _get_vectors(
            inst._context, list(inst._k_values_or_until_differs(metric_1_order, r))
        )
        vectors_2 = _get_vectors(
            inst._context, list(inst._k_values_or_until_differs(metric_2_order, r))
        )

        i1 = mean(
            (max((inst._similarity(b1, b2) for b2 in vectors_1)) for b1 in vectors_2)
        )

        i2 = mean(
            (max((inst._similarity(b1, b2) for b2 in vectors_2)) for b1 in vectors_1)
        )

        return min(i1, i2)

    @staticmethod
    def _init(inst, ignore_columns):
        r_range = range(1, len(inst._source.index))

        results = []

        filtered_columns = filter(
            lambda c: c not in ignore_columns, inst._source.columns
        )

        for column1, column2 in combinations(filtered_columns, 2):
            column1_order = list(
                inst._source.sort_values(
                    column1, ascending=False, kind="mergesort"
                ).index
            )
            column2_order = list(
                inst._source.sort_values(
                    column2, ascending=False, kind="mergesort"
                ).index
            )

            label = f"{column1}-{column2}"

            for r in r_range:
                results.append(
                    [
                        r,
                        inst._top_r_similarity(inst, column1_order, column2_order, r),
                        label,
                    ]
                )

        return pd.DataFrame(results, columns=["r", "top_k_similarity", "label"])

    def to_plotly(self) -> "go.Figure":
        """Generates plotly figure.

        Returns:
            go.Figure: figure
        """
        fig = px.line(
            self.df,
            x="r",
            y="top_k_similarity",
            color="label",
            labels={"label": "Legend"},
            line_dash="label",
        )

        # layout needs some cleaning
        fig.update_layout(
            title=dict(
                font=dict(family="IBM Plex Sans", size=14, color="black"),
            ),
            margin=dict(l=15, r=15, t=15, b=15),
            xaxis=dict(
                title="r",
                mirror=True,
                ticks="inside",
                showline=True,
                linecolor="black",
                linewidth=1,
                tickangle=-90,
                tickfont=dict(family="IBM Plex Sans", size=11, color="black"),
            ),
            yaxis=dict(
                title="S",
                mirror=True,
                ticks="inside",
                showline=True,
                linecolor="black",
                linewidth=1,
                tickfont=dict(family="IBM Plex Sans", size=11, color="black"),
            ),
            paper_bgcolor="rgba(255,255,255,1)",
            plot_bgcolor="rgba(255,255,255,1)",
            legend=dict(
                font=dict(family="IBM Plex Sans", size=10),
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
