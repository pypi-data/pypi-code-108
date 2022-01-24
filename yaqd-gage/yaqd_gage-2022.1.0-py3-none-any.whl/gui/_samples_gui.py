from functools import partial

import toml
import numpy as np
import pyqtgraph  # type: ignore
from qtpy import QtWidgets, QtCore  # type: ignore
import qtypes  # type: ignore

import yaqc_qtpy  # type: ignore
from yaqc_qtpy import _plot, qtype_items  # noqa

import yaq_traits  # type: ignore


class SamplesGUI(QtWidgets.QSplitter):
    def __init__(self, qclient: yaqc_qtpy.QClient):
        super().__init__()
        self.arr = None
        self.qclient = qclient
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.poll)
        self._create_main_frame()
        self.poll()    # once to get some data plotted

    def _create_main_frame(self):
        self.plot_widget = yaqc_qtpy._plot.Plot1D(yAutoRange=True)
        self.scatter = self.plot_widget.add_scatter()
        self.signal_region = pyqtgraph.LinearRegionItem(brush="#b5bd6844", movable=False, pen="#00000000")
        self.plot_widget.plot_object.addItem(self.signal_region)
        self.baseline_region = pyqtgraph.LinearRegionItem(brush="#cc666644", movable=False, pen="#00000000")
        self.plot_widget.plot_object.addItem(self.baseline_region)
        self.signal_mean = self.plot_widget.add_infinite_line(color="#b5bd68", hide=False, angle=0)
        self.baseline_mean = self.plot_widget.add_infinite_line(color="#cc6666", angle=0)
        self.addWidget(self.plot_widget)

        self._tree_widget = qtypes.TreeWidget(width=500)

        # plot control
        plot_item = qtypes.Null("plot")
        self._tree_widget.append(plot_item)
        self._poll_button = qtypes.Button("poll now")
        self._poll_button.updated.connect(self.poll)
        plot_item.append(self._poll_button)
        self._poll_periodically_bool = qtypes.Bool("poll periodically")
        self._poll_periodically_bool.updated.connect(self._on_poll_periodically_updated)
        plot_item.append(self._poll_periodically_bool)
        self._poll_period = qtypes.Float("poll period (s)", value={"value": 1, "minimum": 0, "maximum": 1000})
        self._poll_period.updated.connect(self._on_poll_periodically_updated)
        self.qclient.get_measured_samples.finished.connect(self._on_get_samples)
        plot_item.append(self._poll_period)
        self._channel_selector = qtypes.Enum("channel", value={"allowed": [f"ai{i}" for i in range(4)]})
        self._channel_selector.updated.connect(lambda x: self.poll())
        plot_item.append(self._channel_selector)
        plot_item.setExpanded(True)

        # config
        self.config_item = qtypes.Null("config")
        self._tree_widget.append(self.config_item)
        self.qclient.get_config.finished.connect(self._on_get_config)
        self.qclient.get_config()

        self._tree_widget.resizeColumnToContents(0)
        self.addWidget(self._tree_widget)

    def _on_get_config(self, config):
        config = toml.loads(config)
        self._config = config

        for i, d in enumerate(config["channels"]):
            header = qtypes.Null(f"ai{i}")
            self.config_item.append(header)
            header.append(qtypes.Integer("range (mV)", disabled=True, value={"value": d["range"]}))
            header.append(qtypes.Enum("coupling", disabled=True, value={"value": d["coupling"], "allowed": ["AC", "DC"]}))
            header.append(qtypes.Float("dc offset (V)", disabled=True, value={"value": d["dc_offset"]}))
            header.append(qtypes.Integer("signal start index", disabled=True, value={"value": d["signal_start_index"]}))
            header.append(qtypes.Integer("signal stop index", disabled=True, value={"value": d["signal_stop_index"]}))
            header.append(qtypes.Bool("use baseline", disabled=True, value={"value": d["use_baseline"]}))
            header.append(qtypes.Integer("baseline start index", disabled=True, value={"value": d["baseline_start_index"]}))
            header.append(qtypes.Integer("baseline stop index", disabled=True, value={"value": d["baseline_stop_index"]}))
            header.append(qtypes.Bool("invert", disabled=True, value={"value": d["invert"]}))

            header.setExpanded(True)
    
        self.config_item.setExpanded(True)
        self._tree_widget.resizeColumnToContents(0)

    def _on_get_samples(self, samples):
        channel_name = self._channel_selector.get_value()
        channel_index = int(channel_name[-1])
        yi = samples[self._channel_selector.get_value()]
        xi = np.arange(yi.size)
        self.scatter.setData(xi, yi)
        signal_start_index = self._config["channels"][channel_index]["signal_start_index"]
        signal_stop_index = self._config["channels"][channel_index]["signal_stop_index"]
        self.signal_region.setRegion((signal_start_index - 0.5, signal_stop_index + 0.5))
        self.signal_mean.setValue(np.mean(yi[signal_start_index:signal_stop_index]))
        if self._config["channels"][channel_index]["use_baseline"]:
            self.baseline_region.show()
            self.baseline_mean.show()
            baseline_start_index = self._config["channels"][channel_index]["baseline_start_index"]
            baseline_stop_index = self._config["channels"][channel_index]["baseline_stop_index"]
            self.baseline_region.setRegion((baseline_start_index - 0.5, baseline_stop_index + 0.5))
            self.baseline_mean.setValue(np.mean(yi[baseline_start_index:baseline_stop_index]))
        else:
            self.baseline_region.hide()
            self.baseline_mean.hide()

    def _on_poll_periodically_updated(self, value):
        if self._poll_periodically_bool.get_value():
            self._timer.start(self._poll_period.get_value() * 1000)
        else:
            self._timer.stop()

    def poll(self):
        self.qclient.get_measured_samples()
