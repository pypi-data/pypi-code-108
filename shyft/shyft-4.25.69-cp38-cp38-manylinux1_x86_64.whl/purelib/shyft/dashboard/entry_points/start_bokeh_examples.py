import argparse

from shyft.dashboard.examples.hover_tool import HoverToolExample
from shyft.dashboard.examples.message_viewer import MessageViewerExample
from shyft.dashboard.examples.basic_bokeh_app import BasicBokeh
from shyft.dashboard.examples.ts_viewer_background_data_renderer import BackgroundDataRendererExample
from shyft.dashboard.examples.time_interval_selector_slider import TimeIntervalSliderExample
from shyft.dashboard.util.find_free_port import find_free_port
from shyft.dashboard.base.app import start_bokeh_apps
from shyft.dashboard.examples.time_series_viewer import TsViewerExample
from shyft.dashboard.examples.time_series_period_selector import TsPeriodSelectorExample
from shyft.dashboard.examples.slider_selector import SliderSelectorExample
from shyft.dashboard.examples.multi_select_tabs import MultiSelectTabsExample
from shyft.dashboard.examples.label_selector import LabelSelectorExample
from shyft.dashboard.examples.date_selector import DateSelectorExample
from shyft.dashboard.examples.selector_views import CompSelectorViewsExample
from shyft.dashboard.examples.selector_model import CompSelectorModelExample
from shyft.dashboard.examples.gates import CompGatesExample
from shyft.dashboard.examples.figure_legend import FigureLegend
from shyft.dashboard.examples.time_series_scatter_renderer import TsScatterViewerExample

# -- CHANGE OF LOGGER FORMAT FOR DEBUGGING
import logging
log_fmt = logging.Formatter("in: %(filename)s -- %(funcName)s -- %(lineno)d \n")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_fmt)
logger = logging.getLogger()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def main(input_args=None):
    """Run shyft dashboard example apps"""

    available_apps = {'ts_viewer': TsViewerExample,
                      'hover_tool_example': HoverToolExample,
                      'time_interval_slider': TimeIntervalSliderExample,
                      'ts_period_selector': TsPeriodSelectorExample,
                      'slider_selector': SliderSelectorExample,
                      'multi_select_tabs': MultiSelectTabsExample,
                      'label_selector': LabelSelectorExample,
                      'date_selector': DateSelectorExample,
                      'selector_views': CompSelectorViewsExample,
                      'selector_model': CompSelectorModelExample,
                      'gates': CompGatesExample,
                      'message_viewer': MessageViewerExample,
                      'base_bokeh_app': BasicBokeh,
                      'figure_legend': FigureLegend,
                      'scatter_renderer': TsScatterViewerExample,
                      'bg_data_renderer': BackgroundDataRendererExample}

    max_len = max([len(k) for k in available_apps.keys()])
    app_names = '\n        '.join([f'{k:<{max_len}} : {a.__module__}' for k, a in available_apps.items()])


    h = f"""Select example bokeh-app:

    All available apps are:\n\n
        {app_names}

    If no specific app is defined with -a all will be started!
    """
    # add user name as in old bat scripts from sih
    default_port = find_free_port()

    parser = argparse.ArgumentParser(prog="Start Bokeh Apps",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=h, add_help=True)
    parser.add_argument("--no-show", action="store_false", default=True,
                        help="Don't show bokeh apps in default browser")
    parser.add_argument("-a", "--apps", nargs="+",
                        dest='apps', help=f"Run one or more specific app(s)",
                        default=available_apps.keys())
    parser.add_argument("-p", "--port", type=int, default=default_port,
                        help="Port to run bokeh server [will crash if it is not free]")
    parser.add_argument('-d', '--debug', help="Print lots of debugging statements",
                        action="store_const", dest="log_level", const=logging.DEBUG,
                        default=logging.ERROR)
    parser.add_argument('-v', '--verbose', help="Be verbose",
                        action="store_const", dest="log_level", const=logging.INFO)
    parser.add_argument("-l", "--logger_box", action="store_true", default=False,
                        help="Enable logger box in application")
    parser.add_argument("--async_off", action="store_true", default=False,
                        help="Disable async data loading")
    parser.add_argument("--async-max-worker", type=int, default=12,
                        help="Number of worker for async data loading")

    args = parser.parse_args(input_args)

    if not args.apps or args.apps is None:
        parser.print_help()
        print(f"No apps defined, use -a to define apps listed above!")
        return

    apps = [available_apps[k] for k in args.apps if k in available_apps]
    if not apps:
        parser.print_help()
        print(f"'-a : {', '.join(args.apps)}' unknown apps defined! use apps listed above!")
        return

    start_bokeh_apps(apps=apps,
                     show=args.no_show,
                     port=args.port,
                     log_level=args.log_level,
                     show_logger_box=args.logger_box,
                     async_on=not args.async_off,
                     async_max_worker=args.async_max_worker)


if __name__ == "__main__":
    main()
