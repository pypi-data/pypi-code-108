from galleries.galleries_management import GalleriesManagement
from PySide2 import QtWidgets, QtCore


class GalleriesCombobox(QtWidgets.QWidget):
    event_gallery_selection_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(GalleriesCombobox, self).__init__(parent=parent)

        self._combobox = QtWidgets.QComboBox()
        self._combobox.currentIndexChanged.connect(self._on_selection_changed)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._combobox)
        self.setLayout(layout)

        self._populate_galleries()

    def _populate_galleries(self):
        galleries = GalleriesManagement.load_galleries()
        for gallery_name, gallery in galleries:
            self._combobox.addItem(gallery_name, gallery)

    @QtCore.Slot()
    def _on_selection_changed(self, index: int):
        self.event_gallery_selection_changed.emit()

    def current_gallery_selected(self):
        gallery = self._combobox.currentData()
        gallery_name = self._combobox.currentText()
        return gallery_name, gallery
