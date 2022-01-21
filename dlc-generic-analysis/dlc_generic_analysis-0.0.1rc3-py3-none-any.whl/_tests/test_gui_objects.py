from dlc_generic_analysis.gui_objects import PlayPause
from qtpy import QtWidgets


def test_play_pause(qtbot):
    p_p = PlayPause()
    w = QtWidgets.QWidget()
    w.setLayout(p_p)
    qtbot.addWidget(w)
