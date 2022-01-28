import os

from qtpy import QtCore, QtGui, QtWidgets

from kabaret.app.ui.gui.styles import Style


class SirenStyle(Style):
    """
    You can customize this style by modifying QSettings() (colors/*)
    """

    def __init__(self, name=None):
        super(SirenStyle, self).__init__(name or 'SirenStyle')

    def apply(self, widget=None):
        widget = widget or QtWidgets.QApplication.instance()

        app = QtWidgets.QApplication.instance()

        # --- Stuff we could not deal with only using css:

        self.set_property('alternate_child_color', False)

        # --- Change palette only for app wide apply:

        if widget is app:
            widget = widget or QtWidgets.QApplication.instance()

            settings = QtCore.QSettings()
            settings.beginGroup('colors')

            # setup the palette
            palette = QtWidgets.QApplication.palette()
            # A color to indicate a selected item or the current item. By default, the highlight color is Qt.darkBlue.
            palette.setColor(QtGui.QPalette.Highlight, settings.value('highlight', QtGui.QColor("#ad4e5c")))
            palette.setColor(QtGui.QPalette.HighlightedText, settings.value('highlighted_text', QtGui.QColor("#42314a")))
            palette.setColor(QtGui.QPalette.WindowText, settings.value('window_text', QtGui.QColor("#b9c2c8")))
            palette.setColor(QtGui.QPalette.Window, settings.value('window', QtGui.QColor("#3e4041"))) 
            palette.setColor(QtGui.QPalette.Text, settings.value('text', QtGui.QColor("#a7b0b4"))) 
            palette.setColor(QtGui.QPalette.Base, settings.value('base', QtGui.QColor("#2b2b2b")))
            palette.setColor(QtGui.QPalette.Dark, settings.value('dark', QtGui.QColor("#22222b")))
            palette.setColor(QtGui.QPalette.Light, settings.value('light', QtGui.QColor("#ffe6ee")))
            palette.setColor(QtGui.QPalette.Midlight, settings.value('midlight', QtGui.QColor("#911f36")))
            palette.setColor(QtGui.QPalette.Mid, settings.value('mid', QtGui.QColor("#4b1b1f")))
            palette.setColor(QtGui.QPalette.Button, settings.value('button', QtGui.QColor("#4c5052")))
            palette.setColor(QtGui.QPalette.ButtonText, settings.value('button_text', QtGui.QColor("#a9b7c6")))

            settings.endGroup()

            widget.setPalette(palette)

        # --- Load and apply the css
        this_folder = os.path.dirname(__file__)
        css_file = os.path.join(this_folder, 'siren_style.css')
        with open(css_file, 'r') as r:
            self.apply_css(widget, r.read())

