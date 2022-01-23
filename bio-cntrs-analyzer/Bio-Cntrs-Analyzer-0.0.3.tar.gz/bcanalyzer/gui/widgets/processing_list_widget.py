
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QPoint, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QWidget, QAction
from PyQt5.QtWidgets import QVBoxLayout, QMenu
from PyQt5.QtWidgets import QListView


class ProcessinListWidget(QWidget):
    delete_item = pyqtSignal(QModelIndex, QItemSelectionModel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_index = None
        self.initUI()

    def initUI(self):
        self._root_layout = QVBoxLayout()

        self.processing_list = QListView(self)
        self.processing_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.processing_list.setSelectionMode(
            self.processing_list.ExtendedSelection)

        self._root_layout.addWidget(self.processing_list)

        self.contextMenu = QMenu()
        self.delete_action = QAction("Delete", self.processing_list)
        self.delete_action.triggered.connect(self.deleteClickedSlot)
        self.contextMenu.addAction(self.delete_action)
        self.processing_list.customContextMenuRequested.connect(
            self.onCustomContextMenu)

        self.setLayout(self._root_layout)

    def set_processing_list_model(self, processing_list_model):
        self.processing_list.setModel(processing_list_model)

    @pyqtSlot(QPoint)
    def onCustomContextMenu(self, point):
        self._current_index = self.processing_list.indexAt(point)
        if self._current_index.isValid():
            self.contextMenu.exec(
                self.processing_list.viewport().mapToGlobal(point))

    @pyqtSlot()
    def deleteClickedSlot(self):
        if self._current_index:
            self.delete_item.emit(self._current_index,
                                  self.processing_list.selectionModel())
            self._current_index = None
