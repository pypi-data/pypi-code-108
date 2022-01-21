from dlc_generic_analysis.trimmer import GoToTime, Trimmer
from qtpy import QtWidgets


def test_go_to_time(qtbot):
    gtt = GoToTime()
    w = QtWidgets.QWidget()
    w.setLayout(gtt)
    qtbot.addWidget(w)


def test_trimmer(qtbot):
    trimmer = Trimmer([""])
    qtbot.addWidget(trimmer)


#  testing trimmer is too expensive
