"""
Base rule filter class. Main filter classes inherit from this one.
"""
from iguanas.utils.typing import PandasDataFrameType
from typing import List


class _BaseFilter:
    """
    Base rule filter class. Main filter classes inherit from this one.

    Parameters
    ----------
    rules_to_keep : List[str]
        List of rules which remain after correlated rules have been removed.
    """

    def __init__(self, rules_to_keep: List[str]) -> None:
        self.rules_to_keep = rules_to_keep

    def transform(self, X_rules: PandasDataFrameType) -> PandasDataFrameType:
        """
        Applies the filter to the given dataset.

        Parameters
        ----------
        X_rules : PandasDataFrameType
            The binary columns of the rules applied to a dataset.

        Returns
        -------
        PandasDataFrameType
            The binary columns of the filtered rules.
        """

        X_rules = X_rules[self.rules_to_keep]
        return X_rules

    def fit_transform(self,
                      X_rules: PandasDataFrameType,
                      y=None,
                      sample_weight=None) -> PandasDataFrameType:
        """
        Fits then applies the filter to the given dataset.

        Parameters
        ----------
        X_rules : PandasDataFrameType
            The binary columns of the rules applied to a dataset.
        y : PandasSeriesType, optional
            The target (if relevant). Defaults to None.
        sample_weight : PandasSeriesType, optional
            Row-wise weights to apply. Defaults to None.

        Returns
        -------
        PandasDataFrameType
            The binary columns of the filtered rules.
        """

        self.fit(X_rules=X_rules, y=y, sample_weight=sample_weight)
        return self.transform(X_rules=X_rules)
