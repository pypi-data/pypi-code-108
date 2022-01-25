from abc import ABC, abstractmethod
import pandas as pd
from scipy.stats import gmean
from typing import Iterable
import warnings

warn = True


def safe_calculation(func):
    """
    Decoder for safe execution of a function in the thread
    :param func: function
    :return: function value
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as e:
            if warn:
                warnings.warn(
                    ""
                    f"\nStatistics ({func.__qualname__}) cannot be calculated for this data type."
                    f"\nError: {e}"
                )
            return None

    return wrapper


class Statistic(ABC):
    """
    An abstract class of stat_box from which specific stat_box are inherited
    """

    @staticmethod
    def _check_num(series: pd.Series):
        return "int" in series.dtype.name or "float" in series.dtype.name

    @abstractmethod
    def calculate(self, series: pd.Series):
        """
        Calculating stat_box
        :param series: values over which stat_box are calculated
        :return: the result of a statistic calculation
        """
        return

    @abstractmethod
    def str_key(self) -> str:
        return ""


class Size(Statistic):
    """
    Sample size of the sample
    """

    def __init__(self, dropna: bool = False):
        """
        :param dropna: counts the size of only non-empty elements
        """
        self.dropna = dropna

    @safe_calculation
    def calculate(self, series: pd.Series) -> int:
        if self.dropna:
            return len(series.dropna())
        return len(series)

    def str_key(self) -> str:
        return "size" + ("non-empty" if self.dropna else "")


class Density(Statistic):
    """
    Density of non-empty elements
    """

    def calculate(self, series: pd.Series):
        na = Size(True)
        return na.calculate(series) / Size().calculate(series)

    def str_key(self) -> str:
        return "density"


class Min(Statistic):
    """
    Minmum
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.min()

    def str_key(self) -> str:
        return "min"


class Max(Statistic):
    """
    Maximum
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.max()

    def str_key(self) -> str:
        return "max"


class Interval(Statistic):
    """Scatter of values in the sample"""

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.max() - series.min() if self._check_num(series) else None

    def str_key(self) -> str:
        return "interval"


class Mean(Statistic):
    """
    Arithmetic mean
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.mean() if self._check_num(series) else None

    def str_key(self) -> str:
        return "mean"


class WeightedMean(Statistic):
    """
    Weighted average
    """

    def __init__(self, weights_series: pd.Series):
        """
        :param weights_series: веса должны позиционно совпадать с элементами выборки
        """
        self.weights = weights_series

    @safe_calculation
    def calculate(self, series: pd.Series):
        return (
            (series * self.weights).sum() / self.weights.sum()
            if self._check_num(series)
            else None
        )

    def str_key(self) -> str:
        return "weighet_mean"


class Quantile(Statistic):
    """
    Quantile
    """

    def __init__(self, q: float):
        """
        :param q: Quantile from 0 to 1
        """
        self.q = q

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.quantile(self.q) if self._check_num(series) else None

    def str_key(self) -> str:
        return f"quantile({self.q})"


class Std(Statistic):
    """
    Standard deviation
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.std() if self._check_num(series) else None

    def str_key(self) -> str:
        return "std"


class StdCount(Statistic):
    def __init__(self, mode: str = "all"):
        """
        :param mode: mode of operation:
            all - number of standard deviations in the sample
            left - number of standard deviations on the left
            right - number of standard deviations to the right
        """
        self.mode = mode

    @safe_calculation
    def calculate(self, series: pd.Series):
        if not self._check_num(series):
            return None
        if self.mode == "left":
            return (series.mean() - series.min()) / series.std()
        elif self.mode == "right":
            return (series.max() - series.mean()) / series.std()
        else:
            return (series.max() - series.min()) / series.std()

    def str_key(self) -> str:
        addition = ""
        if self.mode in ("left", "right"):
            addition = f" {self.mode}"
        return "std_count" + addition


class CoefficientOfVariation(Statistic):
    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.std() / series.mean() if self._check_num(series) else None

    def str_key(self) -> str:
        return "coefficient_of_variation"


class Skewness(Statistic):
    """
    Asymmetry/Skewness
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.skew() if self._check_num(series) else None

    def str_key(self) -> str:
        return "skewness"


class Kurtosis(Statistic):
    """
    Eksessus/Kurtosis
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.kurt() if self._check_num(series) else None

    def str_key(self) -> str:
        return "kurtosis"


class GeometricMean(Statistic):
    """
    Geometric Mean
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return gmean(series) if self._check_num(series) else None

    def str_key(self) -> str:
        return "geometric_mean"


class Median(Statistic):
    """
    Median value
    """

    @safe_calculation
    def calculate(self, series: pd.Series):
        return series.median() if self._check_num(series) else None

    def str_key(self) -> str:
        return "median"


class Mode(Statistic):
    """
    Mode
    """

    def __init__(self, interval_count: int = 1):
        self.interval_count = interval_count

    @safe_calculation
    def calculate(self, series: pd.Series):
        if self.interval_count <= 1:
            return series.mode().iloc[0]
        intervals = pd.cut(series, bins=self.interval_count)
        return intervals.value_counts().index[0]

    def str_key(self) -> str:
        return "interval " if self.interval_count > 1 else "" + "mode"


class StatisticSet:
    """
    Sets of stat_box
    """

    def __init__(self, stat_set: Iterable[Statistic] = None):
        """
        :param stat_set: stat_box
        """
        self.stat_set = set(stat_set)

    def __add__(self, other):
        return StatisticSet(self.stat_set.union(other.stat_set))

    def calculate(self, series: pd.Series) -> dict:
        """
        Calculation of all stat_box
        :param series: sampling
        :return: calculated stat_box
        """
        return {stat.str_key(): stat.calculate(series) for stat in self.stat_set}

    def stat_table(
        self, df: pd.DataFrame, columns: Iterable[str] = None
    ) -> pd.DataFrame:
        """
        Calculating stat_box from a table
        :param df: Data table
        :param columns: Columns for which stat_box are to be calculated
        :return: table with stat_box
        """
        if columns is None:
            columns = df.keys()
        return pd.DataFrame({k: self.calculate(df[k]) for k in columns}).sort_index()


SIMPLE_SET = StatisticSet(
    {
        Size(),
        Density(),
        Min(),
        Max(),
        Interval(),
        Mean(),
        Median(),
        Std(),
        CoefficientOfVariation(),
    }
)

QUANTILE_SET = StatisticSet({Quantile(i / 100) for i in range(1, 100)})

CATEGORICAL_SET = StatisticSet({Size(), Size(True), Density(), Min(), Max(), Mode()})

if __name__ == "__main__":
    print("This is a basic usage example")
    df = pd.DataFrame(
        {"1": {"a": 1, "b": 2}, "2": {"a": 3, "b": 3}, "3": {"a": "1", "b": "d"}}
    )
    print(df)
    qs = QUANTILE_SET
    r = qs.stat_table(df)
    print(r)
    ss = SIMPLE_SET
    ss.stat_set.add(Mode())
    r = ss.stat_table(df)
    print(r)
