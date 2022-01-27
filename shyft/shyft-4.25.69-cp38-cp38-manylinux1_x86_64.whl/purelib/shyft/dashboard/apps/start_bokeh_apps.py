from shyft.dashboard.apps.water_route_app.water_route_app import WaterRouteApp
from shyft.dashboard.util.find_free_port import find_free_port
from shyft.dashboard.base.app import start_bokeh_apps
from shyft.dashboard.apps.dtss_viewer.dtss_viewer_app import DtssViewerApp
from shyft.time_series import TimeAxis, TimeSeries, TsVector, utctime_now, point_interpretation_policy as ts_fx, \
    DtsServer, DtsClient, shyft_url, time
from tempfile import TemporaryDirectory
from pathlib import Path
import numpy as np
# -- CHANGE OF LOGGER FORMAT FOR DEBUGGING
import logging

log_fmt = logging.Formatter("in: %(filename)s -- %(funcName)s -- %(lineno)d \n")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_fmt)
logger = logging.getLogger()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def start_local_demo_dtss(root_container: Path, n_ts: int = 100, port: int = 0) -> DtsServer:
    s = DtsServer()
    s.set_listening_port(port)  # could be 0, in that case, it selects a free port
    container_name = 'test'
    s.set_container(container_name, str(root_container))
    port = s.start_async()  # we pick the actual port here, either the supplied port, or auto selected
    print(f'Started demo dtss-server @{port} using ts-container test->{root_container}')
    # fill in some demo-data

    print(f'Filling up test ts-container with some {n_ts} time-series ')
    c = DtsClient(f'localhost:{port}', 1000)
    dt = time(3600)  # hourly resolution
    n_days = 365
    ta = TimeAxis(time('2020-01-01T00:00:00Z'), dt, 24 * n_days)
    t = ta.time_points_double[:-1]
    w_h = 2 * 3.1415 / 3600.0
    tsv = TsVector()
    for i in range(100):
        rd = np.random.random() * 2.0
        v = 1000.0 * (np.abs(np.sin(t * w_h / 24.0)) + rd + 5 * np.sin(t * w_h / (24.0 * 7)) + (10 + rd) * np.sin(
            t * w_h / (24 * n_days)))
        tsv.append(TimeSeries(shyft_url(container_name, f'ts-{i}'), TimeSeries(ta, v, ts_fx.POINT_AVERAGE_VALUE)))
    t0 = utctime_now()
    c.store_ts(tsv, overwrite_on_write=True,
               cache_on_write=True)  # replace existing, and cache it in memory for faster read-access
    t_used = utctime_now() - t0
    c.close()
    print(f'Done creating demo test-series, n_days={n_days}  hourly, used {t_used} to store&cache')
    return s, port


if __name__ == "__main__":
    import argparse

    available_apps = {'dtss_viewer_app': DtssViewerApp, 'water_route_app': WaterRouteApp}

    # add user name as in old bat scripts from sih
    default_port = find_free_port()

    parser = argparse.ArgumentParser(prog="start_bokeh_apps",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--no-show", action="store_false", default=True,
                        help="Don't show ltm bokeh apps in default browser")
    parser.add_argument("-a", "--apps", nargs="+",
                        default=list(available_apps.keys()),
                        dest='apps', help=f"Run one or more specific app(s): {list(available_apps.keys())}")
    parser.add_argument("-p", "--port", type=int, default=default_port,
                        help="Port to run bokeh server [will crash if it is not free]")
    parser.add_argument('-d', '--debug', help="Print lots of debugging statements",
                        action="store_const", dest="log_level", const=logging.DEBUG,
                        default=logging.ERROR)
    parser.add_argument('-v', '--verbose', help="Be verbose",
                        action="store_const", dest="log_level", const=logging.INFO)
    parser.add_argument("-l", "--logger_box", action="store_true", default=False,
                        help="Enable logger box in application")
    parser.add_argument("-u", "--use-external-dtss", action="store_true", dest="use_external_dtss", default=False,
                        help="Use external dtss, do *not* start local dtss for demo purposes")

    a = parser.parse_args()

    if not a.apps:
        raise RuntimeError(f"No apps defined, use -a to define apps! Possible apps are: {list(available_apps.keys())}")

    apps = [available_apps[k] for k in a.apps if k in available_apps]
    if not apps:
        raise RuntimeError(
            f"'-a : {a.apps}' unknown apps defined! possible apps are: {list(available_apps.keys())}")
    dtss = None
    with TemporaryDirectory() as root_dir:
        dtss_port = 0
        app_kwargs = {}
        try:
            if not a.use_external_dtss:
                dtss, dtss_port = start_local_demo_dtss(root_container=root_dir)
                app_kwargs = {'dtss_host': 'localhost', 'dtss_port': dtss_port}

            start_bokeh_apps(apps=apps,
                             show=a.no_show,
                             port=a.port,
                             log_level=a.log_level,
                             show_logger_box=a.logger_box, app_kwargs=app_kwargs)
        finally:
            if dtss:
                dtss.clear()
