"""Contains classes for calculating classification metrics."""
import numpy as np
from typing import Union
import iguanas.utils as utils
from iguanas.utils.types import NumpyArray, PandasDataFrame, PandasSeries, \
    KoalasDataFrame, KoalasSeries
from iguanas.utils.typing import NumpyArrayType, PandasDataFrameType, \
    PandasSeriesType, KoalasDataFrameType, KoalasSeriesType


class Precision:
    """
    Calculates the Precision for either a single or set of binary
    predictors.
    """

    def __repr__(self):
        return 'Precision'

    def fit(self,
            y_preds: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType,
                           PandasDataFrameType, KoalasDataFrameType],
            y_true: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType],
            sample_weight=None) -> Union[float, NumpyArrayType]:
        """
        Calculates the Precision for either a single or set of binary
        predictors.

        Parameters
        ----------
        y_preds : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType]
            The binary predictor column(s).
        y_true : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType]
            The target column.
        sample_weight : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType], optional
            Row-wise weights to apply. Defaults to None.

        Returns
        -------
        Union[float, NumpyArrayType]
            The Precision score(s).
        """

        utils.check_allowed_types(
            y_true, 'y_true', [
                NumpyArray, PandasSeries,
                KoalasSeries
            ])
        utils.check_allowed_types(
            y_preds, 'y_preds', [
                NumpyArray, PandasSeries,
                PandasDataFrame, KoalasSeries,
                KoalasDataFrame
            ])
        if sample_weight is not None:
            utils.check_allowed_types(
                sample_weight, 'sample_weight', [
                    NumpyArray, PandasSeries,
                    KoalasSeries
                ])
        tps_sum, _, _, _, tps_fps_sum, _ = utils.calc_tps_fps_tns_fns(
            y_true=y_true, y_preds=y_preds, sample_weight=sample_weight, tps=True, tps_fps=True)
        tps_fps_sum = np.where(tps_fps_sum == 0, np.nan, tps_fps_sum)
        precision = np.nan_to_num(np.divide(tps_sum, tps_fps_sum))
        return precision


class Recall:
    """
    Calculates the Recall for either a single or set of binary
    predictors.
    """

    def __repr__(self):
        return 'Recall'

    def fit(self,
            y_preds: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType],
            y_true: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType],
            sample_weight=None) -> Union[float, NumpyArrayType]:
        """
        Calculates the Recall for either a single or set of binary
        predictors.

        Parameters
        ----------
        y_preds : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType]
            The binary predictor column(s).
        y_true : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType]
            The target column.
        sample_weight : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType], optional
            Row-wise weights to apply. Defaults to None.

        Returns
        -------
        Union[float, NumpyArrayType]
            The Recall score(s).
        """

        utils.check_allowed_types(
            y_true, 'y_true', [
                NumpyArray, PandasSeries,
                KoalasSeries
            ])
        utils.check_allowed_types(
            y_preds, 'y_preds', [
                NumpyArray, PandasSeries,
                PandasDataFrame, KoalasSeries,
                KoalasDataFrame
            ])
        if sample_weight is not None:
            utils.check_allowed_types(
                sample_weight, 'sample_weight', [
                    NumpyArray, PandasSeries,
                    KoalasSeries
                ])
        tps_sum, _, _, _, _, tps_fns_sum = utils.calc_tps_fps_tns_fns(
            y_true=y_true, y_preds=y_preds, sample_weight=sample_weight,
            tps=True, tps_fns=True)
        tps_fns_sum = np.where(tps_fns_sum == 0, np.nan, tps_fns_sum)
        recall = np.nan_to_num(np.divide(tps_sum, tps_fns_sum))
        return recall


class FScore:
    """
    Calculates the Fbeta score for either a single or set of binary
    predictors.

    Parameters
    ----------
    beta : float
        The beta value used to calculate the Fbeta score.        
    """

    def __init__(self, beta: float):
        self.beta = beta

    def __repr__(self):
        return f'FScore with beta={self.beta}'

    def fit(self,
            y_preds: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType],
            y_true: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType],
            sample_weight=None) -> Union[float, NumpyArrayType]:
        """
        Calculates the Fbeta score for either a single or set of binary
        predictors.

        Parameters
        ----------
        y_preds : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType]
            The binary predictor column(s).
        y_true : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType]
            The target column.
        sample_weight : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType], optional
            Row-wise weights to apply. Defaults to None.

        Returns
        -------
        Union[float, NumpyArrayType]
            The Fbeta score(s).
        """
        def _fscore(p, r, b):
            if p == 0 or r == 0:
                fs = 0
            else:
                fs = (1 + b ** 2) * ((p * r) / ((p * b ** 2) + r))
            return fs

        utils.check_allowed_types(
            y_true, 'y_true', [
                NumpyArray, PandasSeries,
                KoalasSeries
            ])
        utils.check_allowed_types(
            y_preds, 'y_preds', [
                NumpyArray, PandasSeries,
                PandasDataFrame, KoalasSeries,
                KoalasDataFrame
            ])
        if sample_weight is not None:
            utils.check_allowed_types(
                sample_weight, 'sample_weight', [
                    NumpyArray, PandasSeries,
                    KoalasSeries
                ])
        tps_sum, _, _, _, tps_fps_sum, tps_fns_sum = utils.calc_tps_fps_tns_fns(
            y_true=y_true, y_preds=y_preds, sample_weight=sample_weight,
            tps=True, tps_fps=True, tps_fns=True
        )
        tps_fps_sum = np.where(tps_fps_sum == 0, np.nan, tps_fps_sum)
        tps_fns_sum = np.where(tps_fns_sum == 0, np.nan, tps_fns_sum)
        precisions = np.nan_to_num(np.divide(tps_sum, tps_fps_sum))
        recalls = np.nan_to_num(np.divide(tps_sum, tps_fns_sum))

        if utils.is_type(precisions, NumpyArray) and \
                utils.is_type(recalls, NumpyArray):
            fscores = np.array([_fscore(p, r, self.beta)
                               for p, r in zip(precisions, recalls)])
        else:
            fscores = _fscore(precisions, recalls, self.beta)
        return fscores


class Revenue:
    """
    Calculates the revenue for either a single or set of binary
    predictors.

    Parameters
    ----------
    y_type : str
        Dictates whether the binary target column flags fraud (y_type = 
        'Fraud') or non-fraud (y_type = 'NonFraud').
    chargeback_multiplier : int
        Multiplier to apply to chargeback transactions.
    """

    def __init__(self, y_type: str, chargeback_multiplier: int):

        if y_type not in ['Fraud', 'NonFraud']:
            raise ValueError('`y_type` must be either "Fraud" or "NonFraud"')
        self.y_type = y_type
        self.chargeback_multiplier = chargeback_multiplier

    def __repr__(self):
        return f'Revenue with y_type={self.y_type}, chargeback_multiplier={self.chargeback_multiplier}'

    def fit(self,
            y_preds: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType],
            y_true: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType],
            sample_weight: Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType]) -> Union[float, NumpyArrayType]:
        """
        Calculates the revenue for either a single or set of binary
        predictors.

        Parameters
        ----------
        y_preds : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType, PandasDataFrameType, KoalasDataFrameType]
            The binary predictor column.
        y_true : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType] 
            The target column.
        sample_weight : Union[NumpyArrayType, PandasSeriesType, KoalasSeriesType] 
            Row-wise transaction amounts to apply.

        Returns
        -------
        Union[float, NumpyArrayType]
            Revenue(s).
        """

        utils.check_allowed_types(
            y_true, 'y_true', [
                NumpyArray, PandasSeries,
                KoalasSeries
            ])
        utils.check_allowed_types(
            y_preds, 'y_preds', [
                NumpyArray, PandasSeries,
                PandasDataFrame, KoalasSeries,
                KoalasDataFrame
            ])
        utils.check_allowed_types(
            sample_weight, 'sample_weight', [
                NumpyArray, PandasSeries,
                KoalasSeries
            ])
        tps_sum, fps_sum, tns_sum, fns_sum, _, _ = utils.calc_tps_fps_tns_fns(
            y_true=y_true, y_preds=y_preds, sample_weight=sample_weight,
            tps=True, fps=True, tns=True, fns=True)
        if self.y_type == 'Fraud':
            revenue = self.chargeback_multiplier * \
                (tps_sum - fns_sum) + tns_sum - fps_sum
        elif self.y_type == 'NonFraud':
            revenue = tps_sum - fns_sum + \
                self.chargeback_multiplier * (tns_sum - fps_sum)
        return revenue
