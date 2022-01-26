# -*- coding: utf-8 -*-
import os
import copy
import traceback
import subprocess

import numpy as np

from qtpy import QtGui, QtWidgets
from qtpy import QtCore
from qtpy.QtCore import Signal
from qtpy.QtCore import Qt, QRegularExpression, QTimer
from qtpy.QtWidgets import QStyle, QFileDialog, QFontDialog
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QFont
import pyqtgraph as pg

# NOTE: must be imported after pyqt or else config is reset
import logging

from . import __version__
from ._qt import load_ui
from . import const
from . import util
from .data import DataStore
from .plot import NDScopePlot
from .trigger import Trigger
from .crosshair import Crosshair
from . import export
from . import dialog
from . import channel_select


logger = logging.getLogger('SCOPE')

##################################################
# CONFIG


if os.getenv('ANTIALIAS'):
    pg.setConfigOption('antialias', True)
    logger.info("Anti-aliasing ENABLED")
# pg.setConfigOption('leftButtonPan', False)
# see also ViewBox.setMouseMode(ViewBox.RectMode)
# file:///usr/share/doc/python-pyqtgraph-doc/html/graphicsItems/viewbox.html#pyqtgraph.ViewBox.setMouseMode


STATUS_STYLES = {
    "data": "background: rgba(0,100,0,100);",
    "msg": "background: rgba(0,0,100,100);",
    "error": "background: rgba(255,0,0,255); color: black; font-weight: bold;",
}


TREND_OPTIONS = [
    'auto',
    'raw',
    'sec',
    'min',
]


class BuildChannelModelsThread(QtCore.QThread):
    done = Signal('PyQt_PyObject')

    def __init__(self, channels):
        super().__init__()
        self.channels = channels

    def run(self):
        channel_list = []
        all_online = True
        for chan in self.channels.values():
            channel_list.append(chan)
            all_online &= chan.online
        #channel_list = list(sorted(self.channels.values(), key=lambda c: c.name))
        tree_model = channel_select.AvailableChannelTreeModel(channel_list)
        table_model = channel_select.AvailableChannelTableModel(channel_list)
        self.done.emit((tree_model, table_model, all_online))

##################################################


class NDScope(*load_ui('scope.ui')):
    _channel_models_ready = Signal()
    _plots_updated = Signal()
    _export_complete = Signal()

    def __init__(self):
        """initilize NDScope object

        """
        super().__init__(None)
        self.setupUi(self)

        server, self.server_formatted = util.format_nds_server_string()
        logger.info(f"version {__version__}")
        logger.info(f"server {server}")
        self.labelServer = QtWidgets.QLabel(f"{self.server_formatted}")
        self.labelServer.setToolTip("NDS server")
        # add a little space
        self.statusBar.addWidget(QtWidgets.QLabel())
        self.statusBar.addWidget(self.labelServer)
        self.labelChannelCount = QtWidgets.QLabel("[?]")
        self.labelChannelCount.setToolTip("channel count")
        # the '1' add stretch to push the next label to the right side
        self.statusBar.addWidget(self.labelChannelCount, 1)
        self.statusBar.addWidget(QtWidgets.QLabel(f"ndscope {__version__}"))
        self.statusClearButton = QtWidgets.QPushButton("clear")
        # permanent widgets are added to the right side
        self.statusBar.addPermanentWidget(self.statusClearButton)
        self.statusBar.messageChanged.connect(self.status_clear_callback)
        self.statusClearButton.clicked.connect(self.status_clear)
        self.status_clear()

        self.t0 = 0
        self._error = False
        self._dialogs = {}
        self._channel_tree_model = None
        self._channel_table_model = None
        self._channel_select_dialog = None
        self._channel_list_window = None
        self._bcsmt = None

        # FIXME: HACK: this is an attempt to bypass the following bug:
        #
        # Traceback (most recent call last):
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/GraphicsObject.py", line 23, in itemChange
        #     self.parentChanged()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/GraphicsItem.py", line 440, in parentChanged
        #     self._updateView()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/GraphicsItem.py", line 492, in _updateView
        #     self.viewRangeChanged()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/PlotDataItem.py", line 671, in viewRangeChanged
        #     self.updateItems()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/PlotDataItem.py", line 483, in updateItems
        #     x,y = self.getData()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/PlotDataItem.py", line 561, in getData
        #     if view is None or not view.autoRangeEnabled()[0]:
        # AttributeError: 'GraphicsLayoutWidget' object has no attribute 'autoRangeEnabled'
        def autoRangeEnabled():
            return False, False
        self.graphView.autoRangeEnabled = autoRangeEnabled

        self.graphView.dragEnterEvent = lambda event: event.setAccepted(event.mimeData().hasFormat('text/plain'))

        ##########
        # data and data retrieval

        self.data = DataStore()
        self.last_cmd = (None, {})
        self.last_data = (None, 0, 0)

        self.data.signal_channel_list_ready.connect(self._channel_list_ready_callback)
        self.data.signal_channel_add.connect(self._channel_add_callback)
        self.data.signal_channel_remove.connect(self._channel_remove_callback)

        self.data.signal_data_online_start.connect(self._data_online_start)
        self.data.signal_data_retrieve_start.connect(self._data_retrieve_start)
        self.data.signal_data.connect(self._update_plots)
        self.data.signal_data_online_done.connect(self._data_online_done)
        self.data.signal_data_retrieve_done.connect(self._data_retrieve_done)

        ##########
        # window/range entry

        def NonEmptyValidator():
            return QtGui.QRegularExpressionValidator(QRegularExpression('.+'))

        self.entryT0GPS.textEdited.connect(self.update_entryT0Greg)
        self.entryT0GPS.setValidator(QtGui.QDoubleValidator())
        self.entryT0GPS.returnPressed.connect(self.update_t0)

        self.entryT0Greg.textEdited.connect(self.update_entryT0GPS)
        self.entryT0Greg.setValidator(NonEmptyValidator())
        self.entryT0Greg.returnPressed.connect(self.update_t0)

        self.buttonT0Now.clicked.connect(self.set_entryT0)

        self.entryWindowStart.setValidator(QtGui.QDoubleValidator())
        self.entryWindowStart.returnPressed.connect(self.update_window)

        self.entryWindowEnd.setValidator(QtGui.QDoubleValidator())
        self.entryWindowEnd.returnPressed.connect(self.update_window)

        self.entryStartGPS.textEdited.connect(self.update_entryStartGreg)
        self.entryStartGPS.setValidator(QtGui.QDoubleValidator())
        self.entryStartGPS.returnPressed.connect(self.update_range)

        self.entryStartGreg.textEdited.connect(self.update_entryStartGPS)
        self.entryStartGreg.setValidator(NonEmptyValidator())
        self.entryStartGreg.returnPressed.connect(self.update_range)

        self.entryEndGPS.setValidator(QtGui.QDoubleValidator())
        self.entryEndGPS.textEdited.connect(self.update_entryEndGreg)
        self.entryEndGPS.returnPressed.connect(self.update_range)

        self.entryEndGreg.textEdited.connect(self.update_entryEndGPS)
        self.entryEndGreg.setValidator(NonEmptyValidator())
        self.entryEndGreg.returnPressed.connect(self.update_range)

        self.buttonEndNow.clicked.connect(self.set_entryEnd)

        self.fetchButton1.clicked.connect(self.update_t0)
        self.fetchButton2.clicked.connect(self.update_range)

        ##########
        # trend

        self.trendSelectGroup = QtWidgets.QButtonGroup()
        # NOTE: the numbers correspond to indices in TREND_OPTIONS
        self.trendSelectGroup.addButton(self.trendAutoSelect, 0)
        self.trendSelectGroup.addButton(self.trendRawSelect, 1)
        self.trendSelectGroup.addButton(self.trendSecSelect, 2)
        self.trendSelectGroup.addButton(self.trendMinSelect, 3)
        self.trendSelectGroup.buttonClicked.connect(self._trend_select)

        self.trendRawSecThresh.setValidator(QtGui.QIntValidator())
        self.trendRawSecThresh.setText(str(const.TREND_TRANS_THRESHOLD['raw/sec']))
        self.trendRawSecThresh.returnPressed.connect(self._set_trend_rawsec)

        self.trendSecMinThresh.setValidator(QtGui.QIntValidator())
        self.trendSecMinThresh.setText(str(const.TREND_TRANS_THRESHOLD['sec/min']))
        self.trendSecMinThresh.returnPressed.connect(self._set_trend_secmin)

        ##########
        # axis

        self.timeAxisModeButtonGroup.buttonClicked.connect(self._set_time_axis_mode)

        ##########
        # trigger

        self.trigger = Trigger()
        self.trigger.sigLevelChanged.connect(self._update_triggerLevel)
        self.triggerLevel.setValidator(QtGui.QDoubleValidator())
        self.triggerLevel.returnPressed.connect(self._set_trigger_level)
        self.triggerResetLevel.clicked.connect(self.reset_trigger_level)
        self.triggerSingle.clicked.connect(self.trigger.set_single)
        self.triggerInvert.clicked.connect(self.trigger.set_invert)
        self.triggerGroup.toggled.connect(self._toggle_trigger)

        ##########
        # crosshair

        self.crosshair = Crosshair()
        self.crosshair.signal_position.connect(self._update_crosshair_entry)
        self._crosshair_proxy = None
        self.crosshairGroup.toggled.connect(self._toggle_crosshair)

        ##########
        # style

        self.fontSizeSelect.valueChanged.connect(self.set_font_size)
        self.colorModeButtonGroup.buttonClicked.connect(self.set_color_mode)

        ##########
        # export

        self.exportButton.clicked.connect(self.export)
        self.exportPath.returnPressed.connect(self._export_save_handler)
        self.exportSaveButton.clicked.connect(self._export_save_handler)
        self.exportShowButton.clicked.connect(self._export_show_handler)
        self.exportButton2.clicked.connect(self.export)

        ##########
        # controls

        self.controlBar.hide()
        self.controlExpandButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarShadeButton))
        self.controlExpandButton.setText('')
        self.controlExpandButton.clicked.connect(self._controlExpand)
        self.controlCollapseButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarUnshadeButton))
        self.controlCollapseButton.setText('')
        self.controlCollapseButton.clicked.connect(self._controlCollapse)

        self.startButton.clicked.connect(self.start)
        self.startButton2.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.stopButton2.clicked.connect(self.stop)
        self.resetRangeButton.clicked.connect(self.reset)
        self.resetRangeButton2.clicked.connect(self.reset)

        ##########
        # button icons
        # FIXME: should set this in .ui somehow

        self.startButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.startButton2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton2.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        # self.fetchButton1.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        # self.fetchButton2.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        # self.resetRangeButton.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        # self.resetRangeButton2.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.exportButton.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.exportSaveButton.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.exportShowButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        self.exportButton2.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

        ##########
        # initial config

        self.setWindowTitle('ndscope')
        self._base_ui()
        self.plotLayout = self.graphView.addLayout()
        self.graphView.nextRow()
        self.referenceTimeLabel = self.graphView.addLabel("t0")
        self.set_color_mode('dark')
        self.set_font_size(10)
        self.add_plot()
        self._set_t0(util.gpstime_parse('now').gps())
        self.set_window(-2, 0)
        self.last_cmd = ('start', {'window': self.get_window()})

    ##########

    def single_shot_export(self, path):
        """Export scene to path then exit

        This is intended to be called before show() at app
        initialization to setup the export of the scene after an
        initial data fetch is complete.

        """
        # this prevents the data object from fetching the channel list
        self.data.available_channels = True
        def _done_export():
            QtCore.QTimer.singleShot(1, lambda: self.export(path))
        self._plots_updated.connect(_done_export)
        self._export_complete.connect(QApplication.quit)

    ##########

    def set_font(self, font):
        self.setFont(font)
        self.fontSizeSelect.setValue(font.pointSize())
        referenceTimeLabelFont = QFont(font)
        referenceTimeLabelFont.setPointSize(font.pointSize() + 2)
        self.referenceTimeLabel.item.setFont(referenceTimeLabelFont)
        self.crosshair.set_font(font)
        self.trigger.set_font(font)
        for plot in self.plots:
            plot.set_font(font)

    def set_font_size(self, size):
        """Set font size for plots"""
        font = self.font()
        font.setPointSize(size)
        self.set_font(font)

    @property
    def _color_mode(self):
        if self.darkModeButton.isChecked():
            return 'dark'
        elif self.lightModeButton.isChecked():
            return 'light'

    def set_color_mode(self, mode):
        """set color mode to "light" or "dark"

        """
        if isinstance(mode, QtWidgets.QRadioButton):
            mode = mode.text()
        fg = const.COLOR_MODE[mode]['fg']
        bg = const.COLOR_MODE[mode]['bg']
        self.graphView.setBackground(bg)
        self.referenceTimeLabel.setAttr('color', fg)
        self.referenceTimeLabel.setText(self.referenceTimeLabel.text)
        self.crosshair.set_color_mode(mode)
        self.trigger.set_color_mode(mode)
        for plot in self.plots:
            plot.set_color_mode(mode)
        if mode == 'light':
            self.lightModeButton.setChecked(True)
        elif mode == 'dark':
            self.darkModeButton.setChecked(True)

    ##########

    def _base_ui(self):
        # UI with no channels
        self.startButton.setEnabled(False)
        self.startButton2.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.stopButton2.setEnabled(False)
        self.resetRangeButton.setEnabled(False)
        self.resetRangeButton2.setEnabled(False)
        self.windowTab.setEnabled(False)
        self.rangeTab.setEnabled(False)
        self.triggerTab.setEnabled(False)
        self.crosshairTab.setEnabled(False)
        self.axisTab.setEnabled(True)
        self.exportTab.setEnabled(False)
        self.exportButton2.setEnabled(False)

    def _offline_ui(self):
        # UI with channels
        self.startButton.setEnabled(True)
        self.startButton2.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.stopButton2.setEnabled(False)
        self.resetRangeButton.setEnabled(True)
        self.resetRangeButton2.setEnabled(True)
        self.windowTab.setEnabled(True)
        self.rangeTab.setEnabled(True)
        self.triggerTab.setEnabled(False)
        self.crosshairTab.setEnabled(True)
        self.axisTab.setEnabled(True)
        self.exportTab.setEnabled(True)
        self.exportButton2.setEnabled(True)

    def _online_ui(self):
        # UI when online
        self.startButton.setEnabled(False)
        self.startButton2.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.stopButton2.setEnabled(True)
        self.resetRangeButton.setEnabled(True)
        self.resetRangeButton2.setEnabled(True)
        self.windowTab.setEnabled(True)
        self.rangeTab.setEnabled(False)
        self.triggerTab.setEnabled(True)
        self.crosshairTab.setEnabled(False)
        self.axisTab.setEnabled(False)
        self.exportTab.setEnabled(False)
        self.exportButton2.setEnabled(False)

    ##########
    # status bar

    def status_clear(self, text=None):
        self._error = False
        self.statusBar.setStyleSheet("")
        self.statusClearButton.setVisible(False)
        self.statusBar.clearMessage()

    def status_clear_callback(self, text):
        # this method is connected to the statusBar.messageChanged
        # slot, so that the status bar is reset when a temporary
        # message is cleared. but we only want to reset when it's
        # cleared (text is empty), not when a new message is added.
        if text == '':
            self.status_clear('MSG')

    def status_message(self, msg, timeout=0, style="msg", clear_button=False, log=True):
        self._error = False
        if log:
            logger.warning(msg)
        style = STATUS_STYLES.get(style)
        if style:
            self.statusBar.setStyleSheet(f"QStatusBar{{{style}}}")
        self.statusBar.showMessage(msg, int(timeout*1000))
        if clear_button:
            self.statusClearButton.setVisible(True)
        else:
            self.statusClearButton.setVisible(False)

    def status_error(self, msg):
        logger.error(msg)
        self.statusBar.setStyleSheet(STATUS_STYLES["error"])
        self.statusBar.showMessage(msg)
        self.statusClearButton.setVisible(True)
        self._error = True

    ##########
    # dialogs

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for dialog in self._dialogs.values():
            dialog.move(0, 0)
            dialog.resize(self.width(), self.height())

    def _dialog_create(self, name, d, callback=None):
        self._dialogs[name] = dialog.DialogOverlayWidget(d, self)
        if callback:
            self._dialogs[name].done.connect(callback)
        self._dialogs[name].show()

    def _dialog_cleanup(self, name):
        if name not in self._dialogs:
            return
        try:
            self._dialogs[name].done.disconnect()
        except AttributeError:
            pass
        self._dialogs[name].close()
        del self._dialogs[name]

    def auth_dialog(self):
        if 'auth' in self._dialogs and self._dialogs['auth'].isVisible():
            return
        d = dialog.NDSAuthDialog(self)
        self._dialog_create('auth', d, callback=self.auth_dialog_result)
        d.usernameEntry.setFocus()

    def auth_dialog_result(self, result=None):
        self._dialog_cleanup('auth')
        if not result:
            # FIXME: this is not the right place to clean this stuff
            # up, but unclear where else it should be done.
            self._dialog_cleanup('channel-wait')
            self._channel_models_ready.disconnect()
            return
        self.data.fetch_channel_list_async()
        self.reset()

    def ontape_dialog(self):
        if 'tape' in self._dialogs and self._dialogs['tape'].isVisible():
            return
        d = dialog.NDSOnTapeDialog(self)
        self._dialog_create('tape', d, callback=self.ontape_dialog_result)

    def ontape_dialog_result(self, result=None):
        self._dialog_cleanup('tape')
        if not result:
            return
        os.environ['NDS2_CLIENT_ALLOW_DATA_ON_TAPE'] = 'TRUE'
        self.reset()

    ##########
    # controls box

    def _controlExpand(self):
        self.controlBarSmall.hide()
        self.controlBar.show()

    def _controlCollapse(self):
        self.controlBar.hide()
        self.controlBarSmall.show()

    ##########
    # CHANNELS AND PLOTS

    @property
    def plots(self):
        """list of scope plots"""
        return list(self.plotLayout.items.keys())

    @property
    def plot0(self):
        """base plot at (0,0) location"""
        return self.plotLayout.getItem(0, 0)

    def get_plot_locations(self):
        """iterator of plot locations as (row, col) tuples"""
        for plot, cells in self.plotLayout.items.items():
            tabspec = util.cells_to_tabspec(cells)
            yield plot, (tabspec['row'], tabspec['col'])

    def get_plot_location(self, plot):
        """return plot location as (row, col)"""
        for p, loc in self.get_plot_locations():
            if plot == p:
                return loc

    def add_plot(self, channels=None, yrange=None, **kwargs):
        """Add plot to the scope

        If provided `channels` should be a list of channel:property
        dicts to add to the plot on initialization.

        """
        self.status_clear()
        logger.info(f"creating plot {kwargs}...")

        # check that there's not already a plot at the requested location
        loc = (kwargs.get('row'), kwargs.get('col'))
        for plot, ploc in self.get_plot_locations():
            if loc == ploc:
                raise ValueError(f"Plot already exists at location {ploc}.")

        plot = NDScopePlot(self.data, loc=loc)
        plot.set_font(self.font())
        plot.set_color_mode(self._color_mode)
        plot.channel_select_request.connect(self.select_channels)
        plot.channel_add_complete.connect(self._channel_add_complete)
        plot.new_plot_request.connect(self._add_plot_handler)
        plot.remove_plot_request.connect(self.remove_plot)
        plot.t0_reset.connect(self.reset_t0_relative)
        plot.t_cursors_enabled.connect(self._update_t_cursors)
        plot.t_cursor_moved.connect(self._update_t_cursor)

        # FIXME: where to add if row/col not specified?  need some
        # sort of layout policy
        self.plotLayout.addItem(
            plot, **kwargs,
        )

        # HACK: this is how to remove the "export" command from the
        # context menu
        plot.scene().contextMenu = None

        # connect mouse gesture signals
        if plot == self.plot0:
            logger.info("connecting plot 0...")
            #self.plot0.sigXRangeChanged.connect(self.XRangeChanged_callback)
            self.XRangeChanged_callback_proxy = pg.SignalProxy(
                self.plot0.sigXRangeChanged,
                rateLimit=1,
                slot=self.XRangeChanged_callback,
            )
        else:
            # set time axis mode
            plot.axes['bottom']['item'].t0 = self.t0
            plot.axes['bottom']['item'].setTickStringsMode(self.active_time_axis_mode)

            logger.info("connecting to plot 0...")
            plot.setXLink(self.plot0)

        if channels:
            # each channel should be a {name: curve_params} dict
            for chan in channels:
                name, ckwargs = list(chan.items())[0]
                ckwargs = ckwargs or {}
                plot.add_channel(name, **ckwargs)

        if self.plot0.t_cursors:
            plot.enable_t_cursors()
            plot.t_cursors.set_values(*self.plot0.t_cursors.get_values())

        # set y ranges
        if yrange in [None, 'auto']:
            plot.enableAutoRange(axis='y')
        else:
            plot.setYRange(*yrange)

        return plot

    def _add_plot_handler(self, recv):
        """handler to add new plot based on signal from plotMenu"""
        ref_plot, new_loc, plot_kwargs = recv
        occupied_cells = set()
        for plot, cells in self.plotLayout.items.items():
            occupied_cells.update(cells)
            if plot == ref_plot:
                tabspec = util.cells_to_tabspec(cells)
        rowcol = (tabspec['row'], tabspec['col'])
        while rowcol in occupied_cells:
            row, col = rowcol
            if new_loc == 'row':
                col += 1
            elif new_loc == 'col':
                row += 1
            rowcol = (row, col)
        plot_kwargs['row'] = row
        plot_kwargs['col'] = col
        self.add_plot(**plot_kwargs)

    def remove_plot(self, plot, _force=False):
        """remove plot from layout"""
        self.status_clear()
        loc = self.get_plot_location(plot)
        logger.info(f"removing plot: {loc}")
        if _force is not True:
            if len(self.plots) == 1:
                self.status_error("Can not remove last plot.")
                return
            if loc == (0, 0):
                self.status_error("Can not remove (0,0) plot.")
                return
        # first remove all channels
        # make copy of list cause we'll be changing it
        for chan in list(plot.channels.keys()):
            plot.remove_channel(chan)
        self.plotLayout.removeItem(plot)

    def plots4chan(self, channel):
        """Return list of plots displaying channel"""
        plots = []
        for plot in self.plots:
            if channel in plot.channels:
                plots.append(plot)
        return plots

    def _channel_list_ready_callback(self):
        logger.debug("building channel models...")
        t = BuildChannelModelsThread(self.data.available_channels)
        t.done.connect(self._channel_models_ready_callback)
        t.start()
        # hold a reference to the thread until it's done
        self._bcsmt = t

    def _channel_models_ready_callback(self, recv):
        self._channel_tree_model, self._channel_table_model, all_online = recv
        nchannels = len(self.data.available_channels)
        channel_list_widget = channel_select.ChannelListWidget(self._channel_tree_model, self._channel_table_model)
        channel_list_widget.title.setText(f"Channel list for <span style='font-weight: bold'>{self.server_formatted}</span> [{nchannels} channels]")
        self._channel_select_dialog = channel_select.ChannelSelectDialog(channel_list_widget, self)
        self._bcsmt = None
        logger.debug("channel select dialog ready.")
        self.labelChannelCount.setText(f"[{nchannels} channels]")
        self._channel_models_ready.emit()

    def select_channels(self, plot=None):
        """Present the channel select dialog

        Will block the scope to wait for the channel list if it's not
        available yet.

        If no plot is specified, assume plot0

        """
        if 'select' in self._dialogs and self._dialogs['select'].isVisible():
            return
        if not plot:
            plot = self.plot0
        if self._channel_select_dialog:
            self._channel_select_present(plot)
        else:
            if not self._bcsmt:
                self.data.fetch_channel_list_async()
            self._channel_select_wait(plot)

    def _channel_select_wait(self, plot):
        d = QtWidgets.QLabel("waiting for channel list...", self)
        d.setMargin(10)
        d.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self._dialog_create('channel-wait', d)
        self._channel_models_ready.connect(lambda: self._channel_select_wait_done(plot))

    def _channel_select_wait_done(self, plot):
        self._dialog_cleanup('channel-wait')
        self._channel_select_present(plot)

    def _channel_select_present(self, plot):
        self._channel_select_dialog.setSelectedChannelList(plot.channels)
        self._channel_select_dialog.setTitlePlot(self.get_plot_location(plot))
        self._dialog_create(
            'select', self._channel_select_dialog,
            callback=lambda chans: self._channel_select_dialog_result(plot, chans),
        )

    # SLOT
    def _channel_select_dialog_result(self, plot, channel_list):
        self._dialog_cleanup('select')
        plot.set_channel_objs(channel_list)

    def _channel_add_callback(self, recv):
        """callback for when channel added"""
        channel, error = recv
        if error:
            self.status_error(error)
            return
        logger.info(f"added channel: {channel}")
        self._update_triggerSelect()

    def _channel_add_complete(self):
        """callback for when a set of channel adds is complete

        This call is signaled when a channel is added via the plot
        menu

        """
        # FIXME: this really needs to be a better condition
        if len(self.data.channels) == 1:
            self.reset()

    def _channel_remove_callback(self, recv):
        """callback for when channel removed from plot"""
        channel, error = recv
        if error:
            self.status_error(error)
            return
        self.status_clear()
        logger.info(f"removed channel: {channel}")
        self._update_triggerSelect()
        if self.data.empty:
            self._base_ui()

    def load_template(self, template):
        """Load scope template from template dictionary

        """
        logger.info(f"loading template...")

        # check the layout to make sure there's a (0,0) plot specified
        for plot in template['plots']:
            loc = (plot.get('row'), plot.get('col'))
            if loc == (0, 0):
                plot0 = plot
                break
        else:
            raise ValueError("Template layout must specify a plot at row=0, col=0")

        title = template.get('window-title')
        if title:
            self.setWindowTitle('ndscope: {}'.format(title))
        font_size = template.get('font-size')
        if font_size:
            self.set_font_size(font_size)
        # FIXME: DEPRECATE
        if 'black-on-white' in template:
            logger.warning("WARNING: Template key 'black-on-white' is deprecated, please use 'color-mode: light' instead.")
            if template.get('black-on-white'):
                self.set_color_mode('light')
            else:
                self.set_color_mode('dark')
        if template.get('color-mode'):
            self.set_color_mode(template.get('color-mode'))

        # clear *all* plots from the scope, including the base 0,0 plot
        logger.info("clearing plots...")
        for p in self.plots:
            self.remove_plot(p, _force=True)

        def add_plot(p):
            y_cursors = p.get('y-cursors')
            if 'y-cursors' in p:
                del p['y-cursors']
            plot = self.add_plot(**p)
            if y_cursors:
                plot.enable_y_cursors()
                plot.y_cursors.set_values(*y_cursors)

        # add the (0, 0) plot first
        add_plot(plot0)
        # then add the rest
        for plot in template['plots']:
            loc = (plot['row'], plot['col'])
            if loc == (0, 0):
                continue
            add_plot(plot)

        t_cursors = template.get('t-cursors')
        if t_cursors:
            self.enable_t_cursors()
            self.set_t_cursor_values(*t_cursors)

        time_axis_mode = template.get('time-axis-mode')
        if time_axis_mode:
            self.set_time_axis_mode(time_axis_mode)

        t0 = template.get('t0')
        window = template.get('time-window')
        logger.info(f"t0={t0}, window={window}")
        if t0:
            self.fetch(t0=t0, window=window)
        else:
            self.start(window)

    ##########
    # RANGE AND SPAN

    def get_window(self):
        (xmin, xmax), (ymin, ymax) = self.plot0.viewRange()
        return xmin, xmax

    def get_range(self):
        """tuple of (start, end) times"""
        xmin, xmax = self.get_window()
        start = self.t0 + xmin
        end = self.t0 + xmax
        return start, end

    def get_span(self):
        """time span in seconds"""
        start, end = self.get_range()
        return abs(end - start)

    def preferred_trend(self):
        """preferred trend for the current time span"""
        trend = TREND_OPTIONS[self.trendSelectGroup.checkedId()]
        if trend == 'auto':
            span = self.get_span()
            if span > const.TREND_TRANS_THRESHOLD['sec/min']:
                return 'min'
            elif span > const.TREND_TRANS_THRESHOLD['raw/sec']:
                return 'sec'
            else:
                return 'raw'
        else:
            return trend

    ##########
    # UI

    def start(self, window=None):
        """Start online mode

        """
        logger.info('START')
        self.status_clear()
        if window:
            span = abs(min(window))
        else:
            span = self.get_span()
            window = (-span, 0)
        self.set_window(*window)
        trend = self.preferred_trend()
        if trend == 'min':
            self.status_error("Online minute trends not supported.  Try a smaller window.")
            return
        self.last_cmd = ('start', {'window': window})
        self.data.online_start(trend, span)

    def stop(self):
        """Stop online mode

        """
        logger.info('STOP')
        self.data.online_stop()
        # consider a stop as fetch for the stop range
        self.last_cmd = ('fetch', {'t0': self.t0, 'window': self.get_window()})

    def _data_request(self, force=False):
        ltrend, lstart, lend = self.last_data
        trend = self.preferred_trend()
        start, end = self.get_range()
        if not force \
           and trend == ltrend \
           and start >= lstart \
           and end <= lend:
            return
        self.data.request(trend, (start, end))

    def fetch(self, **kwargs):
        """Fetch data offline

        May specify `t0` and `window`, or `start` and `end`.

        """
        logger.info(f'FETCH: {kwargs}')
        self.data.online_stop()
        if QtWidgets.QApplication.keyboardModifiers() == Qt.ShiftModifier:
            self.data.reset()
        if 't0' in kwargs:
            t0 = kwargs['t0']
            window = kwargs['window']
            start = t0 + window[0]
            end = t0 + window[1]
        else:
            start = kwargs['start']
            end = kwargs['end']
            t0 = max(start, end)
            window = (-abs(start-end), 0)
        self.triggerGroup.setChecked(False)
        self._set_t0(t0)
        self.set_window(window[0], window[1])
        self.last_cmd = ('fetch', {'t0': self.t0, 'window': self.get_window()})
        self._data_request(force=True)

    def reset(self):
        """Reset to last fetch range

        """
        logger.info(f'RESET: {self.last_cmd}')
        if not self.last_cmd[0]:
            return
        for plot in self.plots:
            plot.enableAutoRange(axis='y')
        if self.last_cmd[0] == 'start':
            self.start(**self.last_cmd[1])
        elif self.last_cmd[0] == 'fetch':
            self.fetch(**self.last_cmd[1])

    def XRangeChanged_callback(self, *args):
        """update time range info on X range change

        includes both mouse pan/zoom, but also interal X range
        changes.

        """
        self.updateGPS()
        self.update_entryWindow()
        self.update_tlabel()
        self._data_request()

    def get_entryWindow(self):
        try:
            window = (
                float(self.entryWindowStart.text()),
                float(self.entryWindowEnd.text()),
            )
        except ValueError:
            return
        return window

    def update_t0(self):
        self.update_entryT0GPS()
        try:
            t0 = float(self.entryT0GPS.text())
            window = self.get_entryWindow()
        except ValueError:
            return
        if window is None:
            return
        self.fetch(t0=t0, window=window)

    def update_window(self):
        if self.data.online:
            window = self.get_entryWindow()
            if window is None:
                return
            self._set_window(*window)
            self.last_cmd = ('start', {'window': window})
        else:
            self.update_t0()

    def update_range(self):
        self.update_entryStartGPS()
        self.update_entryEndGPS()
        try:
            start = float(self.entryStartGPS.text())
            end = float(self.entryEndGPS.text())
        except ValueError:
            return
        self.fetch(start=start, end=end)

    ##########

    # SLOT
    def _data_online_start(self, msg):
        self._online_ui()
        if self.triggerGroup.isChecked():
            self._enable_trigger()
        self._disable_crosshair()
        self._set_time_axis_mode('relative')

    # SLOT
    def _data_retrieve_start(self, msg):
        self.status_message(msg, style="data", log=False)
        self.entryT0GPS.setEnabled(False)
        self.entryT0Greg.setEnabled(False)
        self.buttonT0Now.setEnabled(False)
        self.fetchButton1.setEnabled(False)
        self.fetchButton2.setEnabled(False)

    # SLOT
    def _data_online_done(self, signal):
        self._disable_trigger()
        if self.crosshairGroup.isChecked():
            self._enable_crosshair()
        self._reset_time_axis_mode()

    # SLOT
    def _data_retrieve_done(self, signal):
        if self.data.empty:
            self._base_ui()
        elif self.data.online:
            self._online_ui()
        else:
            self._offline_ui()
        error, active = signal
        if error:
            self.status_error(error)
            if 'SASL authentication protocol' in error:
                self.auth_dialog()
            if 'Requested data is on tape' in error:
                self.ontape_dialog()
        if active:
            return
        if not error and not self._error:
            self.status_clear()
        self.entryT0GPS.setEnabled(True)
        self.entryT0Greg.setEnabled(True)
        self.buttonT0Now.setEnabled(True)
        self.fetchButton1.setEnabled(True)
        self.fetchButton2.setEnabled(True)

    ##########
    # PLOTTING

    # SLOT
    def _update_plots(self, recv):
        logger.log(5, f"PLOT: {recv}")

        data, trend, online = recv

        if not data:
            logger.log(5, "CLEAR")
            for plot in self.plots:
                plot.clear_data()
            return

        # if this isn't the trend we need then drop the packet
        preferred_trend = self.preferred_trend()
        if trend != preferred_trend:
            logger.debug(f"DROP {trend} trend packet ({preferred_trend} preferred)")
            return

        self.last_data = (trend,) + data.range

        trigger = None
        if online:
            # if we're online, check for triggers
            if self.trigger.active:
                trigger = self.trigger.check(data)
                if trigger:
                    self._update_triggerTime(trigger)
                    self._set_t0(trigger)

            else:
                self._set_t0(data.range[1])

        for plot in self.plots:
            plot.update(data, self.t0)

        if trigger and self.trigger.single:
            self.stop()

        self._plots_updated.emit()

    def update_tlabel(self):
        # span = self.get_span()
        # mod = ''
        # try:
        #     prec = int(np.round(np.log10(span))) - 2
        # except OverflowError:
        #     span = 2.385e-07
        #     prec = -9
        #     mod = '<'
        # sstr = '{mod}{span}'.format(
        #     mod=mod,
        #     span=util.seconds_time_str(span, prec),
        # )
        self.referenceTimeLabel.setText(
            #'t0 = {greg} [{gps:0.4f}], {span} span'.format(
            't0 = {greg} [{gps:0.4f}]'.format(
                greg=util.gpstime_str_greg(
                    util.gpstime_parse(self.t0),
                    fmt=const.DATETIME_FMT,
                ),
                gps=self.t0,
                #span=sstr,
            )
        )

    def _set_t0(self, t0):
        dt = self.t0 - t0
        self.t0 = t0
        logger.log(5, f"t0 = {t0}")
        self.update_tlabel()
        self.updateGPS()
        self.crosshair.update_t(dt)

    def reset_t0(self):
        start, end = self.get_range()
        t0 = (start+end)/2
        xd = (end-start)/2
        self.fetch(t0=t0, window=(-xd, xd))

    def reset_t0_relative(self, val):
        if self.data.online:
            return
        start, end = self.get_window()
        t0 = self.t0 + val
        start -= val
        end -= val
        self.fetch(t0=t0, window=(start, end))
        t_cursors = self.get_t_cursor_values()
        if t_cursors:
            t1, t2 = t_cursors
            t1 -= val
            t2 -= val
            self.set_t_cursor_values(t1, t2)

    def _set_window(self, xmin, xmax):
        logger.debug("set window: {} {}".format(xmin, xmax))
        self.plot0.setXRange(xmin, xmax, padding=0, update=False)

    def set_window(self, xmin, xmax):
        self._set_window(xmin, xmax)
        self.update_entryWindow()

    ##########
    # TIMES

    def updateGPS(self):
        start, end = self.get_range()
        self.set_entryT0(self.t0)
        self.set_entryStart(start)
        self.set_entryEnd(end)

    def set_entryT0(self, time=None):
        if time:
            gt = util.gpstime_parse(time)
        else:
            gt = util.gpstime_parse('now')
        self.entryT0GPS.setText(util.gpstime_str_gps(gt))
        self.entryT0Greg.setText(util.gpstime_str_greg(gt))

    def update_entryT0GPS(self):
        gt = util.gpstime_parse(self.entryT0Greg.text())
        if not gt:
            return
        self.entryT0GPS.setText(util.gpstime_str_gps(gt))

    def update_entryT0Greg(self):
        gt = util.gpstime_parse(self.entryT0GPS.text())
        if not gt:
            return
        self.entryT0Greg.setText(util.gpstime_str_greg(gt))

    def update_entryWindow(self):
        xmin, xmax = self.get_window()
        self.entryWindowStart.setText(f'{xmin:.6f}')
        self.entryWindowEnd.setText(f'{xmax:.6f}')

    def set_entryStart(self, time):
        gt = util.gpstime_parse(time)
        self.entryStartGPS.setText(util.gpstime_str_gps(gt))
        self.entryStartGreg.setText(util.gpstime_str_greg(gt))

    def set_entryEnd(self, time=None):
        if time:
            gt = util.gpstime_parse(time)
        else:
            gt = util.gpstime_parse('now')
        self.entryEndGPS.setText(util.gpstime_str_gps(gt))
        self.entryEndGreg.setText(util.gpstime_str_greg(gt))

    def update_entryStartGPS(self):
        t = self.entryStartGreg.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryStartGPS.setText(util.gpstime_str_gps(gt))

    def update_entryStartGreg(self):
        t = self.entryStartGPS.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryStartGreg.setText(util.gpstime_str_greg(gt))

    def update_entryEndGPS(self):
        t = self.entryEndGreg.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryEndGPS.setText(util.gpstime_str_gps(gt))

    def update_entryEndGreg(self):
        t = self.entryEndGPS.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryEndGreg.setText(util.gpstime_str_greg(gt))

    ##########
    # TREND

    def _trend_select(self, button):
        trend = TREND_OPTIONS[self.trendSelectGroup.checkedId()]
        logger.debug(f"trend select: {trend}")
        if button == self.trendAutoSelect:
            self.trendThreshGroup.setEnabled(True)
        else:
            self.trendThreshGroup.setEnabled(False)
        self._data_request()
        # if self.data.online:
        #     self.data.online_restart()
        # else:
        #     self._data_request()

    def _set_trend_rawsec(self, *args):
        const.TREND_TRANS_THRESHOLD['raw/sec'] = int(self.trendRawSecThresh.text())

    def _set_trend_secmin(self, *args):
        const.TREND_TRANS_THRESHOLD['sec/min'] = int(self.trendSecMinThresh.text())

    ##########
    # AXIS

    @property
    def active_time_axis_mode(self):
        return self.plot0.axes['bottom']['item'].mode

    def _set_time_axis_mode(self, mode):
        """set time axis mode, base method"""
        if isinstance(mode, QtWidgets.QRadioButton):
            mode = mode.text()
        logger.debug(f"time axis mode: {mode}")
        for plot in self.plots:
            plot.axes['bottom']['item'].setTickStringsMode(mode)
        if mode == 'relative':
            self.referenceTimeLabel.show()
        else:
            self.referenceTimeLabel.hide()

    def set_time_axis_mode(self, mode):
        """set the mode of the time (X) axis

        relative, or absolute GPS/UTC/local

        """
        if mode == 'relative':
            self.timeAxisRelativeSelect.click()
        elif mode == 'absolute GPS':
            self.timeAxisGPSSelect.click()
        elif mode == 'absolute UTC':
            self.timeAxisUTCSelect.click()
        elif mode == 'absolute local':
            self.timeAxisLocalSelect.click()
        else:
            raise ValueError(f"Unknown time axis mode '{mode}'.")

    def _reset_time_axis_mode(self):
        mode = self.timeAxisModeButtonGroup.checkedButton().text()
        if self.active_time_axis_mode == mode:
            return
        self._set_time_axis_mode(mode)

    ##########
    # TRIGGER

    def set_trigger_channel(self, channel):
        """set the trigger channel"""
        assert channel in self.data.channels + [None]
        if channel == self.trigger.channel:
            return
        if self.trigger.channel is not None:
            tplot = self.plots4chan(self.trigger.channel)[0]
        else:
            tplot = None
        if channel is not None:
            nplot = self.plots4chan(channel)[0]
        else:
            nplot = None
        self.trigger.channel = channel
        if nplot != tplot:
            if tplot:
                tplot.removeItem(self.trigger.line)
            if nplot:
                nplot.addItem(self.trigger.line, ignoreBounds=True)
                nplot.disableAutoRange(axis='y')
            return True
        else:
            return False

    def _update_trigger_channel(self):
        """update trigger channel from menu select"""
        chan = str(self.triggerSelect.currentText())
        if self.set_trigger_channel(chan):
            self.reset_trigger_level()
        logger.info("trigger set: {}".format(chan))

    def _update_triggerSelect(self):
        """update the trigger channel select menu"""
        try:
            self.triggerSelect.currentIndexChanged.disconnect(self._update_trigger_channel)
        except TypeError:
            pass
        self.triggerSelect.clear()
        self.triggerSelect.addItems(self.data.channels)
        self.triggerSelect.currentIndexChanged.connect(self._update_trigger_channel)

    def set_trigger_level(self, level):
        """set trigger level"""
        self.trigger.set_level(level)

    def _update_triggerLevel(self):
        """update trigger level text entry on mouse level change"""
        self.triggerLevel.setText('{:g}'.format(self.trigger.level))

    def _set_trigger_level(self):
        """set the trigger level from text entry return press"""
        value = float(self.triggerLevel.text())
        self.set_trigger_level(value)

    def reset_trigger_level(self):
        """reset the trigger level to the midpoint of the range"""
        chan = self.trigger.channel
        if self.data['raw'] and chan in self.data['raw']:
            y = self.data['raw'][chan].data['raw']
            yn = y[np.where(np.invert(np.isnan(y)))[0]]
            value = np.mean(yn)
        else:
            value = 0
        self.set_trigger_level(value)

    def _enable_trigger(self):
        """enable trigger, base method"""
        chan = str(self.triggerSelect.currentText())
        self.set_trigger_channel(chan)
        if not self.triggerLevel.text():
            self.reset_trigger_level()
        span = self.get_span()
        self.set_window(-span/2, span/2)
        logger.info("trigger enabled")

    def enable_trigger(self):
        """enable trigger"""
        if self.triggerGroup.isChecked():
            return
        self._enable_trigger()
        self.triggerGroup.setChecked(True)

    def _disable_trigger(self):
        """disable trigger, base method"""
        self.set_trigger_channel(None)
        span = self.get_span()
        self.set_window(-span, 0)
        logger.info("trigger disabled")

    def disable_trigger(self):
        """disable trigger"""
        if not self.triggerGroup.isChecked():
            return
        self.triggerGroup.setChecked(False)
        self._disable_trigger()

    def _toggle_trigger(self):
        """toggle trigger on/off"""
        if not self.trigger:
            return
        if self.triggerGroup.isChecked():
            self._enable_trigger()
        else:
            self._disable_trigger()

    def _update_triggerTime(self, time):
        """update trigger time label (from trigger)"""
        self.triggerTime.setText('{:14.6f}'.format(time))

    ##########
    # CROSSHAIR

    def _connect_crosshair(self):
        """connect the crosshair update signal handler"""
        self._crosshair_proxy = pg.SignalProxy(
            self.graphView.scene().sigMouseMoved,
            rateLimit=20,
            slot=self._update_crosshair)

    def _enable_crosshair(self):
        """enable crosshair, base method"""
        for plot in self.plots:
            plot.disableAutoRange(axis='y')
        self._connect_crosshair()
        self.graphView.scene().sigMouseClicked.connect(self._clicked_crosshair)
        self.graphView.setCursor(Qt.CrossCursor)
        logger.info("crosshair enabled")

    def enable_crosshair(self):
        """enable crosshair"""
        if self.crosshairGroup.isChecked():
            return
        self._enable_crosshair()
        self.crosshairGroup.setChecked(True)

    def _disable_crosshair(self):
        """disable crosshair, base method"""
        self.crosshair.set_active_plot(None)
        self._crosshair_proxy = None
        try:
            self.graphView.scene().sigMouseClicked.disconnect(self._clicked_crosshair)
        except TypeError:
            pass
        self.graphView.setCursor(Qt.ArrowCursor)
        self.crosshairGPS.setText('')
        self.crosshairUTC.setText('')
        self.crosshairLocal.setText('')
        self.crosshairYValue.setText('')
        logger.info("crosshair disabled")

    def disable_crosshair(self):
        """disable crosshair"""
        if not self.crosshairGroup.isChecked():
            return
        self.crosshairGroup.setChecked(False)
        self._disable_crosshair()

    def _toggle_crosshair(self):
        """toggle crosshair on/off"""
        if self.crosshairGroup.isChecked():
            self._enable_crosshair()
        else:
            self._disable_crosshair()

    def _update_crosshair(self, event):
        """update crosshair on mouse move"""
        # using signal proxy unfortunately turns the original
        # arguments into a tuple pos = event
        pos = event[0]
        for plot in self.plots:
            if plot.sceneBoundingRect().contains(pos):
                break
        self.crosshair.update(pos, plot, self.t0)

    def _update_crosshair_entry(self, recv):
        t, utc, local, y = recv
        self.crosshairGPS.setText(str(t))
        self.crosshairUTC.setText(utc)
        self.crosshairLocal.setText(local)
        self.crosshairYValue.setText(str(y))

    def _clicked_crosshair(self, event):
        """drop crosshair on click, pickup on click"""
        if event.button() != 1:
            return
        if self._crosshair_proxy is None:
            self._connect_crosshair()
        else:
            self._crosshair_proxy = None

    ##########
    # CURSORS

    def enable_t_cursors(self):
        """enable the time cursors"""
        if self.plot0.t_cursors:
            return
        for plot in self.plots:
            plot.enable_t_cursors()
        # update the cursor locations from plot0, so they all get the
        # same value
        self.plot0.t_cursors.reset(self.plot0)
        logger.info("T cursors enabled")

    def disable_t_cursors(self):
        """disable the time cursors"""
        if not self.plot0.t_cursors:
            return
        for plot in self.plots:
            plot.disable_t_cursors()
        logger.info("T cursors disabled")

    def _update_t_cursors(self, enable):
        if enable:
            self.enable_t_cursors()
        else:
            self.disable_t_cursors()

    def _update_t_cursor(self, indval):
        index, value = indval
        for plot in self.plots:
            plot.t_cursors.set_values(**{index.lower(): value})

    def get_t_cursor_values(self):
        if self.plot0.t_cursors:
            return self.plot0.t_cursors.get_values()

    def set_t_cursor_values(self, t1=None, t2=None):
        self.plot0.t_cursors.set_values(t1, t2)

    ##########
    # STYLE

    def font_select_dialog(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.set_font(font)

    ##########
    # EXPORT

    def get_template(self):
        """Return the scope template as a dictionary

        """
        template = {
            # convert to float from numpy.float64
            't0': float(self.t0),
            'time-window': list(map(float, self.get_window())),
            'color-mode': self._color_mode,
            'window-title': self.windowTitle().replace('ndscope: ', ''),
            'font-size': self.font().pointSize(),
        }
        plots = []
        for plot, cells in self.plotLayout.items.items():
            plot_item = {}
            plot_item['channels'] = {}
            for name, chan in plot.channels.items():
                params = copy.deepcopy(chan.params)
                plot_item['channels'][name] = params
            tabspec = util.cells_to_tabspec(cells)
            plot_item.update(tabspec)
            if any(plot.vb.state['autoRange']):
                plot_item['yrange'] = 'auto'
            else:
                # convert to float from numpy.float64
                plot_item['yrange'] = list(map(float, plot.vb.viewRange()[1]))
            if plot.y_cursors:
                plot_item['y-cursors'] = plot.y_cursors.get_values()
            plots.append(plot_item)

        t_cursors = self.get_t_cursor_values()
        if t_cursors:
            template['t-cursors'] = t_cursors

        template['time-axis-mode'] = self.timeAxisModeButtonGroup.checkedButton().text()

        template['plots'] = plots
        return template

    def _export_dialog(self):
        """export save file dialog"""
        path = export.export_dialog(
            QFileDialog.getSaveFileName,
            self,
            self.exportPath.text(),
        )
        if not path:
            return
        self.exportPath.setText(path)
        return path

    def export(self, path=None):
        """Export plot scene, data, or template to file.

        Supports PNG, SVG, PDF image formats, HDF5 for data, and YAML
        for template.  A file select dialog will be presented if a
        path is not supplied.

        """
        if not path:
            path = self._export_dialog()
            if not path:
                return
        if not path or os.path.isdir(path):
            self.status_error(f"Must specify file path.")
            return
        ext = os.path.splitext(path)[1]
        if ext in [None, '']:
            self.status_error(f"Must specify export file extension.")
            return
        self.status_message(f"Writing file {path}...", timeout=10)
        self.exportPath.setText(path)
        QTimer.singleShot(1, self._export)
        # we do this timer thing so that the event loop will display
        # the above status message, in case it takes some time to
        # render/construct the output

    def _export(self):
        path = self.exportPath.text()
        ext = os.path.splitext(path)[1]

        if ext in export.IMAGE_EXPORT_FUNCTIONS:
            obj = 'scene'
            export_func = export.IMAGE_EXPORT_FUNCTIONS[ext]
            args = (
                self.graphView.scene(),
                path,
            )
            kwargs = dict()

        elif ext in export.DATA_EXPORT_FUNCTIONS:
            obj = 'data'
            export_func = export.DATA_EXPORT_FUNCTIONS[ext]
            trend = self.data.last_trend
            args = (
                self.data.db[trend],
                path,
                *self.get_range()
            )
            kwargs = dict(
                t0=self.t0,
                window=self.get_window(),
            )

        elif ext in export.TEMPLATE_EXPORT_FUNCTIONS:
            obj = 'template'
            export_func = export.TEMPLATE_EXPORT_FUNCTIONS[ext]
            args = (
                self.get_template(),
                path,
            )
            kwargs = dict()

        else:
            self.status_error(f"Unsupported export file extension: {ext}")
            return

        try:
            export_func(*args, **kwargs)
        except Exception as e:
            logger.info(traceback.format_exc())
            self.status_error(str(e))
            return

        ftype = ext[1:].upper()
        self.status_message(f"Exported {obj} to {ftype}: {path}", timeout=10)
        self._export_complete.emit()

    def _export_save_handler(self, path=None):
        path = self.exportPath.text()
        self.export(path)

    def _export_show_handler(self):
        path = self.exportPath.text()
        if not path or not os.path.exists(path):
            self.status_error("No path, or no file at path.  Export first.")
            return
        ext = os.path.splitext(path)[1]
        if ext in ['.hdf5', '.h5']:
            export.matplot_h5(path)
        else:
            try:
                subprocess.Popen(['xdg-open', path])
            except FileNotFoundError:
                self.status_error("xdg-open binary not found.  Please install 'xdg-utils' package.")
            # FIXME: catch open errors even though process backgrounded?
