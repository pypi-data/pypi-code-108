import cv2 as cv
import numpy as np
import os
from pathlib import Path
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import QSize

from galleries.galleries_management import GalleriesManagement
from galleries.gallery import Gallery
from galleries.annotations_parsers.file_name_parser import FileNameSepParser
from galleries.igallery import IGallery
from galleries.images_providers.local_files_image_providers import LocalFilesImageProvider
from mnd_qtutils.qtutils import setup_widget_from_ui, icon_from_image
import mnd_utils.image
from galleries_qt.gallery_wizard import GalleryWizard


class GalleriesManager(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GalleriesManager, self).__init__(parent=parent)

        ui_file_path = os.path.join(Path(__file__).parent, 'galleries_manager.ui')
        self._widget: QtWidgets.QWidget = setup_widget_from_ui(ui_file_path, self)

        self._gallery_dir_edit: QtWidgets.QLineEdit = self._widget.gal_dir_edit
        self._gallery_dir_edit.setText(GalleriesManagement.get_galleries_folder())

        self._gallery_dir_button: QtWidgets.QPushButton = self._widget.gal_dir_button
        self._gallery_dir_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))
        self._gallery_dir_button.clicked.connect(self._change_galleries_folder)

        self._galleries_list: QtWidgets.QListWidget = self._widget.galleries_list
        self._galleries_list.itemSelectionChanged.connect(self._on_gallery_selection_changed)

        self._gallery_wizard: GalleryWizard = GalleryWizard()
        self._gallery_wizard.setEnabled(False)
        self._gallery_wizard.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self._gallery_wizard.setMinimumHeight(self._gallery_wizard.minimumSizeHint().height())
        self._wizard_container: QtWidgets.QWidget = self._widget.wizard_container
        self._wizard_container.layout().addWidget(self._gallery_wizard)

        self._new_button: QtWidgets.QPushButton = self._widget.new_button
        self._new_button.clicked.connect(self._add_empty_gallery)

        self._save_button: QtWidgets.QPushButton = self._widget.save_button
        self._save_button.clicked.connect(self._save_gallery)
        self._save_button.setEnabled(False)

        self._remove_button: QtWidgets.QPushButton = self._widget.remove_button
        self._remove_button.clicked.connect(self._remove_gallery)
        self._remove_button.setEnabled(False)

        self._update_galleries_list()

    @QtCore.Slot()
    def _change_galleries_folder(self):
        workdir = os.getcwd()
        galleries_folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.tr("Seleccionar ubicación de las galerías"),
            workdir,
        )

        if os.path.exists(galleries_folder):
            GalleriesManagement.set_galleries_folder(galleries_folder)
            self._gallery_dir_edit.setText(galleries_folder)
            self._update_galleries_list()

    @QtCore.Slot()
    def _on_gallery_selection_changed(self):
        any_gallery_selected = self._is_any_gallery_selected()
        if any_gallery_selected:
            gallery_item: GalleryListWidgetItem = self._get_selected_gallery()
            gallery_name = gallery_item.gallery_name
            gallery = gallery_item.gallery
            self._gallery_wizard.set_gallery(gallery_name, gallery)
        else:
            self._gallery_wizard.clear()

        self._gallery_wizard.setEnabled(any_gallery_selected)
        self._save_button.setEnabled(any_gallery_selected)
        self._remove_button.setEnabled(any_gallery_selected)

    def _is_any_gallery_selected(self):
        selected_items = self._galleries_list.selectedItems()
        return len(selected_items) > 0

    def _get_selected_gallery(self):
        selected_items = self._galleries_list.selectedItems()
        return selected_items[0]

    def _update_galleries_list(self):
        self._clear_galleries_list()
        galleries = GalleriesManagement.load_galleries()
        for gallery_name, gallery in galleries:
            self._add_gallery_to_list(gallery_name, gallery)

    def _add_gallery_to_list(self, gallery_name: str, gallery: IGallery):
        icon_size = self._galleries_list.iconSize()
        gallery_list_item = GalleryListWidgetItem(gallery_name, gallery, icon_size)
        self._galleries_list.addItem(gallery_list_item)

    @QtCore.Slot()
    def _add_empty_gallery(self):
        images_provider = LocalFilesImageProvider('')
        parser = FileNameSepParser([], '')
        gallery = Gallery("", images_provider, parser)
        self._add_gallery_to_list('', gallery)

    @QtCore.Slot()
    def _save_gallery(self):
        any_gallery_selected = self._is_any_gallery_selected()
        if any_gallery_selected:
            gallery_item: GalleryListWidgetItem = self._get_selected_gallery()
            gallery_name = self._gallery_wizard.get_name()
            gallery = self._gallery_wizard.get_gallery()
            gallery_item.gallery_name = gallery_name
            gallery_item.gallery = gallery
            GalleriesManagement.save_gallery(gallery_name, gallery)

    @QtCore.Slot()
    def _remove_gallery(self):
        any_gallery_selected = self._is_any_gallery_selected()
        if any_gallery_selected:
            gallery_item: GalleryListWidgetItem = self._get_selected_gallery()
            gallery_name = gallery_item.gallery_name
            GalleriesManagement.remove_gallery_by_name(gallery_name)
            self._galleries_list.takeItem(self._galleries_list.row(gallery_item))

    def _clear_galleries_list(self):
        self._galleries_list.clear()


class GalleryListWidgetItem(QtWidgets.QListWidgetItem):

    def __init__(self, gallery_name: str, gallery: IGallery, icon_size: QSize):
        icon = self._get_first_image_icon(gallery, icon_size)
        super().__init__(icon, gallery_name)
        self._gallery_name = gallery_name
        self._gallery = gallery

    @property
    def gallery_name(self):
        return self._gallery_name

    @gallery_name.setter
    def gallery_name(self, value: str):
        self._gallery_name = value
        self.setText(value)

    @property
    def gallery(self):
        return self._gallery

    @gallery.setter
    def gallery(self, value):
        self._gallery = value
        icon = self._get_first_image_icon(value, self.sizeHint())
        self.setIcon(icon)

    def _get_first_image_icon(self, gallery: IGallery, icon_size: QSize) -> QtGui.QIcon:
        indices = gallery.get_indices()
        try:
            first_image_index = next(indices)
            image = cv.imread(first_image_index)
        except:
            image = np.ones((64, 64, 3)).astype(np.uint8) * 127
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image = mnd_utils.image.fit_in_size(image, (icon_size.width(), icon_size.height()))
        icon = icon_from_image(image)
        return icon


if __name__ == '__main__':
    import sys
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QWidget, QVBoxLayout

    app = QApplication(sys.argv)

    window = QWidget()
    window.setMinimumSize(100, 100)
    layout = QVBoxLayout()
    window.setLayout(layout)

    panel = GalleriesManager()
    layout.addWidget(panel)

    window.show()

    sys.exit(app.exec_())
