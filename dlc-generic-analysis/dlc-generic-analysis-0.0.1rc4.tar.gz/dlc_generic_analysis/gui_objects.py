from qtpy import QtWidgets
import qtawesome as qta


class PlayPause(QtWidgets.QHBoxLayout):
    def __init__(self):
        """
        Creates fast reverse play/pause and fast forward buttons wrapped in a QHBoxLayout
        """
        QtWidgets.QHBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.fast_reverse_button = QtWidgets.QPushButton()
        fr_icon = qta.icon("fa5s.fast-backward")
        self.fast_reverse_button.setIcon(fr_icon)
        self.addWidget(self.fast_reverse_button)
        self.play_icon = qta.icon("fa5s.play")
        self.pause_icon = qta.icon("fa5s.pause")
        self.play_pause_button = QtWidgets.QPushButton()
        self.play_pause_button.setIcon(self.play_icon)
        self.addWidget(self.play_pause_button)
        ff_icon = qta.icon("fa5s.fast-forward")
        self.fast_forward_button = QtWidgets.QPushButton()
        self.fast_forward_button.setIcon(ff_icon)
        self.addWidget(self.fast_forward_button)
