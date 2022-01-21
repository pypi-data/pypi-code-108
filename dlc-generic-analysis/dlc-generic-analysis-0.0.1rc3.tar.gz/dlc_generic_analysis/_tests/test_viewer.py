from dlc_generic_analysis.viewer import ViewerWidget


class VW(ViewerWidget):
    def __init__(self):
        super(VW, self).__init__()

    def position_changed(self, position):
        super(VW, self).position_changed(position)

    def load_video(self, path: str) -> None:
        super(VW, self).load_video(path)


def test_viewer(qtbot):
    window = VW()
    window.load_video("")
    window.setBaseSize(window.sizeHint().width(), window.sizeHint().height())
    qtbot.addWidget(window)
    window.show()
    window.on_play_pause()
    window.on_fast_forward()
    window.on_fast_reverse()
    window.on_play_pause()
