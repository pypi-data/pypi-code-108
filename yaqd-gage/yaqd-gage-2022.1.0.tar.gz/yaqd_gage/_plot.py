import sys

import numpy as np  # type: ignore
import pyqtgraph as pg  # type: ignore
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets  # type: ignore
import time
import pyqtgraph.graphicsItems.ScatterPlotItem  # type: ignore
import yaqc  # type: ignore
import toml


def update():
    try:
        global measurement_id
        current_id = gage.get_measurement_id()
        if current_id <= measurement_id:
            return
        else:
            measurement_id = current_id
        y = gage.get_measured_samples()[f"channel{channel_index}"]
        x = np.arange(y.size)
        all_samples.setData(x=x, y=y)
        measurement = gage.get_measured()

        legend.getLabel(all_samples).setText(str(measurement[f"channel{channel_index}"]))
        legend.getLabel(signal_samples).setText(str(measurement[f"channel{channel_index}_signal"]))

        baseline = -0.2887
        legend.getLabel(ratio_item).setText(
            str(
                (measurement[f"channel{channel_index}_signal"] - baseline)
                / (measurement[f"channel{channel_index}_baseline"] - baseline)
            )
        )
        # signal_samples
        start = config["channels"][channel_index - 1]["signal_start_index"]
        stop = config["channels"][channel_index - 1]["signal_stop_index"]
        yy = y[start:stop]
        xx = x[start:stop]
        signal_samples.setData(x=xx, y=yy)

        # baseline_samples
        if config["channels"][channel_index - 1]["use_baseline"]:
            start = config["channels"][channel_index - 1]["baseline_start_index"]
            stop = config["channels"][channel_index - 1]["baseline_stop_index"]
            yy = y[start:stop]
            xx = x[start:stop]
            baseline_samples.setData(x=xx, y=yy)
            legend.getLabel(baseline_samples).setText(
                str(measurement[f"channel{channel_index}_baseline"])
            )
    except Exception as e:
        print(e)
        time.sleep(0.1)


global measurement_id
measurement_id = -1

gage = yaqc.Client(39003)
config = toml.loads(gage.get_config())


def update_config():
    global config
    config = toml.loads(gage.get_config())


gage.register_connection_callback(update_config)

app = pg.mkQApp()
p = pg.PlotWidget()
p.show()

all_samples = pg.ScatterPlotItem(brush=pg.mkBrush(color="#ffffff44"), pen=None)
all_samples = pg.ScatterPlotItem(brush=pg.mkBrush(color="#ffffff44"), pen=None)
p.addItem(all_samples)
signal_samples = pg.ScatterPlotItem(label="signal", brush=pg.mkBrush(color="g"), pen=None)
p.addItem(signal_samples)
baseline_samples = pg.ScatterPlotItem(label="baseline", brush=pg.mkBrush(color="r"), pen=None)
p.addItem(baseline_samples)

legend = p.addLegend(labelTextSize="36pt")
sig_legend = legend.addItem(signal_samples, "signal")
baseline_legend = legend.addItem(baseline_samples, "no baseline")
diff_legend = legend.addItem(all_samples, "diff")
ratio_item = pg.ScatterPlotItem()
ratio_legend = legend.addItem(ratio_item, "ratio")
legend.show()


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)


def main():
    global channel_index
    channel_index = int(sys.argv[-1])
    pg.mkQApp().exec_()


if __name__ == "__main__":
    main()
