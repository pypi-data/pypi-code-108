"""Phase module for calculations regarding the phase."""
from typing import Union

from numpy import sign
from pandas import DataFrame, Series


def accumulated_phase(data: Series, limit: float = 340) -> None:
    """Scan a row of a :obj:`pandas.DataFrame` and calculate the absolute phase delay.

    Looks for a jump in the phase of at least :obj:`limit` and adds ±360° to remove the phase jump.

    Parameters
    ----------
    data : pandas.Series
        Row of a :obj:`pandas.DataFrame`.
    limit : float
        Minimum phase difference to detect a phase jump.

    Returns
    -------
    None
        The row is changed inplace, no need for a return value.

    """
    if len(data.shape) != 1:
        raise ValueError("The DataFrame should only contain one single column.")
    for i in range(1, len(data)):
        if abs(data.iloc[i - 1] - data.iloc[i]) > limit:
            data.iloc[i:] += 360 * sign(data.iloc[i - 1] - data.iloc[i])


def clamp_phase(
    phase: Union[float, Series, DataFrame]
) -> Union[float, Series, DataFrame]:
    """
    Returns phase with all values mapped to between +/- 180 degrees.
    """
    return (phase + 180.0) % 360.0 - 180.0
