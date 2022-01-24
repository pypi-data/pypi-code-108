# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from datetime import datetime, timezone
import threading
import traceback
import time as systime
import uuid
import os

import azureml.core
from azureml.telemetry import get_diagnostics_collection_info

# noinspection PyProtectedMember
from azureml.widgets._telemetry_logger import _TelemetryLogger
# noinspection PyProtectedMember
from azureml.widgets._constants import WIDGET_REFRESH_TIME_OVERRIDE
# noinspection PyProtectedMember
from azureml._base_sdk_common import _ClientSessionId

from . import _platform

_logger = _TelemetryLogger.get_telemetry_logger(__name__)


class _WidgetRunDetailsBase(object):
    """Base class providing common methods by widgets."""

    def __init__(self, widget, widget_sleep_time_updater):
        self.widget_instance = widget()
        self.widget_sleep_time = widget_sleep_time_updater()
        self.widget_sleep_time_updater = widget_sleep_time_updater
        self.widget_instance.heartbeat_timestamp = datetime.now(timezone.utc).timestamp()
        self.settings = {}
        self.isDebug = False
        self.miniWidgetHandle = None

    def __del__(self):
        """Destructor for the widget."""
        pass

    def show(self, render_lib=None, widget_settings=None):
        """Render widget and start thread to refresh the widget.

        :param render_lib: The library to use for rendering.
        :type render_lib: func
        :param widget_settings: The widget settings.
        :type widget_settings: object
        """
        if widget_settings is None:
            widget_settings = {}

        widget_settings = {**self._get_default_setting(), **widget_settings}

        self.settings = widget_settings

        # pass the widget settings to client
        self.widget_instance.widget_settings = self.settings
        self.isDebug = 'debug' in self.settings and self.settings['debug']

        # register events you want to subscribe to while taking actions on traitlets on client side
        try:
            self._register_events()
        except Exception as e:
            if self.isDebug:
                self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))
            from IPython.display import update_display
            import json
            error_to_client = {
                "application/aml.mini.widget.v1": json.dumps(repr(e))
            }
            update_display(error_to_client, display_id=True, raw=True)

        _render_override = os.environ.get('AMLWIDGET_RENDER')
        _render = not _render_override or _render_override == "1"

        # render the widget
        telemetry_values = self._get_telemetry_values(self.show)
        with _TelemetryLogger.log_activity(_logger,
                                           "train.widget.show",
                                           custom_dimensions=telemetry_values):
            if _render:
                try:
                    from IPython.display import display
                    display(self.widget_instance)
                    import json
                    widget_data = {"loading": True}
                    bundle = {
                        "application/aml.mini.widget.v1": json.dumps(widget_data)
                    }
                    self.miniWidgetHandle = display(bundle, display_id=True, raw=True)
                except Exception as e:
                    if render_lib is not None:
                        render_lib(self.widget_instance.get_html())
                    if self.isDebug:
                        self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))
                    from IPython.display import update_display
                    import json
                    error_to_client = {
                        "application/aml.mini.widget.v1": json.dumps(repr(e))
                    }
                    update_display(error_to_client, display_id=True, raw=True)

        def _is_async():
            _sync_override_flag = os.environ.get('AMLWIDGET_SYNC')
            _sync_override = _sync_override_flag and _sync_override_flag == "1"
            return _platform._in_jupyter_nb() and not _sync_override

        # refresh the widget in given interval
        if _is_async():
            import uuid
            suffix = str(uuid.uuid4()).replace("-", "")
            thread = threading.Thread(target=self._refresh_widget,
                                      name="WidgetRefresher" + suffix,
                                      args=(render_lib, self.settings, _render))
            thread.start()
        else:
            self._refresh_widget(render_lib, self.settings, _render)

    def _refresh_widget(self, render_lib, widget_settings, render_widget=True):
        """Retrieve data from data source and update widget data value to reflect it on UI.

        :param render_lib: The library to use for rendering.
        :type render_lib: func
        :param widget_settings: The widget settings.
        :type widget_settings: object
        """
        start_time = systime.time()
        telemetry_values = self._get_telemetry_values(self._refresh_widget)
        with _TelemetryLogger.log_activity(_logger,
                                           "train.widget.refresh",
                                           custom_dimensions=telemetry_values) as activity_logger:
            lastError = None
            lastErrorCount = 0
            while True:
                def update_mini_widget(data):
                    from IPython.display import update_display
                    import json
                    bundle = {
                        "application/aml.mini.widget.v1": json.dumps(data)
                    }
                    update_display(bundle, display_id=self.miniWidgetHandle.display_id, raw=True)
                try:
                    activity_logger.info(("Getting widget data..."))
                    widget_data = self.get_widget_data(widget_settings)
                    widget_data["loading"] = False
                    activity_logger.info(("Rendering the widget..."))
                    if render_lib is not None:
                        render_lib(self.widget_instance.get_html())
                    else:
                        update_mini_widget(widget_data)
                    self.widget_instance.error = ''
                    # if self._should_stop_refresh(widget_data):
                    #     activity_logger.info(("Stop auto refreshing..."))
                    #     self.widget_instance.is_finished = True
                    #     if render_lib is None:
                    #         widget_data = self.get_widget_data(widget_settings)
                    #         widget_data["loading"] = False
                    #         update_mini_widget(widget_data)
                    #     break
                except Exception as e:
                    # only check exception type instead of value to avoid timestamp or some dynamic content
                    if type(e) == type(lastError):
                        lastErrorCount += 1
                    else:
                        lastError = e
                        lastErrorCount = 0

                    if lastErrorCount > 2:
                        if self.isDebug:
                            self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))
                        else:
                            self.widget_instance.error = repr(traceback.format_exception_only(type(e), e))

                        if not render_widget:
                            raise
                        break
                    update_mini_widget(repr(e))

                time_to_sleep = os.environ.get(WIDGET_REFRESH_TIME_OVERRIDE)
                time_to_sleep = self.widget_sleep_time if time_to_sleep is None else time_to_sleep
                alpha = min(1, (systime.time() - start_time) / 3600.0)
                self.widget_sleep_time = self.widget_sleep_time_updater(alpha)
                systime.sleep(time_to_sleep)

    def get_widget_data(self, widget_settings=None):
        """Abstract method for retrieving data to be rendered by widget."""
        pass

    # def _should_stop_refresh(self, widget_data):
    #     return datetime.now(timezone.utc).timestamp() - self.widget_instance.heartbeat_timestamp > 300

    def _register_events(self):
        self._register_event(self._on_heartbeat_change, "heartbeat")

    def _register_event(self, callback, traitlet_name):
        self.widget_instance.observe(callback, names=traitlet_name)

    def _get_default_setting(self):
        send_telemetry, level = get_diagnostics_collection_info()
        return {"childWidgetDisplay": "popup",
                "send_telemetry": send_telemetry,
                "log_level": level,
                "sdk_version": azureml.core.VERSION}

    def _get_telemetry_values(self, func):
        telemetry_values = {}

        # client common...
        telemetry_values['amlClientType'] = 'azureml-train-widget'
        telemetry_values['amlClientFunction'] = func.__name__
        telemetry_values['amlClientModule'] = self.__class__.__module__
        telemetry_values['amlClientClass'] = self.__class__.__name__
        telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
        telemetry_values['amlClientSessionId'] = _ClientSessionId

        return telemetry_values

    def _on_heartbeat_change(self, change):
        self.widget_instance.heartbeat_timestamp = change.new
