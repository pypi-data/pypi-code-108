import typing
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from fuzzycorr import fuzzy_correlation_factory
from fuzzycorr.strict_orderings import lukasiewicz_strict_ordering_factory
from fuzzycorr.t_norms import godel
from scipy.stats import kendalltau, pearsonr

from fcapsy_experiments._styles import css, css_corr


class Correlation:
    def __init__(self, source: "pd.DataFrame", type: str) -> None:
        """Calculates correlation for source dataframe

        Args:
            source (pd.DataFrame): source data
            type (str): type of correlation ("kendall", "pearson", "fuzzy")
        """
        self.type = type
        self.corr, self.p_values = self._init(self, source)

    @staticmethod
    def _init(inst, source):
        if inst.type in ["kendall", "pearson"]:
            funcs = {"kendall": kendalltau, "pearson": pearsonr}
            corr = funcs[inst.type]

            return source.corr(lambda x, y: corr(x, y)[0]), source.corr(
                lambda x, y: corr(x, y)[1]
            )
        elif inst.type in ["fuzzy"]:
            ordering = lukasiewicz_strict_ordering_factory(r=0.2)
            corr = fuzzy_correlation_factory(ordering, godel)
            return source.corr(corr), None

        raise ValueError(f"Correlation {inst.type} is not supported.")

    def _make_triangle(self, df):
        df = df.where(np.triu(np.ones(df.shape)).astype(bool))
        return df.fillna("")

    def to_html(self, triangle=True) -> str:
        """Generates html which represents the correlation table.

        Returns:
            str: html table
        """

        def highlight_low_corr(x):
            if isinstance(x, str):
                return None
            return f"font-weight: bold;" if abs(x) < 0.2 else None

        if triangle:
            df = self._make_triangle(self.corr)
        else:
            df = self.corr

        df = df.style.format(precision=2)
        df.set_table_styles(css + css_corr)
        df.applymap(highlight_low_corr)

        return df.to_html()

    def p_values_to_html(self, triangle=True) -> typing.Optional[str]:
        """Generates html of pvalues table.

        Returns:
            typing.Optional[str]: html table
        """

        def highlight_high_p_value(x):
            if isinstance(x, str):
                return None
            return f"font-weight: bold;" if abs(x) > 0.04 else None

        if self.p_values is None:
            return None

        if triangle:
            df = self._make_triangle(self.p_values)
        else:
            df = self.p_values

        df = df.style.format(precision=2)
        df.set_table_styles(css + css_corr)
        df.applymap(highlight_high_p_value)

        return df.to_html()

    def to_plotly(self) -> "go.Figure":
        fig = px.imshow(self.corr)
        return fig

    def to_plotly_html(self) -> str:
        return self.to_plotly().to_html(
            full_html=False,
            include_plotlyjs="cdn",
            include_mathjax="cdn",
        )


class CorrelationTable:
    def __init__(self, source: "pd.DataFrame", dataset: str = None) -> None:
        """Represents multiple correlation tables for given source dataframe.

        Args:
            source (pd.DataFrame): source dataframe
            dataset (str, optional): name of the dataset. Defaults to None.
        """
        self.dataset = dataset
        self.source = source

        self._kendall = None
        self._pearson = None
        self._fuzzy = None

    @property
    def kendall(self) -> "Correlation":
        """Returns kendall correlation table."""
        if self._kendall is None:
            self._kendall = Correlation(self.source, "kendall")

        return self._kendall

    @property
    def pearson(self) -> "Correlation":
        """Returns pearson correlation table."""
        if self._pearson is None:
            self._pearson = Correlation(self.source, "pearson")

        return self._pearson

    @property
    def fuzzy(self) -> "Correlation":
        """Returns fuzzy correlation table."""
        if self._fuzzy is None:
            self._fuzzy = Correlation(self.source, "fuzzy")

        return self._fuzzy
