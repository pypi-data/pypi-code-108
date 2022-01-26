import weakref
import logging

from qtpy import QtCore, QtGui, QtWidgets

from ._qt import load_ui
from .const import CHANNEL_REGEXP, CHANNEL_RE


AxisCtrlTemplate, __ = load_ui('axisCtrlTemplate.ui')

class AxisCtrlMenu(QtWidgets.QMenu, AxisCtrlTemplate):
    def __init__(self, title, mainmenu):
        super().__init__(title, mainmenu)
        self.setupUi(self)
        self.manualRadio.clicked.connect(mainmenu.yManualClicked)
        self.minText.setValidator(QtGui.QDoubleValidator())
        self.minText.editingFinished.connect(mainmenu.yRangeTextChanged)
        self.maxText.setValidator(QtGui.QDoubleValidator())
        self.maxText.editingFinished.connect(mainmenu.yRangeTextChanged)
        self.autoRadio.clicked.connect(mainmenu.yAutoClicked)
        self.autoPercentSpin.valueChanged.connect(mainmenu.yAutoSpinChanged)
        # self.mouseCheck.toggled.connect(mainmenu.yMouseToggled)
        # self.visibleOnlyCheck.toggled.connect(mainmenu.yVisibleOnlyToggled)
        # self.autoPanCheck.toggled.connect(mainmenu.yAutoPanToggled)


# this is lifted from the pqtgraph.ViewBoxMenu module
class NDScopePlotMenu(QtWidgets.QMenu):
    def __init__(self, plot):
        QtWidgets.QMenu.__init__(self)
        # keep weakref to view to avoid circular reference (don't know
        # why, but this prevents the ViewBox from being collected)
        self.plot = weakref.ref(plot)
        self.view = weakref.ref(plot.getViewBox())
        self.viewMap = weakref.WeakValueDictionary()

        loc = self.plot().loc
        title = f"plot {loc}"
        self.setTitle(title)
        self.addLabel(title)
        self.addSeparator()

        # view all data
        self.viewAll = QtWidgets.QAction("view all data", self)
        self.viewAll.triggered.connect(self.autoRange)
        self.addAction(self.viewAll)

        self.resetT0 = QtWidgets.QAction("reset t0 to point", self)
        self.resetT0.triggered.connect(self.reset_t0)
        self.addAction(self.resetT0)

        self.yAxisUI = AxisCtrlMenu("Y axis scale", self)
        self.addMenu(self.yAxisUI)

        self.mouseMenu = QtWidgets.QMenu("mouse mode")
        group = QtWidgets.QActionGroup(self)
        # This does not work! QAction _must_ be initialized with a permanent
        # object as the parent or else it may be collected prematurely.
        #pan = self.leftMenu.addAction("3 button", self.set3ButtonMode)
        #zoom = self.leftMenu.addAction("1 button", self.set1ButtonMode)
        pan = QtWidgets.QAction("pan/zoom", self.mouseMenu)
        rect = QtWidgets.QAction("zoom box", self.mouseMenu)
        self.mouseMenu.addAction(pan)
        self.mouseMenu.addAction(rect)
        pan.triggered.connect(self.setMouseModePan)
        rect.triggered.connect(self.setMouseModeRect)
        pan.setCheckable(True)
        rect.setCheckable(True)
        pan.setActionGroup(group)
        rect.setActionGroup(group)
        self.mouseModes = [pan, rect]
        self.addMenu(self.mouseMenu)

        self.YCursorSelect = QtWidgets.QAction("Y cursors", self, checkable=True)
        self.YCursorSelect.triggered.connect(self.toggle_y_cursors)
        self.addAction(self.YCursorSelect)
        self.TCursorSelect = QtWidgets.QAction("T cursors", self, checkable=True)
        self.TCursorSelect.triggered.connect(self.toggle_t_cursors)
        self.addAction(self.TCursorSelect)

        self.addLabel()

        # channel select dialog
        self.openChannelSelectDialogButton = self.addButton("set channel list/parameters")
        self.openChannelSelectDialogButton.clicked.connect(self.channel_select_dialog)

        # add channel
        self.addChannelEntry = QtWidgets.QLineEdit()
        self.addChannelEntry.setMinimumSize(300, 24)
        self.addChannelEntry.setPlaceholderText("enter channel to add")
        self.addChannelEntry.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(CHANNEL_REGEXP)))
        self.addChannelEntry.textChanged.connect(self.validate_add)
        self.addChannelEntry.returnPressed.connect(self.add_channel)
        self.addChannelEntry.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        acea = QtWidgets.QWidgetAction(self)
        acea.setDefaultWidget(self.addChannelEntry)
        self.addAction(acea)

        self.addChannelButton = self.addButton("add channel to plot")
        self.addChannelButton.setEnabled(False)
        self.addChannelButton.clicked.connect(self.add_channel)

        self.addLabel()

        # remove channel
        self.removeChannelList = QtWidgets.QComboBox()
        self.removeChannelList.setMinimumSize(200, 26)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)
        # self.removeChannelList.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        rcl = QtWidgets.QWidgetAction(self)
        rcl.setDefaultWidget(self.removeChannelList)
        self.addAction(rcl)

        self.addLabel()
        self.addSeparator()
        self.addLabel("add/remove plots")
        self.addLabel()

        self.newPlotRowButton = self.addButton("add plot to row")
        self.newPlotRowButton.clicked.connect(self.new_plot_row)

        self.newPlotColButton = self.addButton("add plot to column")
        self.newPlotColButton.clicked.connect(self.new_plot_col)

        self.addLabel()

        self.removePlotButton = self.addButton("remove plot")
        self.removePlotButton.clicked.connect(self.remove_plot)

        self.setContentsMargins(10, 10, 10, 10)

        self.view().sigStateChanged.connect(self.viewStateChanged)
        self.updateState()

    ##########

    def addLabel(self, label=''):
        ql = QtWidgets.QLabel()
        ql.setText(label)
        ql.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        qla = QtWidgets.QWidgetAction(self)
        qla.setDefaultWidget(ql)
        self.addAction(qla)

    def addButton(self, label):
        button = QtWidgets.QPushButton(label)
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(button)
        self.addAction(action)
        return button

    ##########

    def viewStateChanged(self):
        if self.yAxisUI.minText.isVisible():
            self.updateState()

    def updateState(self):
        # Something about the viewbox has changed; update the menu GUI

        state = self.view().getState(copy=False)
        if state['mouseMode'] == self.view().PanMode:
            self.mouseModes[0].setChecked(True)
        else:
            self.mouseModes[1].setChecked(True)

        i = 1
        tr = state['targetRange'][i]
        self.yAxisUI.minText.setText("%0.5g" % tr[0])
        self.yAxisUI.maxText.setText("%0.5g" % tr[1])
        if state['autoRange'][i] is not False:
            self.yAxisUI.autoRadio.setChecked(True)
            if state['autoRange'][i] is not True:
                self.yAxisUI.autoPercentSpin.setValue(int(state['autoRange'][i]*100))
        else:
            self.yAxisUI.manualRadio.setChecked(True)
        # self.yAxisUI.invertCheck.setChecked(state.get('yInverted', False))
        # self.yAxisUI.mouseCheck.setChecked(state['mouseEnabled'][i])
        # self.yAxisUI.visibleOnlyCheck.setChecked(state['autoVisibleOnly'][i])
        # self.yAxisUI.autoPanCheck.setChecked(state['autoPan'][i])

    def popup(self, pos):
        self.updateState()

        ppos = self.plot().vb.mapSceneToView(pos)
        self.pos = (ppos.x(), ppos.y())

        if hasattr(self.plot(), 'y_cursors'):
            enabled = self.plot().y_cursors is not None
            self.YCursorSelect.setChecked(enabled)

        if hasattr(self.plot(), 't_cursors'):
            enabled = self.plot().t_cursors is not None
            self.TCursorSelect.setChecked(enabled)

        # update remove channels list
        self.update_channel_list()

        # see if there's a channel in the clipboard
        clipboard = QtWidgets.QApplication.clipboard().text(
            mode=QtGui.QClipboard.Selection)
        clipboard = clipboard.strip()
        if CHANNEL_RE.match(clipboard):
            # if we have a channel add it to the label
            self.addChannelEntry.setText(clipboard)
        else:
            self.addChannelEntry.setText('')

        # FIXME: only remove plot if it's not the last
        # if numplots > 1:
        #     self.removePlotButton.setEnabled(True)

        # cparams = {chan:c.params for chan, c in self.plot().channels.items()}
        # self.ptree.setParameters(
        #     parameters.create_channels_params(cparams),
        #     showTop=False,
        # )

        self.removeChannelList.setEnabled(len(self.plot().channels) > 0)

        QtWidgets.QMenu.popup(self, pos)

    ##########

    def autoRange(self):
        # don't let signal call this directly--it'll add an unwanted argument
        self.view().autoRange()

    def reset_t0(self):
        self.plot()._reset_t0(self.pos[0])

    def toggle_t_cursors(self):
        self.plot()._update_t_cursors(
            self.TCursorSelect.isChecked())

    def toggle_y_cursors(self):
        if self.YCursorSelect.isChecked():
            self.plot().enable_y_cursors()
        else:
            self.plot().disable_y_cursors()

    ##########

    def update_channel_list(self):
        channels = list(self.plot().channels.keys())
        self.removeChannelList.clear()
        ls = ['remove channel'] + channels
        self.removeChannelList.addItems(ls)
        self.removeChannelList.insertSeparator(1)

    def validate_add(self):
        channel = str(self.addChannelEntry.text())
        if CHANNEL_RE.match(channel):
            if channel in self.plot().channels:
                self.addChannelEntry.setStyleSheet("background: #87b5ff;")
                self.addChannelButton.setEnabled(False)
            else:
                self.addChannelEntry.setStyleSheet("font-weight: bold; background: #90ff8c;")
                self.addChannelButton.setEnabled(True)
        else:
            self.addChannelEntry.setStyleSheet('')
            self.addChannelButton.setEnabled(False)

    def channel_select_dialog(self):
        self.plot()._select_channel_menu()
        self.close()

    def add_channel(self):
        channel = str(self.addChannelEntry.text())
        if CHANNEL_RE.match(channel):
            self.plot()._add_channel_menu(channel)
        self.close()

    def remove_channel(self, *args):
        self.removeChannelList.currentIndexChanged.disconnect(self.remove_channel)
        channel = str(self.removeChannelList.currentText())
        self.plot().remove_channel(channel)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)
        self.close()

    def new_plot_row(self):
        self.new_plot('row')

    def new_plot_col(self):
        self.new_plot('col')

    def new_plot(self, rowcol):
        channel = str(self.addChannelEntry.text())
        kwargs = {}
        if CHANNEL_RE.match(channel):
            kwargs['channels'] = [{channel: None}]
        self.plot().new_plot_request.emit(
            (self.plot(), rowcol, kwargs),
        )
        self.close()

    def remove_plot(self):
        self.plot().remove_plot_request.emit(self.plot())
        self.close()

    ##########

    def setMouseModePan(self):
        self.view().setLeftButtonAction('pan')

    def setMouseModeRect(self):
        self.view().setLeftButtonAction('rect')

    def yMouseToggled(self, b):
        self.view().setMouseEnabled(y=b)

    def yManualClicked(self):
        self.view().enableAutoRange(self.view().YAxis, False)

    def yRangeTextChanged(self):
        self.yAxisUI.manualRadio.setChecked(True)
        try:
            self.view().setYRange(float(self.yAxisUI.minText.text()), float(self.yAxisUI.maxText.text()), padding=0)
        except ValueError as e:
            logging.error(f"Y range: {e}")

    def yAutoClicked(self):
        val = self.yAxisUI.autoPercentSpin.value() * 0.01
        self.view().enableAutoRange(self.view().YAxis, val)

    def yAutoSpinChanged(self, val):
        self.yAxisUI.autoRadio.setChecked(True)
        self.view().enableAutoRange(self.view().YAxis, val*0.01)

    def yAutoPanToggled(self, b):
        self.view().setAutoPan(y=b)

    def yVisibleOnlyToggled(self, b):
        self.view().setAutoVisible(y=b)

    def yInvertToggled(self, b):
        self.view().invertY(b)
