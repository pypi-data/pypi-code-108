"""Method(s) for extracting continuous HRV parameter."""
from typing import Dict, Optional

import neurokit2 as nk
import pandas as pd
from biopsykit.signals.ecg import EcgProcessor
from biopsykit.utils.array_handling import sliding_window
from biopsykit.utils.datatype_helper import RPeakDataFrame

__all__ = ["hrv_continuous"]

from tqdm.auto import tqdm


def hrv_continuous(rpeaks: RPeakDataFrame, sampling_rate: Optional[float] = 256.0) -> pd.DataFrame:
    """Perform continuous HRV parameter computation on sliding windows of R peaks.

    The windowing is performed on the R peak samples with a window size of N = 10 samples (R peaks) and a
    shift of 1 sample.

    Parameters
    ----------
    rpeaks : :obj:`~biopsykit.utils.datatype_helper.RPeakDataFrame`
        dataframe with R peaks
    sampling_rate : float, optional
        sampling rate of the source data. Default: 256.0 Hz

    Returns
    -------
    :class:`~pandas.DataFrame`
        dataframe with HRV parameters per sliding window

    """
    if isinstance(rpeaks.index, pd.DatetimeIndex):
        rpeaks_idx = pd.to_datetime(
            sliding_window(pd.to_numeric(rpeaks.index), window_samples=10, overlap_samples=9)[:, 0]
        )
    else:
        rpeaks_idx = sliding_window(rpeaks.index, window_samples=10, overlap_samples=9)[:, 0]

    rpeaks_sliding_window = sliding_window(rpeaks[["R_Peak_Idx"]], window_samples=10, overlap_samples=9)
    rpeaks_sliding_window = pd.DataFrame(rpeaks_sliding_window, index=rpeaks_idx)
    rpeaks_sliding_window = rpeaks_sliding_window.dropna()

    return rpeaks_sliding_window.apply(lambda row: nk.hrv_time(row, sampling_rate=int(sampling_rate)).squeeze(), axis=1)


def hrv_continuous_dict(ecg_processor: EcgProcessor) -> Dict[str, pd.DataFrame]:
    """Extract continuous heart rate variability (HRV) data from a dictionary of data.

    Parameters
    ----------
    ecg_processor : :class:`~biopsykit.signals.ecg.EcgProcessor`
        ``EcgProcessor`` instance to extract R-peak data from

    Returns
    -------
    dict
        dictionary with continuous HRV data

    """
    return {key: hrv_continuous(rpeaks) for key, rpeaks in tqdm(list(ecg_processor.rpeaks.items()), desc="HRV")}
