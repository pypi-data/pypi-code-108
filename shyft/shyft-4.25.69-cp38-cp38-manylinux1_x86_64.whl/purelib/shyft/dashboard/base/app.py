"""
This module contains classes and methods to define and serve bokeh apps for all projects in the same way
"""
import logging

from typing import Dict, List, Any, Callable, Type, Optional, Union
import abc

from functools import partial

from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.layouts import column, row
from bokeh.server.server import Server

from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop

import bokeh

from shyft.dashboard.widgets.logger_box import LoggerBox


class AppBase(abc.ABC):
    """
    This is the base class for any Dashboard app
    """
    def __init__(self,
                 thread_pool: Optional[ThreadPoolExecutor]=None,
                 app_kwargs: Optional[Dict[str, Any]]=None):
        """
        Init of base app

        Parameters
        ----------
        thread_pool:
            Optional thread pool used for async calls within the app
        app_kwargs:
            Optional keyword arguments provided to the app through the start_bokeh_apps methods
        """
        self.thread_pool = thread_pool

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        pass

    @abc.abstractmethod
    def get_layout(self, doc: 'bokeh.document.Document', logger: Optional[LoggerBox]=None) -> bokeh.models.LayoutDOM:
        """
        This function returns the full page layout for the app
        """
        pass


def make_document(doc: bokeh.document.Document,
                  get_app_layout: Callable[[bokeh.document.Document], bokeh.models.LayoutDOM],
                  log_level: int,
                  enable_logger_box: bool=False) -> None:
    """
    This function creates a specific document for a user request and fills in the layout of the app provided by
    the layout callback. (The layout callback should be the implemented method BaseApp.get_layout of the BaseApp)

    Parameters
    ----------
    doc:
        bokeh document provided by the bokeh server
    get_app_layout:
        layout callback should return the entire layout of the app
    log_level:
        log level to initialize the logger box widget
    enable_logger_box:
        if enabled a logger box widget is added to the app, which shows the log msg from all
        app widgets, this requires that logger in the BaseApp.get_layout function is passed to the widgets.
    """
    logger_box = None
    if enable_logger_box:
        logger_box = LoggerBox(doc, log_level)
    layout = get_app_layout(doc, logger_box)
    if enable_logger_box:
        layout = column(logger_box.layout,
                        row(layout))
    doc.add_root(layout)


def start_bokeh_apps(apps: List[Type[AppBase]],
                     show: bool = False,
                     port: int = 5006,
                     log_level=logging.ERROR,
                     async_on: bool = True,
                     async_max_worker: int = 12,
                     show_logger_box: bool = False,
                     server_kwargs: Optional[Dict[str, Any]] = None,
                     app_kwargs: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None) -> None:
    """
    This function starts a bokeh serve with the apps provided to the function

    Parameters
    ----------
    apps:
        List of AppBase classes
    show:
        if True a browser with all apps will be opened
    port:
        port where on which the apps are loaded 'localhost:port'
    log_level:
        Logging level in the console
    async_on:
        use async data loading
    async_max_worker:
        number of workers for thread pool doing the async data loading
    show_logger_box:
        enable in-app logger
    server_kwargs:
        keyword arguments for the Bokeh / tornado server
    app_kwargs:
        list of dictionaries of additional keyword arguments for the apps, if a single dictionary is passed, a list
        is created with the same length as the number of apps
    """
    if not server_kwargs:
        server_kwargs = {}
    if not isinstance(app_kwargs, list):
        app_kwargs = [app_kwargs]
        for _ in range(len(apps)-1):
            app_kwargs.append(app_kwargs[0].copy()) if app_kwargs[0] is not None else app_kwargs.append(None)
    if not len(app_kwargs) == len(apps):
        raise RuntimeError(f'Required: len(app_kwargs) == len(apps), {len(app_kwargs)} != {len(apps)}')
    logger = logging.getLogger()
    logger.setLevel(log_level)
    dp_pct = 1.0/(len(apps) + 3 + int(show))*100
    pct = 0.0
    if async_on:
        thread_pool = ThreadPoolExecutor(max_workers=async_max_worker)
    else:
        thread_pool = None

    io_loop = IOLoop.current()
    end_points = {}
    for app, kwargs in zip(apps, app_kwargs):
        pct += dp_pct
        print(f"[{pct:>3.0f}%]  Initializing: {app.__name__}")
        app_instance = app(thread_pool=thread_pool, app_kwargs=kwargs)
        if not issubclass(app, AppBase):
            print(f"App {app} is not of type AppBase .. skipped")
            continue
        if app_instance in end_points:
            print(f"WARNING: Not Adding App {app_instance} with name {app_instance.name} since endpoint exists already")
            continue
        make_doc = partial(make_document,
                           get_app_layout=app_instance.get_layout,
                           enable_logger_box=show_logger_box,
                           log_level=log_level)
        end_points[f"/{app_instance.name.replace(' ', '_').lower()}"] = Application(FunctionHandler(make_doc))
    pct += dp_pct
    print(f"[{pct:>3.0f}%]  Set up server with async_on={async_on}  and workers={async_max_worker}")
    server = Server(end_points, port=port, allow_websocket_origin=['*'], **server_kwargs)
    pct += dp_pct
    print(f"[{pct:>3.0f}%]  Start bokeh server: apps are served on port {port}")
    urls = "\n".join([f'                            http://localhost:{port}{app}' for app in end_points])
    print(f'{urls}')
    server.start()

    if show:
        pct += dp_pct
        print(f"[{pct:>3.0f}%]  Launching website")
        for k in end_points.keys():
            server.show(app_path=k, browser='windows-default', new='tab')

    pct += dp_pct
    print(f"[{pct:>3.0f}%]  Start io_loop: this may take a while ...")
    io_loop.start()


LayoutComponents = Dict[str, List[Any]]


def update_value_factory(layout_dom_object,
                         callback_attr: str,
                         logger: Optional[logging.Logger]=None) -> Callable[[Any], None]:
    """
    Factory method to create update functions for attributes bokeh layout dom objects, without triggering the
    connected callback functions.

    Parameters
    ----------
    layout_dom_object:
        bokeh object
    callback_attr:
        attribute to update
    logger:
        logger

    Returns
    -------
    Callable which takes one argument to update the bokeh object attribute  callback_attr
    """
    if not isinstance(callback_attr, str):
        raise AttributeError(
            f"'{self}', update_value_factory  callback_attr must be str type, was '{callback_attr}'")
        

    class ValueSetter:

        def __init__(self, layout_dom_object, callback_attr: str, logger: logging.Logger = None) -> None:

            self.logger = logger
            self.layout_dom_object = layout_dom_object
            self.callback_attr = callback_attr
            self.update_dict = {self.callback_attr: None}
            if not hasattr(self.layout_dom_object, callback_attr):
                raise AttributeError(
                    f"'{self}', update_value_factory '{layout_dom_object}' has not callback_attr '{callback_attr}'")

        def update_value_without_callback(self, value: Any) -> None:
            # python callbacks
            c_funcs = self.layout_dom_object._callbacks.get(self.callback_attr, []).copy()
            for c_func in c_funcs:
                self.layout_dom_object.remove_on_change(self.callback_attr, c_func)
            # js callbacks
            js_funcs = {}
            js_callbacks = {k:v for k,v in self.layout_dom_object.js_property_callbacks.items()}
            for js_func_name, js_func in js_callbacks.items():
                js_funcs[js_func_name] = self.layout_dom_object.js_property_callbacks.pop(js_func_name)

            try:
                self.update_dict[self.callback_attr] = value
                self.layout_dom_object.update(**self.update_dict)
            except (AttributeError, ValueError) as e:
                self._log_exception(e, msg="NoCallbackValueSetter Error: ")
                raise e
            except Exception as e:
                self._log_exception(e, msg="NoCallbackValueSetter Unhandled Error: ")
                raise e
            finally:
                for c_func in c_funcs:
                    self.layout_dom_object.on_change(self.callback_attr, c_func)
                self.layout_dom_object.js_property_callbacks.update(js_funcs)

        def _log_exception(self, exception, msg=''):
            if self.logger is not None:
                self.logger.exception("{}: {}".format(msg, exception))

    update_value_function = ValueSetter(layout_dom_object, callback_attr, logger).update_value_without_callback

    return update_value_function


class Widget(metaclass=abc.ABCMeta):

    def __init__(self, logger=None) -> None:
        """
        Base class for all Widgets

        Parameters
        ----------
        logger:
            Optional logger, e.g composable_logger_box
        """
        if not logger:
            logger = logging.getLogger()
        self.logger = logger

    def __dir__(self) -> List[str]:
        return ['layout_components', 'update_value_factory']

    @property
    @abc.abstractmethod
    def layout(self) -> bokeh.models.LayoutDOM:
        pass

    @property
    @abc.abstractmethod
    def layout_components(self) -> LayoutComponents:
        """ Property to return all layout.dom components of an visualisation app
        such that they can be arranged by the parent layout obj as
        desired.

        Returns
        -------
        layout_components as: {'widgets': [], 'figures': []}
        """
        pass

    def update_value_factory(self, layout_dom_object, callback_attr: str) -> Callable[[Any], None]:
        return update_value_factory(layout_dom_object=layout_dom_object,
                                    callback_attr=callback_attr,
                                    logger=self.logger)
