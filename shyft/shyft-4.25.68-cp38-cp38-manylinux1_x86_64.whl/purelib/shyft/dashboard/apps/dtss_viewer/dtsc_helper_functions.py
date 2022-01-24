from typing import List, Tuple
import shyft.time_series as sa
from shyft.dashboard.time_series.state import Quantity, State, Unit
from shyft.dashboard.time_series.sources.ts_adapter import TsAdapter
from shyft.dashboard.time_series.state import State


def check_dtss_url(dtss_url: str) -> bool:
    """
    This function evaluates if the url belogs to a running dts server
    Parameters
    ----------
    dtss_url:
        url of dtss like localhost:20000

    Returns
    -------
    True if dtss reachable with given url, False if not
    """
    dtsc = sa.DtsClient(dtss_url)
    try:
        dtsc.reopen()
    except RuntimeError as e:
        return False
    finally:
        dtsc.close()
    return True


def try_dtss_connection(dtss_url: str) -> bool:
    """
    This function evaluates if the url belogs to a running dts server
    Parameters
    ----------
    dtss_url:
        url of dtss like localhost:20000

    Returns
    -------
    True if dtss reachable with given url

    Raises
    ------
    RuntimeError if no dtss can be found under given url
    """
    dtsc = sa.DtsClient(dtss_url)
    try:
        dtsc.reopen()
    finally:
        dtsc.close()
    return True


def find_all_dtss_infos(dtss_url: str, dtss_container:str) -> sa.TsVector:
    """
    This function returns a TsVector of TsInfo for each Time Series in the container of the
    dtss at the url.

    Parameters
    ----------
    dtss_url:
        url to dtss
    dtss_container:
        dtss data container to search in

    Returns
    -------
    a TsVector of TsInfo for each Time Series

    Raises
    ------
    RuntimeError if no dtss can be found under given url
    """
    dtsc = sa.DtsClient(dtss_url)
    try:
        return dtsc.find(sa.shyft_url(dtss_container,r'.*'))
    finally:
        dtsc.close()


def find_all_ts_names_and_url(dtss_url: str, dtss_container: str) -> List[Tuple[str, str]]:
    """
    This function returns a list of time series names and urls for each Time Series in the container of the
    dtss at the ts_url.

    Parameters
    ----------
    dtss_url:
        url to dtss
    dtss_container:
        dtss data container to search in

    Returns
    -------
    List of Tuple with (ts_url, name) for each ts in the container

    Raises
    ------
    RuntimeError if no dtss can be found under given url
    """
    ts_infos = find_all_dtss_infos(dtss_url=dtss_url, dtss_container=dtss_container)
    return [(sa.shyft_url(dtss_container,ti.name), ti.name) for ti in ts_infos]


class DtssTsAdapter(TsAdapter):

    def __init__(self, dtss_url: str, ts_url: str) -> None:
        super().__init__()
        # TODO add unit reg
        self.dtsc = sa.DtsClient(dtss_url)
        self.tsv_request = sa.TsVector([sa.TimeSeries(ts_url)])

    def __call__(self, *, time_axis: sa.TimeAxis, unit: Unit) -> Quantity[sa.TsVector]:
        try:
            tsv = self.dtsc.evaluate(self.tsv_request.average(time_axis), time_axis.total_period())
        except RuntimeError as e:
            return sa.TsVector()
        finally:
            self.dtsc.close()
        return State.Quantity(tsv, '')


if __name__ == '__main__':

    dtss_url = 'localhost:20000'
    dtss_container = 'test'


    check_dtss_url(dtss_url)
    ts_url_names = find_all_ts_names_and_url(dtss_url=dtss_url, dtss_container=dtss_container)

    print(ts_url_names[0][0])
    dtss_adapter = DtssTsAdapter(dtss_url=dtss_url, ts_url=ts_url_names[0][0])

    time_axis = sa.TimeAxis(sa.utctime_now()-sa.Calendar.MONTH*5, 20, sa.Calendar.DAY)
    tsv = dtss_adapter(time_axis=time_axis, unit='')
    print(tsv.units)
    print(len(tsv))
    if len(tsv):
        print(tsv[0].time_axis.time_points)
        print(tsv[0].values.to_numpy())


    print(ts_url_names[1][0])
    dtss_adapter = DtssTsAdapter(dtss_url=dtss_url, ts_url=ts_url_names[1][0])

    time_axis = sa.TimeAxis(sa.utctime_now()-sa.Calendar.MONTH*5, 20, sa.Calendar.DAY)
    tsv = dtss_adapter(time_axis=time_axis, unit='')
    print(tsv.units)
    print(len(tsv))
    if len(tsv):
        print(tsv[0].time_axis.time_points)
        print(tsv[0].values.to_numpy())

