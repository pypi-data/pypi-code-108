import os
from pathlib import Path

from PySide2 import QtWidgets, QtGui, QtCore

from galleries.gallery import Gallery
from galleries.annotations_parsers.file_name_parser import GalleryAnnotationsParser
from galleries.images_providers.gallery_images_provider import GalleryImagesProvider

from galleries.images_providers import *
from galleries.annotations_parsers import *

from pyrulo_qt.ui_configurable_selector import ConfigurableSelector

from mnd_qtutils.qtutils import setup_widget_from_ui


class GalleryWizard(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GalleryWizard, self).__init__(parent=parent)

        self._dirty = False

        ui_file_path = os.path.join(Path(__file__).parent, 'gallery_wizard.ui')
        self._widget: QtWidgets.QWidget = setup_widget_from_ui(ui_file_path, self)

        self._name_edit: QtWidgets.QLineEdit = self._widget.name_edit
        self._name_edit.setValidator(QtGui.QRegExpValidator('[A-Za-z0-9_áéíóúÁÉÍÓÚ]*'))
        self._name_edit.textEdited.connect(self._set_dirty)

        self._image_provider_container: QtWidgets.QWidget = self._widget.provider_container
        self._provider_selector = ConfigurableSelector(base_class=GalleryImagesProvider)
        self._provider_selector.eventObjectSelected.connect(self._on_provider_changed)
        self._image_provider_container.layout().addWidget(self._provider_selector)

        self._parser_container: QtWidgets.QWidget = self._widget.parser_container
        self._parser_selector = ConfigurableSelector(base_class=GalleryAnnotationsParser)
        self._parser_selector.eventObjectSelected.connect(self._on_parser_changed)
        self._parser_container.layout().addWidget(self._parser_selector)

    def is_dirty(self):
        dirty = self._dirty
        return dirty

    def set_gallery(self, gallery_name: str, gallery: Gallery):
        self._name_edit.setText(gallery_name)
        self._set_provider_ui_by_image_provider(gallery.images_provider)
        self._set_parser_ui_by_parser(gallery.annotations_parser)
        self._dirty = False

    def get_gallery(self) -> Gallery:
        images_provider = self._provider_selector.current_object()
        parser = self._parser_selector.current_object()
        gallery_name = self._name_edit.text()
        gallery = Gallery(gallery_name, images_provider, parser)
        return gallery

    def get_name(self) -> str:
        return self._name_edit.text()

    def clear(self):
        self._provider_selector.set_current_index(0)
        self._parser_selector.set_current_index(0)
        self._dirty = False

    def _set_provider_ui_by_image_provider(self, image_provider):
        provider_class = type(image_provider)
        self._provider_selector.add_class(provider_class)
        self._provider_selector.set_object_for_class(provider_class, image_provider)
        self._provider_selector.select_class(provider_class)

    def _set_parser_ui_by_parser(self, parser):
        parser_class = type(parser)
        self._parser_selector.add_class(parser_class)
        self._parser_selector.set_object_for_class(parser_class, parser)
        self._parser_selector.select_class(parser_class)

    @QtCore.Slot()
    def _on_provider_changed(self, index):
        self._set_dirty()

    @QtCore.Slot()
    def _on_parser_changed(self, index):
        self._set_dirty()

    def _set_dirty(self):
        self._dirty = True


if __name__ == '__main__':
    import sys
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QWidget, QVBoxLayout

    app = QApplication(sys.argv)

    window = QWidget()
    window.setMinimumSize(100, 100)
    layout = QVBoxLayout()
    window.setLayout(layout)

    panel = GalleryWizard()
    layout.addWidget(panel)

    window.show()

    sys.exit(app.exec_())
