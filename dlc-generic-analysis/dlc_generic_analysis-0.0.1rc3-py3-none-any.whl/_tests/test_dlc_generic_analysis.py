from dlc_generic_analysis import MainWidget


class TestMainWidget(MainWidget):
    def __init__(self, title: str):
        super(TestMainWidget, self).__init__(title=title)

    def on_click_analyze(self):
        pass

    def on_click_view(self):
        pass

    def on_click_trim(self):
        super(TestMainWidget, self).on_click_trim()


def test_main_widget(qtbot):
    tmw = TestMainWidget("test")
    qtbot.addWidget(tmw)
    tmw.on_click_analyze()
    tmw.on_click_view()


def test_trimmer(qtbot):
    tmw = TestMainWidget("test")
    qtbot.addWidget(tmw)
