import pkg_resources
import logging

from shyft.dashboard.base.app import AppBase

# -- CHANGE OF LOGGER FORMAT FOR DEBUGGING
log_fmt = logging.Formatter("in: %(filename)s -- %(funcName)s -- %(lineno)d \n")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_fmt)
logger = logging.getLogger()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def parse_entry_points_for_apps():

    available_apps = []
    for entry_point in pkg_resources.iter_entry_points('shyft_dashboard_apps'):
        entry_point_name = entry_point.name
        app_class = entry_point.load()
        if not issubclass(app_class, AppBase):
            print(f"Warning skipping: {entry_point_name}, not subclass of AppBase")
            continue
        available_apps.append((entry_point_name, app_class))

    return available_apps


