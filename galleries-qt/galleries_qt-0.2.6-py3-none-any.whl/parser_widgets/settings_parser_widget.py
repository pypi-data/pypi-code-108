from PySide2 import QtWidgets
from galleries.annotations_parsers.gallery_annots_parsers import GalleryAnnotationsParser
from propsettings_qt.ui_settings_area import SettingsAreaWidget

from galleries_qt.gallery_annotations_parser_view import GalleryAnnotationsParserView


class SettingsParserWidget(GalleryAnnotationsParserView):

    def __init__(self, parent=None):
        super(SettingsParserWidget, self).__init__(parent=parent)
        self._settings_area = SettingsAreaWidget()

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._settings_area)

        self._parser = None

    def get_parser(self) -> GalleryAnnotationsParser:
        return self._parser

    def populate_with_parser(self, parser: GalleryAnnotationsParser):
        self._parser = parser
        self._settings_area.populate_object(self._parser)

    def clear(self):
        pass

    def is_dirty(self) -> bool:
        return False
