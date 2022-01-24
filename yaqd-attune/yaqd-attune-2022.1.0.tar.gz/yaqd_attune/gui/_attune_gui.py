from functools import partial

from qtpy import QtWidgets, QtCore  # type: ignore
import qtypes  # type: ignore

import yaqc_qtpy  # type: ignore
from yaqc_qtpy import _plot, qtype_items  # noqa
import WrightTools as wt  # type: ignore
import attune  # type: ignore

import yaq_traits  # type: ignore


class AttuneGUI(QtWidgets.QSplitter):
    def __init__(self, qclient: yaqc_qtpy.QClient):
        super().__init__()
        self.units = "nm"  # TODO synchronous getter calls at startup?
        self.arr = None
        self.plot_widget = yaqc_qtpy._plot.Plot1D(yAutoRange=True)
        self.plot_v_line = self.plot_widget.add_infinite_line(angle=90, hide=False)
        self.tune_enum = qtypes.Enum("Tune")
        self.instrument_item = qtypes.Null("instrument")
        allowed_values = ["wn"] + list(wt.units.get_valid_conversions("wn"))
        self.plot_units = qtypes.Enum(
            "Units", value={"value": self.units, "allowed": allowed_values}
        )
        self.qclient = qclient
        self.qclient.get_instrument.finished.connect(self.on_get_instrument)
        self.qclient.get_instrument()
        self.qclient.get_position.finished.connect(self.on_get_position)
        self.qclient.get_arrangement.finished.connect(self.on_arrangement_updated)
        self._create_main_frame()

    def _create_main_frame(self):
        # container widget
        display_container_widget = QtWidgets.QWidget()
        display_container_widget.setLayout(QtWidgets.QVBoxLayout())
        display_layout = display_container_widget.layout()
        display_layout.setContentsMargins(0, 0, 0, 0)
        self.addWidget(display_container_widget)
        # plot
        self.plot_widget.plot_object.setMouseEnabled(False, False)
        self.plot_curve = self.plot_widget.add_scatter()
        # self.plot_h_line = self.plot_widget.add_infinite_line(angle=0, hide=False)
        display_layout.addWidget(self.plot_widget)

        # right hand tree
        self._tree_widget = qtypes.TreeWidget(width=500)

        # plot control
        display_item = qtypes.Null("Display")
        self._tree_widget.append(display_item)
        self.tune_enum.updated.connect(self.update_plot)
        display_item.append(self.tune_enum)
        self.plot_units.updated.connect(self.update_plot)
        display_item.append(self.plot_units)
        display_item.setExpanded(True)

        # id
        id_item = qtypes.Null("id")
        self._tree_widget.append(id_item)
        for key, value in self.qclient.id().items():
            id_item.append(qtypes.String(label=key, disabled=True, value={"value": value}))
        id_item.setExpanded(True)

        # traits
        traits_item = qtypes.Null("traits")
        self._tree_widget.append(traits_item)
        for trait in yaq_traits.__traits__.traits.keys():
            traits_item.append(
                qtypes.Bool(
                    label=trait, disabled=True, value={"value": trait in self.qclient.traits}
                )
            )

        # properties
        properties_item = qtypes.Null("properties")
        self._tree_widget.append(properties_item)
        qtype_items.append_properties(self.qclient, properties_item)
        properties_item.setExpanded(True)

        # is-homeable
        if "is-homeable" in self.qclient.traits:

            def on_clicked(_, qclient):
                qclient.home()

            home_button = qtypes.Button("is-homeable", value={"text": "home"})
            self._tree_widget.append(home_button)
            home_button.updated.connect(partial(on_clicked, qclient=self.qclient))

        # instrument preview
        self._tree_widget.append(self.instrument_item)

        self._tree_widget.resizeColumnToContents(0)
        self.addWidget(self._tree_widget)

        self.update()
        self.update_plot()

    def update_plot(self):
        if not hasattr(self, "instrument"):
            return
        arr = self.arr
        if arr is None:
            return
        motor_name = self.tune_enum.get_value()
        tune = self.instrument.arrangements[arr][motor_name]
        if not isinstance(tune, attune.Tune):
            return
        # units
        units = self.plot_units.get_value()
        # xi
        colors = tune.independent
        xi = wt.units.converter(colors, tune.ind_units, units)
        # yi
        yi = tune.dependent
        self.plot_widget.set_labels(xlabel=units, ylabel=motor_name)
        self.plot_curve.clear()
        try:
            self.plot_curve.setData(xi, yi)
        except ValueError:
            pass
        self.plot_widget.graphics_layout.update()
        self.qclient.get_position()
        self.update()

    def on_get_instrument(self, json):
        self.instrument = attune.Instrument(**json)
        self.update_plot()
        # TODO empty instrument item
        for name, arr in self.instrument.arrangements.items():
            arr_item = qtypes.String(
                name, value={"value": f"{arr.ind_min:0.3f} - {arr.ind_max:0.3f} nm"}, disabled=True
            )
            self.instrument_item.append(arr_item)
            for tune in arr.tunes.keys():
                arr_item.append(qtypes.Null(tune))

    def on_arrangement_updated(self, arr):
        self.arr = arr
        self.tune_enum.set({"allowed": list(self.instrument[arr].keys())})
        self.update_plot()

    def on_get_position(self, pos):
        self.plot_v_line.setValue(wt.units.convert(pos, self.units, self.plot_units.get_value()))
